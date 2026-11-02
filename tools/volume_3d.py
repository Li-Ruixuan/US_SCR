"""
Interactive 3D view of a compounded US sweep: one self-contained HTML page (open it in a
browser; three.js from a CDN), rotatable, with
  * the volume compounded with the true poses (Polaris) and with each estimate given
    (odometry, odometry + anchors, zero motion), all on ONE common grid, so badly placed
    pixels stay visible (poses.py builds its volume on the GT grid and drops them);
  * render modes: maximum-intensity projection of one volume, overlay of two (first in
    green, second in magenta: white where they agree), and a translucent rendering;
  * the path of the US image centre for each pose source, and image outlines every 2 s.

Input: poses.py JSON exports of ONE sweep (they all carry the GT poses; the first one's
GT is used). Reads the US images from the data folder named in the JSON (or --root).

  python tools/volume_3d.py \\
    --json runs/rpr-rgb-gap8-12XX-gru8/test_3XX/poses/fold0_run-316_model.json \\
           "runs/rpr-rgb-gap8-12XX-gru8/test_3XX_ownmap/poses/fold0_run-316_anchored-pgo-anchor-rgbd-e20-odometry-train_3XX-map-room-301+room-302.json" \\
    --out runs/volume3d/run-316.html
"""

import argparse
import base64
import gzip
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "baselines"))
from poses import accumulate, fan_mask, load_us, pixel_points  # noqa: E402


def label_of(source):
    if source == "model":
        return "odometry"
    if source == "zero":
        return "zero motion"
    if source.startswith("classical-vo"):
        return "classical odometry"
    if source.startswith("anchored-pgo-scr-") or source.startswith("anchored-pgo-classical-"):
        anchors = "SCR anchors" if source.startswith("anchored-pgo-scr-") else "classical anchors"
        odo = "classical odometry" if "odo-classical-vo" in source else "RPRNet"
        return f"{anchors} + {odo}" + (", start from anchors" if "startanchor" in source else "")
    if source.startswith("anchored-pgo"):
        return "odometry + anchors"
    if source.startswith("anchored"):
        return "odometry + anchors (" + source.split("-")[1] + ")"
    return source


def pack(arr):
    return base64.b64encode(gzip.compress(arr.tobytes(), 6)).decode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", nargs="+", required=True, help="poses.py exports of one sweep")
    ap.add_argument("--out", required=True, help="output .html")
    ap.add_argument("--root", default=None, help="data folder if the JSON's root is not valid here")
    ap.add_argument("--labels", nargs="+", default=None, help="one label per --json (default: from the source name)")
    ap.add_argument("--voxel", type=float, default=1.0, help="mm (raised automatically above --max-voxels)")
    ap.add_argument("--max-voxels", type=float, default=6e6)
    ap.add_argument("--stride", type=int, default=2, help="US pixel stride")
    ap.add_argument("--margin", type=float, default=5.0, help="mm around all volumes")
    ap.add_argument("--fan-threshold", type=float, default=5.0)
    args = ap.parse_args()

    docs = [json.load(open(p)) for p in args.json]
    run = docs[0]["run"]
    if any(d["run"] != run for d in docs):
        raise SystemExit("all --json files must be the same sweep")
    root = Path(args.root) / run if args.root else Path(docs[0]["root"]) / run
    d0 = docs[0]
    roi, S = d0["us_roi"], np.asarray(d0["S_us_px_to_mm"])
    frames = [f for f in d0["frames"] if f["us"]]
    rows = {f["row"] for f in frames}

    sources = [("gt", "true poses (Polaris)", np.array([f["T_world_us_gt"] for f in frames]))]
    if args.labels and len(args.labels) != len(docs):
        raise SystemExit("--labels needs one label per --json")
    for k, d in enumerate(docs):
        fr = {f["row"]: f for f in d["frames"] if f["us"]}
        if set(fr) != rows:
            raise SystemExit(f"{d['source']}: frames differ from the first JSON")
        sources.append((d["source"], args.labels[k] if args.labels else label_of(d["source"]),
                        np.array([fr[f["row"]]["T_world_us_pred"] for f in frames])))

    mask = fan_mask(frames, root, roi, args.fan_threshold)
    r, c, P = pixel_points(mask, args.stride, S)
    _, _, P_err = pixel_points(mask, 16, S)
    corners = S @ np.array([[1, 1, 0, 1], [640, 1, 0, 1], [640, 480, 0, 1], [1, 480, 0, 1]], float).T
    centre = S @ np.array([320.0, 240.0, 0.0, 1.0])

    allc = np.concatenate([(T @ corners)[:, :3].transpose(0, 2, 1).reshape(-1, 3) for _, _, T in sources])
    lo, hi = allc.min(0) - args.margin, allc.max(0) + args.margin
    voxel = args.voxel
    while np.prod(np.ceil((hi - lo) / voxel)) > args.max_voxels:
        voxel *= 1.25
    shape = tuple(int(x) for x in np.ceil((hi - lo) / voxel))
    print(f"{run}: {len(frames)} frames, grid {shape} at {voxel:.2f} mm, {len(sources)} volumes")

    imgs = [load_us(root / f["us"], roi)[r, c].astype(np.float32) for f in frames]
    vols, info = [], []
    T_gt = sources[0][2]
    scale = None
    for key, label, T in sources:
        s = np.zeros(shape, np.float32)
        n = np.zeros(shape, np.float32)
        for i in range(len(frames)):
            accumulate(s, n, lo, voxel, (T[i] @ P)[:3].T, imgs[i])
        v = np.where(n > 0, s / np.maximum(n, 1), 0)
        if scale is None:                              # common intensity scale from the GT volume
            scale = float(np.percentile(v[n > 0], 99.5)) or 1.0
        u8 = np.where(n > 0, np.clip(1 + 254 * v / scale, 1, 255), 0).astype(np.uint8)
        vols.append(pack(np.ascontiguousarray(u8.transpose(2, 1, 0))))   # x fastest, for WebGL
        err = float(np.linalg.norm((T @ P_err - T_gt @ P_err)[:, :3], axis=1).mean()) if key != "gt" else 0.0
        path = (T @ centre)[:, :3][::3].round(2).tolist()
        outl = [(T[i] @ corners)[:3].T.round(2).tolist() for i in range(0, len(frames), 60)]
        info.append({"key": key, "label": label, "pixel_error_mm": round(err, 1), "path": path, "outlines": outl})
        print(f"  {label:24s} mean pixel error {err:5.1f} mm")

    meta = {"run": run, "shape": list(shape), "voxel": voxel, "origin": lo.round(3).tolist(),
            "frames": len(frames), "sources": info}
    html = TEMPLATE.replace("__META__", json.dumps(meta)).replace("__VOLS__", json.dumps(vols))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    print(f"wrote {out} ({out.stat().st_size / 1e6:.1f} MB)")


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>US Volume 3D</title>
<style>
:root{--bg:#f6f5f1;--panel:#ffffff;--text:#1d1d1b;--muted:#6b6a64;--line:#dcdad2;--accent:#2a78d6}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#141413;--panel:#1f1f1d;--text:#ecebe6;--muted:#a3a29b;--line:#3a3935;--accent:#6aa6ff}}
:root[data-theme="dark"]{--bg:#141413;--panel:#1f1f1d;--text:#ecebe6;--muted:#a3a29b;--line:#3a3935;--accent:#6aa6ff}
*{box-sizing:border-box}html,body{margin:0;height:100%}
body{background:var(--bg);color:var(--text);font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif;display:flex;flex-direction:column}
header{padding:12px 16px 4px}h1{font-size:17px;margin:0}header p{margin:2px 0 0;color:var(--muted);font-size:13px}
main{flex:1;display:flex;min-height:0;gap:12px;padding:8px 16px 16px}
#view{flex:1;min-width:0;border-radius:10px;overflow:hidden;background:#0b0b0b;position:relative}
#view canvas{display:block;width:100%;height:100%}
#legend{position:absolute;left:10px;bottom:10px;color:#ddd;font-size:12px;background:rgba(0,0,0,.45);padding:6px 8px;border-radius:6px}
aside{width:290px;flex:none;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px;overflow:auto}
aside h2{font-size:13px;margin:12px 0 6px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.03em}aside h2:first-child{margin-top:0}
label{display:flex;align-items:center;gap:8px;margin:5px 0}select,input[type=range]{width:100%}
select{background:var(--bg);color:var(--text);border:1px solid var(--line);border-radius:6px;padding:5px}
.sw{width:11px;height:11px;border-radius:2px;flex:none}.err{margin-left:auto;color:var(--muted);font-variant-numeric:tabular-nums}
#loading{position:absolute;inset:0;display:grid;place-items:center;color:#ccc}
@media (max-width:760px){main{flex-direction:column}aside{width:auto}#view{min-height:60vh}}
</style></head><body>
<header><h1>Reconstructed US volume, <span id="run"></span></h1>
<p>Each volume stacks the same US images, placed with a different pose source. Drag to rotate, scroll to zoom, right-drag to pan.</p></header>
<main><div id="view"><div id="loading">decoding volumes…</div><div id="legend"></div></div>
<aside>
<h2>Render</h2>
<label>mode <select id="mode"><option value="1">overlay: A green, B magenta</option><option value="0">A only (max. intensity)</option><option value="2">A only (translucent)</option></select></label>
<label>A <select id="volA"></select></label>
<label>B <select id="volB"></select></label>
<label>threshold <input id="thr" type="range" min="0" max="0.9" step="0.01" value="0.25"></label>
<label>brightness <input id="gain" type="range" min="0.5" max="4" step="0.05" value="1.6"></label>
<h2>Probe path and image outlines</h2>
<div id="paths"></div>
<h2>Mean pixel error vs true poses</h2>
<div id="errs"></div>
</aside></main>
<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>
<script type="module">
import * as THREE from "three";
import {OrbitControls} from "three/addons/controls/OrbitControls.js";
const META = __META__;
const VOLS = __VOLS__;
const COLORS = {"gt":"#3fbf5f","model":"#f0a030","zero":"#9a9a9a"};
const colorOf = k => COLORS[k] || (k.startsWith("anchored") ? "#d04ad8" : "#4aa3ff");
document.getElementById("run").textContent = META.run;

async function decode(b64){
  const res = await fetch("data:application/octet-stream;base64," + b64);
  const stream = res.body.pipeThrough(new DecompressionStream("gzip"));
  return new Uint8Array(await new Response(stream).arrayBuffer());
}
const [nx, ny, nz] = META.shape, vox = META.voxel, org = META.origin;
const size = new THREE.Vector3(nx*vox, ny*vox, nz*vox);
const center = new THREE.Vector3(org[0] + size.x/2, org[1] + size.y/2, org[2] + size.z/2);

const view = document.getElementById("view");
const renderer = new THREE.WebGLRenderer({antialias: true});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
view.prepend(renderer.domElement);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(40, 1, 1, 10000);
const dist = 2.2 * Math.max(size.x, size.y, size.z);
camera.position.copy(center).add(new THREE.Vector3(dist*0.6, -dist*0.6, dist*0.5));
camera.up.set(0, 0, 1);
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.copy(center); controls.update();

const textures = await Promise.all(VOLS.map(async b64 => {
  const t = new THREE.Data3DTexture(await decode(b64), nx, ny, nz);
  t.format = THREE.RedFormat; t.type = THREE.UnsignedByteType;
  t.minFilter = t.magFilter = THREE.LinearFilter; t.unpackAlignment = 1; t.needsUpdate = true;
  return t;
}));
document.getElementById("loading").remove();

const mat = new THREE.ShaderMaterial({
  glslVersion: THREE.GLSL3, side: THREE.BackSide, transparent: true,
  uniforms: {volA: {value: textures[0]}, volB: {value: textures[1] || textures[0]}, mode: {value: 1},
             thr: {value: 0.25}, gain: {value: 1.6}, dims: {value: new THREE.Vector3(nx, ny, nz)}},
  vertexShader: `out vec3 vOrigin; out vec3 vDir;
    void main(){ vOrigin = (inverse(modelMatrix) * vec4(cameraPosition, 1.0)).xyz; vDir = position - vOrigin;
                 gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
  fragmentShader: `precision highp float; precision highp sampler3D;
    uniform sampler3D volA, volB; uniform int mode; uniform float thr, gain; uniform vec3 dims;
    in vec3 vOrigin; in vec3 vDir; out vec4 color;
    vec2 hit(vec3 o, vec3 d){ vec3 inv = 1.0/d; vec3 t0 = (vec3(-0.5)-o)*inv, t1 = (vec3(0.5)-o)*inv;
      vec3 a = min(t0,t1), b = max(t0,t1); return vec2(max(max(a.x,a.y),a.z), min(min(b.x,b.y),b.z)); }
    float lev(float v){ return clamp((v - thr) / (1.0 - thr) * gain, 0.0, 1.0); }
    void main(){
      vec3 d = normalize(vDir); vec2 b = hit(vOrigin, d); if (b.x > b.y) discard; b.x = max(b.x, 0.0);
      float dt = 0.5 / max(dims.x, max(dims.y, dims.z)); vec3 p = vOrigin + b.x * d;
      float ma = 0.0, mb = 0.0; vec4 acc = vec4(0.0);
      for (int i = 0; i < 2048; i++) {
        float t = b.x + float(i) * dt; if (t > b.y || acc.a > 0.97) break;
        vec3 q = vOrigin + t * d + 0.5;
        float a = texture(volA, q).r, c = texture(volB, q).r;
        ma = max(ma, a); mb = max(mb, c);
        if (mode == 2) { float v = lev(a); float al = v * v * 0.08; acc.rgb += (1.0 - acc.a) * al * vec3(v); acc.a += (1.0 - acc.a) * al; }
      }
      if (mode == 0) { float v = lev(ma); if (v <= 0.0) discard; color = vec4(vec3(v), 1.0); }
      else if (mode == 1) { float g = lev(ma), m = lev(mb); if (g + m <= 0.0) discard; color = vec4(m, g, m, 1.0); }
      else { if (acc.a <= 0.0) discard; color = vec4(acc.rgb / max(acc.a, 1e-3), acc.a); }
    }`
});
const box = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), mat);
box.scale.copy(size); box.position.copy(center); scene.add(box);
const frame = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(1, 1, 1)),
  new THREE.LineBasicMaterial({color: 0x555555}));
frame.scale.copy(size); frame.position.copy(center); scene.add(frame);

const lines = {}, outlines = {};
let showOutlines = false;
for (const s of META.sources) {
  const g = new THREE.Group(), o = new THREE.Group();
  g.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(s.path.map(p => new THREE.Vector3(...p))),
                       new THREE.LineBasicMaterial({color: colorOf(s.key)})));
  for (const ol of s.outlines) {
    const pts = ol.map(p => new THREE.Vector3(...p)); pts.push(pts[0]);
    o.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({color: colorOf(s.key), transparent: true, opacity: 0.45})));
  }
  g.visible = s.key === "gt" || s.key.startsWith("anchored"); o.visible = false;
  scene.add(g); scene.add(o); lines[s.key] = g; outlines[s.key] = o;
}

const selA = document.getElementById("volA"), selB = document.getElementById("volB");
META.sources.forEach((s, i) => { for (const sel of [selA, selB]) sel.add(new Option(s.label, i)); });
selA.value = 0; selB.value = META.sources.findIndex(s => s.key.startsWith("anchored")) >= 0
  ? META.sources.findIndex(s => s.key.startsWith("anchored")) : Math.min(1, META.sources.length - 1);
const paths = document.getElementById("paths"), errs = document.getElementById("errs");
for (const s of META.sources) {
  const l = document.createElement("label");
  l.innerHTML = `<input type="checkbox" ${lines[s.key].visible ? "checked" : ""}><span class="sw" style="background:${colorOf(s.key)}"></span>${s.label}`;
  l.querySelector("input").onchange = e => { lines[s.key].visible = e.target.checked; outlines[s.key].visible = e.target.checked && showOutlines; };
  paths.append(l);
  if (s.key !== "gt") { const e = document.createElement("label");
    e.innerHTML = `<span class="sw" style="background:${colorOf(s.key)}"></span>${s.label}<span class="err">${s.pixel_error_mm} mm</span>`; errs.append(e); }
}
const ol = document.createElement("label");
ol.innerHTML = `<input type="checkbox"> image outlines every 2 s`;
ol.querySelector("input").onchange = e => { showOutlines = e.target.checked; for (const k in outlines) outlines[k].visible = showOutlines && lines[k].visible; };
paths.append(ol);
const legend = document.getElementById("legend");
function update() {
  const u = mat.uniforms; u.volA.value = textures[+selA.value]; u.volB.value = textures[+selB.value];
  u.mode.value = +document.getElementById("mode").value;
  u.thr.value = +document.getElementById("thr").value; u.gain.value = +document.getElementById("gain").value;
  selB.disabled = u.mode.value !== 1;
  const A = META.sources[+selA.value].label, B = META.sources[+selB.value].label;
  legend.innerHTML = u.mode.value === 1
    ? `<span style="color:#5f5">■</span> ${A} &nbsp; <span style="color:#f5f">■</span> ${B} &nbsp; white: both agree`
    : `${A} · ${META.frames} frames · voxel ${META.voxel.toFixed(2)} mm`;
}
for (const id of ["mode", "volA", "volB", "thr", "gain"]) document.getElementById(id).oninput = update;
update();
function resize() { const w = view.clientWidth, h = view.clientHeight; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); }
new ResizeObserver(resize).observe(view); resize();
renderer.setAnimationLoop(() => { controls.update(); renderer.render(scene, camera); });
</script></body></html>
"""

if __name__ == "__main__":
    main()
