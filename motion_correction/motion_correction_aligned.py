import numpy as np 
import os
import csv 
from pyquaternion import Quaternion
from scipy.spatial.transform import Rotation as R
from scipy.spatial.transform import Slerp
from scipy.interpolate import interp1d
import cv2
import tailer as tl

if __name__ == "__main__":
    ## path to event camera data
    root = '/Users/arpit/Spring20/SLAM_16833/project/data/boxes_translation/'
    pose_gt = np.loadtxt(os.path.join(root,'groundtruth.txt'))
    calibration_params = np.loadtxt(os.path.join(root,'calib.txt'))
    K = np.array([
        [calibration_params[0], 0, calibration_params[2]],
        [0, calibration_params[1], calibration_params[3]],
        [0,0,1]
        ], dtype=float)
    # distortion_parameters:
    k1 = -0.368436311798
    k2 = 0.150947243557
    p1 = -0.000296130534385
    p2 = -0.000759431726241
    distCoeffs = np.array([k1,k2,p1,p2], dtype=float)

    # K_inv = np.linalg.inv(K)
    Z = 1 # depth
    images = np.genfromtxt(os.path.join(root,'images.txt'), dtype='str')

    N = 1000000
    events = []
    with open(os.path.join(root,'events.txt')) as csvfile:
        csvfile = tl.tail(csvfile, N)
        spamreader = csv.reader(csvfile, delimiter=' ')
        # for line in spamreader:
        #     events.append(line)
        for i in range(N):
            events.append(next(iter(spamreader)))
    events = np.array(events, dtype=float)
    events_xy = events[:,1:3]
    events_xy_w = cv2.undistortPoints(events_xy.reshape(-1,1,2), K, distCoeffs)
    events_xy_w = events_xy_w.reshape(-1,2)
    events_xy_w = Z*cv2.convertPointsToHomogeneous(events_xy_w)
    
    
    # append first pose
    first_pose = np.zeros(8)
    first_pose[-1] = 1
    pose_gt = np.insert(pose_gt,0,first_pose,axis=0)

    quaternions = pose_gt[:,4:]
    R_object = R.from_quat(quaternions)
    
    slerp = Slerp(pose_gt[:,0], R_object)
    
    # interpolate rotation for events
    times = events[:,0]
    interp_rot_matrices = slerp(times).as_matrix()
    
    # interpolate translation
    interp1d_obj = interp1d(pose_gt[:,0], pose_gt[:,1:4], axis=0)
    events_t = interp1d_obj(times)

    images_timestamps = np.array(list(map(float,images[:,0])))
    reference_rot = slerp(images_timestamps).as_matrix()
    reference_t = interp1d_obj(images_timestamps)
    

    event_index = []
    for j in range(len(images_timestamps)):
        for i in range(len(events)):
            if(events[i, 0] > images_timestamps[j]):
                event_index.append(i)
                break


    N_events = 20000

    fused_frames = []
    for i, ind in enumerate(event_index):
        # I_uncorrected = np.ones((180,240))*0.5
        I_uncorrected = np.zeros((180,240))
        # I = np.ones((180,240))*0.5
        I = np.zeros((180,240))
        R2 = reference_rot[i]
        t2 = reference_t[i]

        for j in range(ind, max(ind-N_events,0), -1):
            ## uncorrected frames
            x_uncorrected = events_xy[j].astype(int)
            I_uncorrected[x_uncorrected[1], x_uncorrected[0]] += 1

            R1 = interp_rot_matrices[j]
            t1 = events_t[j]

            R_rel = np.matmul(R2,np.linalg.inv(R1))
            t_rel = np.matmul(R2,t1-t2)
            # x_w = Z*np.matmul(K_inv, events_xy[j])
            # x_w = np.matmul(R_rel, x_w) + t_rel
            x_w = events_xy_w[j]
            x,_ = cv2.projectPoints(x_w, np.zeros((3)).astype(float), np.zeros((3)).astype(float), K, distCoeffs)
            # x = np.matmul(K, x_w)
            
            # x = x[:2]/x[2]
            x = x.reshape(-1).astype(int)
            if x[1]>=179 or x[0]>=239:
                continue
            I[x[1],x[0]] += 1

            
        scale = 50
        I = I*scale
        
        I_uncorrected *= scale

        cv2.imwrite("events_fused/{:06d}_uncorrected.png".format(i), I_uncorrected)
        cv2.imwrite("events_fused/{:06d}.png".format(i), I)



            




