self.log('+++ Initializing Module Script +++')

#Publishing fake Trashes and Bins ==================================================
# binMsg = JointState()
# binMsg.name = ['blue', 'green', 'yellow']
# binMsg.position = [0.66, 0.66, 0.56]
# binMsg.velocity = [0.31, 0, -0.32]

# poseList = [[0.10599999999999998, 0.75, 11, -0.004222495939768292, 0.9999910852242827, -6.123179408479028e-17, -2.585533068524967e-19],
# [-0.361, 0.5760000000000001, 11, 0.5650443717528625, 0.825060517750312, -5.0520386108288877e-17, 3.4598989062168507e-17],
# [0.1999999999999998, 0.63, 22, 1.0, 0.0, 0.0, 6.123233995736766e-17],
# [0.30600000000000005, 0.529, 13, -0.002238052132716429, 0.9999974955581895, -6.123218660453532e-17, -1.3704116903280412e-19],
# [-0.07500000000000001, 0.684, 13, -0.3738952804399497, 0.927470926371674, -5.679121506416506e-17, -2.2894482920354318e-17],
# [-0.275, 0.651, 13, 0.4103722017889784, 0.9119181191306959, -5.583888028389407e-17, 2.5128050168996203e-17],
# [-0.258, 0.544, 13, 0.24973214185491485, 0.9683149577098129, -5.929219067629136e-17, 1.5291683408341713e-17],
# [-0.356, 0.663, 13, 0.3411705121299028, 0.9400014264100985, -5.755848690235367e-17, 2.0890668782167435e-17],
# [0.10799999999999998, 0.6020000000000001, 13, -0.045283614368823215, 0.9989741709722507, -6.116952604560238e-17, -2.772821669530122e-18]]
# trashMsg = PoseArray()
# trashMsg.header.frame_id="base_link"
# now = rospy.get_rostime()
# trashMsg.header.stamp = now
# for trash in range(len(poseList)):
#     trash_i = Pose()
#     trash_i.position.x = poseList[trash][0]
#     trash_i.position.y = poseList[trash][1]
#     trash_i.position.z = poseList[trash][2]
#     trash_i.orientation.x = poseList[trash][3]
#     trash_i.orientation.y = poseList[trash][4]
#     trash_i.orientation.z = poseList[trash][5]
#     trash_i.orientation.w = poseList[trash][6]
#     trashMsg.poses.append(trash_i)

# self.bin_poses_publisher.publish(binMsg)
# time.sleep(0.5)
# self.trash_poses_publisher.publish(trashMsg)
#=======================================================================================

# real Image =======================================================================
def binSetup(self):
    self.vision.snapBinImg()
    binMsg = self.vision.getBin()
    self.bin_poses_publisher.publish(binMsg)
    return binMsg

def traySetup(self):
    # test_1 = Pose()
    # test_1.position.x = 0.4
    # test_1.position.y = binMsg.velocity[0]
    # test_1.position.z = binMsg.position[0]+0.1*sin(0.5236)
    # test_1.orientation.x = 0
    # test_1.orientation.y = -0.258
    # test_1.orientation.z = 0
    # test_1.orientation.w = 0.966
    # a = self.kin_solver.computeIK(test_1, 'least_dist', self.getStates())
    # self.log(np.array(a)*(180/pi))
    # # self.moveTo(a,12, blocking = 1)
    time.sleep(0.5)
    self.moveTo(self.preconfig_pose['tray_left_1'],12, blocking = 1)
    time.sleep(0.5)
    self.vision.snapPano('l')
    self.moveOne(4, self.preconfig_pose['tray_left_2'][3],4, blocking = 1)
    time.sleep(0.5)
    self.vision.snapPano('l')
    self.moveOne(4, self.preconfig_pose['tray_left_3'][3],4, blocking = 1)
    time.sleep(0.5)
    self.vision.snapPano('l')

    leftTrashPose,leftPickTrashImg,leftTrashNum = self.vision.findTrash('l',panomode=0,persmode=0)
    self.left_tray_publisher.publish(leftPickTrashImg)
    self.moveTo(self.preconfig_pose['transition'],7, blocking = 1)
    self.moveTo(self.preconfig_pose['tray_right_1'],7, blocking = 1)
    time.sleep(0.5)
    self.vision.snapPano('r')
    self.moveOne(4, self.preconfig_pose['tray_right_2'][3],4, blocking = 1)
    time.sleep(0.5)
    self.vision.snapPano('r')
    self.moveOne(4, self.preconfig_pose['tray_right_3'][3],4, blocking = 1)
    time.sleep(0.5)
    self.vision.snapPano('r')
    rightTrashPose,rightPickTrashImg,rightTrashNum = self.vision.findTrash('r',panomode=0,persmode=0)
    self.right_tray_publisher.publish(rightPickTrashImg)
    trashMsg = PoseArray()
    trashMsg.header.frame_id="base_link"
    now = rospy.get_rostime()
    trashMsg.header.stamp = now
    trashMsg.poses = rightTrashPose.poses+leftTrashPose.poses

    self.trash_poses_publisher.publish(trashMsg)
    # self.moveTo(self.preconfig_pose['home'],10, blocking = 1)
    # self.log('Moving done!')
    return trashMsg

#===============================================================================================

def transferTrash(self, idx, binMsg):
    try:
        global trashMsg
        self.release()
        self.setOD(4, 0)
        trash = trashMsg.poses[idx]
        z_o = 0.14
        t_stand = str(trash.position.z)[0] 
        t_type = str(trash.position.z)[1] 
        if not t_type == '3':
            if t_stand == '1':
                g_o = 0.08
            elif t_stand == '2':
                z_o = 0.108
                g_o = 0
        else:
            g_o = 0.146
            self.grip()

        i = JointState()
        i.name = self.joint_msg.name
        i.position = self.getStates()
        g = JointState()
        g.name = i.name

        try:
            self.log('Solving for all picking configuration...')
            tmp_cfg, tmp_grd = self.pickTrash(trash, z_offset = z_o, guarded_offset = g_o)
            self.log('Finding the best picking configuration...')
            pick_cfg = self.getValidPath(tmp_cfg, q_now = self.getStates()) if len(tmp_cfg) > 1 else tmp_cfg[0]
            self.log('Finding the best guarded picking configuration...')
        except:
            trashMsg.poses.remove(trash)
            self.trash_poses_publisher.publish(trashMsg)
            return 0
        
        trashMsg.poses.remove(trash)
        self.trash_poses_publisher.publish(trashMsg)

        if t_stand != '2':
            if t_type == '3':
                pick_grd = self.kin_solver.leastDist(tmp_grd, q_now = pick_cfg) if len(tmp_grd) > 1 else tmp_grd[0]
            else: 
                pick_grd = self.getValidPath(tmp_grd, q_now = pick_cfg) if len(tmp_grd) > 1 else tmp_grd[0]
        self.log('Solving for all placing configuration...')
        bg_o = 0.13 if not t_type is '3' else 0.24
        tmp_cfg, tmp_grd = self.placeTrash(trash, binMsg, guarded_offset = bg_o)
        self.log('Finding the best placing configuration...')
        place_cfg = self.getValidPath(tmp_cfg, q_now = pick_cfg) if len(tmp_cfg) > 1 else tmp_cfg[0]
        place_grd = self.kin_solver.leastDist(tmp_grd, q_now = place_cfg) if len(tmp_grd) > 1 else tmp_grd[0]

        g.position = pick_cfg
        pick_path = self.plan(i, g)
        if not self.executeTrajectory(pick_path, blocking = 1): return 0
        time.sleep(0.5)
        
        # Guarded picking
        if t_stand != '2': 
            if not self.moveTo(list(pick_grd), 2, blocking = 1): 
                return 0
        time.sleep(0.5)
        if t_type is '3':
            self.setOD(4, 1)
        else:
            self.grip()
        if t_stand != '2': 
            if not self.moveTo(list(pick_cfg), 2, blocking = 1): 
                return 0

        time.sleep(0.25)
        self.isGrip(1)
        time.sleep(0.25)
        i.position = pick_cfg
        g.position = place_cfg
        place_path = self.plan(i, g)
        if not self.executeTrajectory(place_path, blocking = 1): return 0
        time.sleep(0.25)
        self.isGrip(0)
        time.sleep(0.25)
        if not self.moveTo(list(place_grd), 2, blocking = 1): return 0
        time.sleep(0.5)
        if t_type is '3':
            self.setOD(4, 0)
        else:
            self.release()
        time.sleep(0.75)
        if not self.moveTo(list(place_cfg), 2, blocking = 1): return 0

        self.release()
        self.setOD(4, 0)
    except Exception as e:
        self.log('%s'%e, 'error')
        self.release()
        self.setOD(4, 0)


self.moveTo(self.preconfig_pose['bin_snap'],12, blocking = 1)
time.sleep(0.5)

for _ in range(5):
    try:
        binMsg = binSetup(self)
        break
    except:
        self.log('Bin not found!', 'warn')
    time.sleep(0.5)
binMsg.velocity = [0.315, 0, -0.315]

while 1:
    trashMsg = traySetup(self)
    for c in range(len(trashMsg.poses)):
        transferTrash(self, 0, binMsg)
        self.log('Pick count: {}'.format(c))
    self.release()
    a = input('Continue? (Y/n): ')
    if str(a).lower() == 'y':
        pass
    else:
        break

self.log('Finished program cleanly!')
# transferTrash(self, 5, binMsg)


