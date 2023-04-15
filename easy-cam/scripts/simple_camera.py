#!/usr/bin/env python3

import cv2
import rospy
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
import rosgraph
master = rosgraph.Master('params_basic')

def get_param(*args):
    return master.getParam(*args)

def gstreamer_pipeline(
    sensor_id = get_param('sensor_id'),
    capture_width=1920,
    capture_height=1080,
    display_width=960,
    display_height=540,
    framerate=30,
    flip_method=0,
):
    print(get_param('sensor_id'))
    return (
        "nvarguscamerasrc sensor-id=%d !"
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


def publish_image():
    """Capture frames from a camera and publish it to the topic /image_raw
    """
    topic_name = get_param('topic_name')
    print(topic_name)
    image_pub = rospy.Publisher(topic_name, Image, queue_size=10)
    bridge = CvBridge()
    capture = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
    while not rospy.is_shutdown():
            # Capture a frame
            ret, img = capture.read()
            if not ret:
                rospy.ERROR("Could not grab a frame!")
                break
            # Publish the image to the topic image_raw
            try:
                img_msg = bridge.cv2_to_imgmsg(img, "bgr8")
                image_pub.publish(img_msg)
            except CvBridgeError as error:
                print(error)

if __name__=="__main__":
    rospy.init_node("my_cam", anonymous=True)
    print("Image is being published to the topic /image_raw ...")
    publish_image()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down!")
