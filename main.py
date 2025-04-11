# main.py
from motor import LkMotor

motor = LkMotor("/dev/ttyUSB0", motor_id=1)

motor.enable()
print("读取状态2:", motor.read_status_2())

motor.set_speed(90.0)  # 90°/s
print("设置速度为 90 dps")

motor.move_to_position(360.0)  # 旋转到 360 度
print("电机转动至 360°")

encoder = motor.read_encoder()
print("当前编码器状态:", encoder)

motor.disable()
