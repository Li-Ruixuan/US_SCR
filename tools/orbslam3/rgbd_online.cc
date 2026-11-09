/*
 * ORB-SLAM3 RGB-D on a tools/slam_baseline.py export, with the two outputs the comparison needs.
 *
 *   rgbd_online VOCAB SETTINGS SEQ ASSOCIATIONS OUT_DIR MODE N_MAP
 *
 *   MODE slam      as Examples/RGB-D/rgbd_tum: maps the whole sequence (room scan + sweeps)
 *   MODE localize  maps the first N_MAP frames (the room scan), then localisation only: the map is
 *                  frozen, no new keyframes, no loop closing (the same information as our system).
 *                  ORB-SLAM3 still tracks frame to frame (motion model, and visual odometry on
 *                  temporary depth points when few map points match)
 *   MODE reloc     as localize, but every frame after the room scan is relocalised against the frozen map
 *                  on its own (state set to RECENTLY_LOST before each frame, so Tracking runs
 *                  Relocalization(): BoW candidates + PnP + local-map refinement, nothing from the previous
 *                  frame): per-frame localisation, the task of our network. Needs the Tracking.cc patch
 *                  (README 6: the localisation branch relocalises on RECENTLY_LOST)
 *   N_MAP          number of room-scan frames at the start of the sequence (rows of index.csv whose
 *                  run starts with "room-"); ignored in MODE slam
 *
 * Writes to OUT_DIR:
 *   online.txt             the pose returned by TrackRGBD for each frame, as it was tracked (what a
 *                          real-time system shows), only for frames whose tracking state is OK
 *   CameraTrajectory.txt   ORB-SLAM3's trajectory saved at shutdown (frames re-expressed through their
 *                          reference keyframes after local BA / loop closure: refined after the fact)
 *   times.txt              per frame: timestamp, seconds spent in TrackRGBD, tracking state (2 = OK)
 * Both: TUM format, t tx ty tz qx qy qz qw, camera -> world, metres, timestamps as in ASSOCIATIONS.
 *
 * Plays the sequence in real time like rgbd_tum (waits for the next frame's timestamp), so the mapping
 * threads get the same time as in the original example. Viewer off.
 */

#include <algorithm>
#include <chrono>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <thread>

#include <opencv2/core/core.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>

#include <System.h>

using namespace std;

// System::mpTracker is private; an explicit instantiation may name a private member (standard C++), which gives
// a pointer-to-member without patching System.h. Used by MODE reloc only.
template <typename Tag, typename Tag::type M> struct Rob { friend typename Tag::type get(Tag) { return M; } };
struct TrackerOf { typedef ORB_SLAM3::Tracking *ORB_SLAM3::System::*type; friend type get(TrackerOf); };
template struct Rob<TrackerOf, &ORB_SLAM3::System::mpTracker>;

static void LoadImages(const string &path, vector<string> &rgb, vector<string> &depth, vector<double> &stamps)
{
    ifstream f(path.c_str());
    string s;
    while (getline(f, s)) {
        if (s.empty() || s[0] == '#')
            continue;
        stringstream ss(s);
        double t, td;
        string r, d;
        ss >> t >> r >> td >> d;
        stamps.push_back(t);
        rgb.push_back(r);
        depth.push_back(d);
    }
}

int main(int argc, char **argv)
{
    if (argc != 8) {
        cerr << "usage: rgbd_online VOCAB SETTINGS SEQ ASSOCIATIONS OUT_DIR slam|localize|reloc N_MAP" << endl;
        return 1;
    }
    const string seq = argv[3], out = argv[5], mode = argv[6];
    const int nMap = atoi(argv[7]);
    const bool frozen = mode == "localize" || mode == "reloc";
    if (mode != "slam" && !frozen) {
        cerr << "MODE must be slam, localize or reloc" << endl;
        return 1;
    }

    vector<string> rgb, depth;
    vector<double> stamps;
    LoadImages(argv[4], rgb, depth, stamps);
    const int n = rgb.size();
    if (n == 0) {
        cerr << "no images in " << argv[4] << endl;
        return 1;
    }
    cout << n << " frames, mode " << mode << (frozen ? ", map from the first " + to_string(nMap) : string()) << endl;

    ORB_SLAM3::System SLAM(argv[1], argv[2], ORB_SLAM3::System::RGBD, false);
    const float scale = SLAM.GetImageScale();

    ORB_SLAM3::Tracking *tracker = SLAM.*get(TrackerOf());
    ofstream online((out + "/online.txt").c_str()), times((out + "/times.txt").c_str());
    online << fixed;
    times << fixed;
    int ok = 0, okSweeps = 0;
    vector<double> spentSweeps;

    for (int i = 0; i < n; i++) {
        if (frozen && i == nMap) {
            SLAM.ActivateLocalizationMode();
            cout << "frame " << i << ": localisation only from here" << (mode == "reloc" ? ", every frame relocalised" : "") << endl;
        }
        if (mode == "reloc" && i >= nMap)
            tracker->mState = ORB_SLAM3::Tracking::RECENTLY_LOST;   // forget the previous frame: Relocalization()
        cv::Mat im = cv::imread(seq + "/" + rgb[i], cv::IMREAD_UNCHANGED);
        cv::Mat d = cv::imread(seq + "/" + depth[i], cv::IMREAD_UNCHANGED);
        if (im.empty() || d.empty()) {
            cerr << "cannot read frame " << i << ": " << seq << "/" << rgb[i] << endl;
            return 1;
        }
        if (scale != 1.f) {
            cv::resize(im, im, cv::Size(im.cols * scale, im.rows * scale));
            cv::resize(d, d, cv::Size(d.cols * scale, d.rows * scale));
        }
        auto t0 = chrono::steady_clock::now();
        Sophus::SE3f Tcw = SLAM.TrackRGBD(im, d, stamps[i]);
        auto t1 = chrono::steady_clock::now();

        const int state = SLAM.GetTrackingState();
        const double spent = chrono::duration<double>(t1 - t0).count();
        times << setprecision(6) << stamps[i] << " " << spent << " " << state << "\n";
        if (i >= nMap)
            spentSweeps.push_back(spent);
        if (state == 2) {  // Tracking::OK
            Sophus::SE3f Twc = Tcw.inverse();
            Eigen::Vector3f t = Twc.translation();
            Eigen::Quaternionf q = Twc.unit_quaternion();
            online << setprecision(6) << stamps[i] << setprecision(9) << " " << t.x() << " " << t.y() << " " << t.z()
                   << " " << q.x() << " " << q.y() << " " << q.z() << " " << q.w() << endl;  // flushed: kept if ORB-SLAM3 crashes
            ok++;
            if (i >= nMap)
                okSweeps++;
        }

        double next = i < n - 1 ? stamps[i + 1] - stamps[i] : 0.0;
        if (spent < next)
            this_thread::sleep_for(chrono::microseconds(long((next - spent) * 1e6)));
    }
    online.close();
    times.close();
    cout << "online: " << ok << " / " << n << " frames tracked OK";
    if (frozen)
        cout << " (sweeps " << okSweeps << " / " << n - nMap << ")";
    cout << endl;
    if (!spentSweeps.empty()) {
        sort(spentSweeps.begin(), spentSweeps.end());
        cout << "TrackRGBD time after the room scan: median " << 1000 * spentSweeps[spentSweeps.size() / 2] << " ms, p90 "
             << 1000 * spentSweeps[spentSweeps.size() * 9 / 10] << " ms" << endl;
    }

    SLAM.Shutdown();
    SLAM.SaveTrajectoryTUM(out + "/CameraTrajectory.txt");
    return 0;
}
