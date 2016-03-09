#/bin/bash
rostopic pub /gripper_controller/command trajectory_msgs/JointTrajectory "header: 
  seq: 0
  stamp: 
    secs: 0
    nsecs: 0
  frame_id: ''
joint_names: ['gripper_left_finger_joint', 'gripper_right_finger_joint']
points: 
  - 
    positions: [0.05, 0.05]
    velocities: []
    accelerations: []
    effort: []
    time_from_start: 
      secs: 1
      nsecs: 0" --once
