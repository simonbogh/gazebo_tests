#!/usr/bin/env python

from copy import deepcopy
import rospy
from gazebo_msgs.srv import SpawnModel, SpawnModelRequest, SpawnModelResponse
from gazebo_msgs.srv import DeleteModel, DeleteModelRequest, DeleteModelResponse
from geometry_msgs.msg import Pose, Point, Quaternion
from dynamic_reconfigure.server import Server
from gazebo_tests.cfg import ModelSpawnConfig
from cube_template import sdf_template


class CubeSpawner(object):
    def __init__(self):
        self.spawn_srv = rospy.ServiceProxy(
            '/gazebo/spawn_sdf_model', SpawnModel)
        self.spawn_srv.wait_for_service()
        self.delete_srv = rospy.ServiceProxy(
            '/gazebo/delete_model', DeleteModel)
        self.delete_srv.wait_for_service()
        self.template = sdf_template
        self.initial_pose = Pose()
        self.initial_pose.position.x = 2.0
        self.initial_pose.position.y = 2.0
        self.initial_pose.position.z = 2.0
        self.curr_cfg = None
        self.dyn_rec = Server(ModelSpawnConfig, self.callback)

    def callback(self, config, level):
        rospy.loginfo("CB: " + str(config))
        self.curr_cfg = config
        if config["click_to_spawn_model"]:
            config["click_to_spawn_model"] = False
            self.spawn_current_model()
        return config

    def get_updated_template(self):
        template = deepcopy(self.template)
        toreplace = ["MODELNAME_", "MASS_",
                     # "IXX_", "IYY_", "IZZ_",
                     "SIZEX_", "SIZEY_", "SIZEZ_",
                     "RESTITUTION_COEFFICIENT_", "THRESHOLD_",
                     "MU_", "MU2_",
                     "FDIR1X_", "FDIR1Y_", "FDIR1Z_",
                     "SLIP1_", "SLIP2_",
                     "SOFT_CFM_", "SOFT_ERP_",
                     "KP_", "KD_",
                     "MINDEPTH_", "MAXVEL_",
                     "VELDECAYLINEAR_", "VELDECAYANGULAR_"]
        for tag in toreplace:
            template = template.replace("_"+tag, str(self.curr_cfg[tag]))
        inertias = ["_IXX_", "_IYY_", "_IZZ_"]
        for tag in inertias:
            template = template.replace(tag, str(self.curr_cfg["IXYZ_"]))
        rospy.loginfo("Replaced template:" + str(template))
        return template

    def create_req(self):
        req = SpawnModelRequest()
        req.model_name = self.curr_cfg["MODELNAME_"]
        req.model_xml = self.get_updated_template()
        req.robot_namespace = ""
        req.reference_frame = ""
        req.initial_pose = self.initial_pose
        return req

    def call(self, req):
        rospy.loginfo("Call: " + str(req))
        resp = self.spawn_srv.call(req)
        rospy.loginfo("Response: " + str(resp))

    def call_delete(self):
        rospy.loginfo("Deleting " + str(self.curr_cfg["MODELNAME_"]))
        del_req = DeleteModelRequest()
        del_req.model_name = self.curr_cfg["MODELNAME_"]
        resp = self.delete_srv.call(del_req)
        rospy.loginfo("Resp of delete: " + str(resp))

    def spawn_current_model(self):
        self.call_delete()
        rospy.sleep(1.0)
        req = self.create_req()
        self.call(req)

if __name__ == '__main__':
    rospy.init_node('gazebo_test')
    cs = CubeSpawner()
    rospy.spin()
