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
    root = '/Users/arpit/Spring20/SLAM_16833/project/data/boxes_translation/'
    out_path = './events_fused_paper_pos_preint_update/'
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    pose_gt = np.loadtxt(os.path.join(root,'groundtruth.txt'))
    # pose_gt = np.loadtxt(os.path.join(root,'update_bag_translation_3.txt'))
    # # clean data for imu pre integration text files
    # for i in range(len(pose_gt)):
    #     try:
    #         if pose_gt[i,0] >= 1:
    #             pose_gt = np.delete(pose_gt,i,0)
    #             i = i-1
    #     except:
    #         break
    # pose_gt[:,0] = np.cumsum(pose_gt[:,0]) # for delta values

    calibration_params = np.loadtxt(os.path.join(root,'calib.txt'))
    K = np.array([
        [calibration_params[0], 0, calibration_params[2]],
        [0, calibration_params[1], calibration_params[3]],
        [0,0,1]
        ])
    K_inv = np.linalg.inv(K)
    Z = 1 # depth
    N = 1000000
    N_events = 10000
    events = []
    with open(os.path.join(root,'events.txt')) as csvfile:
        csvfile = tl.tail(csvfile, N)
        spamreader = csv.reader(csvfile, delimiter=' ')
        for i in range(N):
            events.append(next(iter(spamreader)))
            
    events = np.array(events, dtype=float)
    events = events[events[:,-1]==1]
    events_xy = np.hstack((events[:,1:3],np.ones((len(events),1))))
    
    # append first pose
    first_pose = np.zeros(8)
    first_pose[-1] = 1
    pose_gt = np.insert(pose_gt,0,first_pose,axis=0)

    quaternions = pose_gt[:,4:]
    R_object = R.from_quat(quaternions)
    
    # check order of timestamps:
    for i in range(len(pose_gt)-1):
        if pose_gt[i,0] >= pose_gt[i+1,0]:
            print("not in order {}, {}, {}".format(i,pose_gt[i,0],pose_gt[i+1,0]))

    slerp = Slerp(pose_gt[:,0], R_object)
    
    # interpolate rotation for events
    times = events[:,0]
    interp_rot_matrices = slerp(times).as_matrix()
    # out = interp_rots.as_euler('xyz',degrees=True)
    # print(out[:3])
    # iterp_rot_matrices = interp_rots.as_matrix()
    # print(iterp_matrices.shape)

    # interpolate translation
    interp1d_obj = interp1d(pose_gt[:,0], pose_gt[:,1:4], axis=0)
    events_t = interp1d_obj(times)
    # print(events_xyz[:4])


    # fused_frames = []
    j = 0
    I_uncorrected = np.zeros((180,240))
    I = np.zeros((180,240))
    R2 = interp_rot_matrices[N_events-1]
    t2 = events_t[N_events-1]
    total_events = len(events)
    scale = 50
    for i in range(total_events):
        if i%N_events==0 and i>0:
            # dump fused frame
            # eps = 1e-10
            # I = ((I/(np.max(I)+eps))*255
            I = I*scale
            # I_uncorrected = ((I_uncorrected-np.min(I_uncorrected))/(np.max(I_uncorrected)-np.min(I_uncorrected)+eps))*255
            I_uncorrected *= scale
            cv2.imwrite(os.path.join(out_path,"{:06d}_uncorrected.png".format(j)), I_uncorrected)
            cv2.imwrite(os.path.join(out_path,"{:06d}.png".format(j)), I)

            # update target frame
            j += 1
            I_uncorrected = np.zeros((180,240))
            I = np.zeros((180,240))
            ref_index = min((j+1)*N_events-1, total_events-1)
            R2 = interp_rot_matrices[ref_index]
            t2 = events_t[ref_index]
        R1 = interp_rot_matrices[i]
        t1 = events_t[i]
        
        R_rel = np.matmul(R2,np.linalg.inv(R1))
        t_rel = np.matmul(R2,t1-t2)
        x_w = Z*np.matmul(K_inv, events_xy[i])
        x_w = np.matmul(R_rel, x_w) + t_rel
        x = np.matmul(K, x_w)
        x = x[:2]/x[2]
        x = x.astype(int)
        if x[1]>=179 or x[0]>=239:
            continue

        I[x[1],x[0]] += 1
        #DEBUG
        x_uncorrected = events_xy[i].astype(int)
        I_uncorrected[x_uncorrected[1], x_uncorrected[0]] += 1
        
