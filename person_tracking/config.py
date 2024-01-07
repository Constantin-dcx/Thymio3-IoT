# MQTT Credentials
MQTT_BROKER = '192.168.1.104'
MQTT_PORT = 1883

# MQTT Topics
# tracking
CAMERA_DETECT_TOPIC = "camera/detect"
# gripper
IMU_TOPIC = "core2/IMU"
GRIPPER_ACTION = "gripper/action"
GRIPPER_STATUS = "gripper/status"

# MQTT Client IDs
THYMIO_CLIENT_ID = 'thymio_client'
# tracking
TRACKING_REMOTE_CLIENT_ID = 'tracking_remote_client'
TRACKING_ON_BOARD_CLIENT_ID = 'tracking_on_board_client'
# gripper
GRIPPER_REMOTE_CLIENT_ID = 'gripper_remote_client'
GRIPPER_ON_BOARD_CLIENT_ID = 'gripper_on_board_client'

# Gripper Commands
GRIPPER_CLOSE = b'gripper_close'
GRIPPER_OPEN = b'gripper_open'
GRIPPER_BUSY = b'gripper_busy'
GRIPPER_FINISHED = b'gripper_finished'

# Camera commands
FACE_NOT_FOUND = 'face_not_found'