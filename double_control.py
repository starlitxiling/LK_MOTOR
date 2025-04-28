from motor.motor import LkMotor
from motor.protocol import radian_to_degree
import time

# KP = 2.0 / 2 / 6 / 2
# KD = 0.01

KP = 2.0 / 2 / 6 / 1.5
KD = 0.01 / 1.5

TORQUE_LIMIT = 2.5
DT = 0.01

motor1 = LkMotor("/dev/ttyUSB1", motor_id=1)
motor2 = LkMotor("/dev/ttyUSB0", motor_id=2)

print("启动电机")
motor1.enable()
motor2.enable()
time.sleep(0.5)

print("设置当前位置为零点")
motor1.set_zero_ram()
motor2.set_zero_ram()
time.sleep(0.2)

print("开始双电机互控")
try:
    while True:
        loop_start = time.perf_counter()
        timestamp = time.strftime("[%H:%M:%S]", time.localtime())

        time.sleep(0.01)
        motor1.refresh()
        time.sleep(0.01)
        motor2.refresh()

        if not (motor1.is_valid() and motor2.is_valid()):
            # time.sleep(0.001)
            continue

        pos1, vel1 = motor1.getPosition(), motor1.getVelocity()
        pos2, vel2 = motor2.getPosition(), motor2.getVelocity()

        pos_error_1 = pos2 - pos1
        vel_error_1 = vel2 - vel1

        pos_error_2 = pos1 - pos2
        vel_error_2 = vel1 - vel2

        torque1 = KP * pos_error_1 + KD * vel_error_1
        print(f"pos_torque1:{KP * pos_error_1:.2f}, vel_torque1:{KD * vel_error_1:.2f}")
        torque2 = KP * pos_error_2 + KD * vel_error_2
        print(f"pos_torque1:{KP * pos_error_2:.2f}, vel_torque1:{KD * vel_error_2:.2f}")

        torque1 = max(-TORQUE_LIMIT, min(TORQUE_LIMIT, torque1))
        torque2 = max(-TORQUE_LIMIT, min(TORQUE_LIMIT, torque2))

        print(f"{timestamp}")
        print(f"Motor1 - POS={radian_to_degree(pos1):+.2f}°, VEL={radian_to_degree(vel1):+.2f}°/s, TORQUE={motor1.getTorque():+.3f}Nm")
        print(f"Motor2 - POS={radian_to_degree(pos2):+.2f}°, VEL={radian_to_degree(vel2):+.2f}°/s, TORQUE={motor2.getTorque():+.3f}Nm")
        print(f"误差 Motor1 ← pos_error={radian_to_degree(pos_error_1):+.2f}°, vel_error={radian_to_degree(vel_error_1):+.2f}°/s, 输出扭矩={torque1:+.3f}Nm")
        print(f"误差 Motor2 ← pos_error={radian_to_degree(pos_error_2):+.2f}°, vel_error={radian_to_degree(vel_error_2):+.2f}°/s, 输出扭矩={torque2:+.3f}Nm")
        
        loop_end = time.perf_counter()
        elapsed = loop_end - loop_start
        # print(f"elapsed: {elapsed:.2f} s")
        print(f"hz = {1/elapsed:.2f} Hz")
        print("-" * 100)

        motor1.set_torque_nm(torque1)
        motor2.set_torque_nm(torque2)   

        # time.sleep(max(0, DT - (loop_end - loop_start)))

except KeyboardInterrupt:
    print("控制中断，关闭电机")
    motor1.disable()
    motor2.disable()
