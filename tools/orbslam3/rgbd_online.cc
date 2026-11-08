/*
 * ORB-SLAM3 RGB-D on a tools/slam_baseline.py export, with the two outputs the comparison needs.
 *
 *   rgbd_online VOCAB SETTINGS SEQ ASSOCIATIONS OUT_DIR MODE N_MAP
 *
 *   MODE slam      as Examples/RGB-D/rgbd_tum: maps the whole sequence (room scan + sweeps)
 *   MODE localize  maps the first N_MAP frames (the room scan), then localisation only: the map is
 *                  frozen, no new keyframes, no loop closing (the same information as our system)
 *   N_MAP          number of room-scan frames at the start of the sequence (rows of index.csv whose
 *                  run starts with "room-"); ignored in MODE slam
 *
 * Writes to OUT_DIR:
 *   online.txt             the pose returned by TrackRGBD for each frame, as it was tracked (what a
 *                          real-time system shows), only for frames whose tracking state is OK
 *   CameraTrajectory.txt   ORB-SLAM3's trajectory saved at shutdown (frames re-expressed through their
 *                          reference keyframes after local BA / loop closure: refined after the fact)
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
        cerr << "usage: rgbd_online VOCAB SETTINGS SEQ ASSOCIATIONS OUT_DIR slam|localize N_MAP" << endl;
        return 1;
    }
    const string seq = argv[3], out = argv[5], mode = argv[6];
    const int nMap = atoi(argv[7]);
    if (mode != "slam" && mode != "localize") {
        cerr << "MODE must be slam or localize" << endl;
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
    cout << n << " frames, mode " << mode << (mode == "localize" ? ", map from the first " + to_string(nMap) : string()) << endl;

    ORB_SLAM3::System SLAM(argv[1], argv[2], ORB_SLAM3::System::RGBD, false);
    const float scale = SLAM.GetImageScale();

    ofstream online((out + "/online.txt").c_str());
    online << fixed;
    int ok = 0, okSweeps = 0;

    for (int i = 0; i < n; i++) {
        if (mode == "localize" && i == nMap) {
            SLAM.ActivateLocalizationMode();
            cout << "frame " << i << ": localisation only from here" << endl;
        }
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

        if (SLAM.GetTrackingState() == 2) {  // Tracking::OK
            Sophus::SE3f Twc = Tcw.inverse();
            Eigen::Vector3f t = Twc.translation();
            Eigen::Quaternionf q = Twc.unit_quaternion();
            online << setprecision(6) << stamps[i] << setprecision(9) << " " << t.x() << " " << t.y() << " " << t.z()
                   << " " << q.x() << " " << q.y() << " " << q.z() << " " << q.w() << endl;  // flushed: kept if ORB-SLAM3 crashes
            ok++;
            if (i >= nMap)
                okSweeps++;
        }

        double spent = chrono::duration<double>(t1 - t0).count();
        double next = i < n - 1 ? stamps[i + 1] - stamps[i] : 0.0;
        if (spent < next)
            this_thread::sleep_for(chrono::microseconds(long((next - spent) * 1e6)));
    }
    online.close();
    cout << "online: " << ok << " / " << n << " frames tracked OK";
    if (mode == "localize")
        cout << " (sweeps " << okSweeps << " / " << n - nMap << ")";
    cout << endl;

    SLAM.Shutdown();
    SLAM.SaveTrajectoryTUM(out + "/CameraTrajectory.txt");
    return 0;
}
