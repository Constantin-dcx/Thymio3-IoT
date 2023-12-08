# MQTT Credentials
MQTT_BROKER = '192.168.1.100'
MQTT_PORT = 1883

# MQTT Topics
IMU_TOPIC = "core2/IMU"
GRIPPER_ACTION = "gripper/action"
GRIPPER_STATUS = "gripper/status"

# MQTT Client IDs
THYMIO_CLIENT_ID = 'thymio_client'
REMOTE_CORE2_CLIENT_ID = 'remote_core2_client'
ON_BOARD_CORE2_CLIENT_ID = 'on_board_core2_client'

# Gripper Commands
GRIPPER_CLOSE = b'gripper_close'
GRIPPER_OPEN = b'gripper_open'
GRIPPER_BUSY = b'gripper_busy'
GRIPPER_FINISHED = b'gripper_finished'
