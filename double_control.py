from motor.motor import LkMotor
import time
import math

KP = 0.0008    # Nm/deg
KD = 0.00     # Nm/(deg/s)
TORQUE_LIMIT = 1.5  # 最大力矩限制（Nm）
DT = 0.000           # 控制周期（秒）

motor1 = LkMotor("/dev/tty.usbserial-AQ04HHBG", motor_id=1)
motor2 = LkMotor("/dev/tty.usbserial-AQ04HHBG", motor_id=2)

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
    cycle_times = []
    last_freq_print = time.time()

    while True:
        loop_start = time.perf_counter()
        timestamp = time.strftime("[%H:%M:%S]", time.localtime())

        motor1.refresh()
        motor2.refresh()

        if not (motor1.is_valid() and motor2.is_valid()):
            print("电机状态无效，跳过")
            time.sleep(0.01)
            continue

        pos1, vel1 = motor1.getPosition(), motor1.getVelocity()
        pos2, vel2 = motor2.getPosition(), motor2.getVelocity()

        pos_error_1 = pos2 - pos1
        vel_error_1 = vel2 - vel1

        pos_error_2 = pos1 - pos2
        vel_error_2 = vel1 - vel2

        torque1 = KP * pos_error_1 + KD * vel_error_1
        torque2 = KP * pos_error_2 + KD * vel_error_2

        torque1 = max(-TORQUE_LIMIT, min(TORQUE_LIMIT, torque1))
        torque2 = max(-TORQUE_LIMIT, min(TORQUE_LIMIT, torque2))

        print(f"{timestamp} Motor1 ← pos_error={pos_error_1:+.2f}°, vel_error={vel_error_1:+.2f}°/s, τ={torque1:+.2f}Nm")
        print(f"{timestamp} Motor2 ← pos_error={pos_error_2:+.2f}°, vel_error={vel_error_2:+.2f}°/s, τ={torque2:+.2f}Nm")
        print(f"{timestamp} 状态: Motor1[POS={pos1:+.2f}°, VEL={vel1:+.2f}°/s] | Motor2[POS={pos2:+.2f}°, VEL={vel2:+.2f}°/s]")
        print("-" * 80)

        motor1.set_torque_nm(torque1)
        motor2.set_torque_nm(torque2)

        loop_end = time.perf_counter()
        elapsed = loop_end - loop_start

        print(f"elapsed = {elapsed:.6f} s")

        # time.sleep(max(0, DT - elapsed))

except KeyboardInterrupt:
    print("控制中断，关闭电机")
    motor1.disable()
    motor2.disable()