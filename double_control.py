from motor.motor import LkMotor
from motor.protocol import radian_to_degree
import time
import threading

# --- 控制参数 ---
KP = 2.0 / 2 / 6 / 1.5
KD = 0.01 / 1.5
TORQUE_LIMIT = 2.5
DT = 0.03

motor1 = LkMotor("/dev/tty.usbmodem01234567895", motor_id=1)
motor2 = LkMotor("/dev/tty.usbmodem01234567893", motor_id=2)

print("启动电机...")
motor1.enable()
motor2.enable()
time.sleep(0.5)

print("设置当前位置为零点...")
motor1.set_zero_ram()
motor2.set_zero_ram()
time.sleep(0.2)

def motor_refresh_worker(motor_instance):
    motor_instance.refresh()

def motor_set_torque_worker(motor_instance, torque_value):
    motor_instance.set_torque_nm(torque_value)

print("开始双电机互控...")
try:
    while True:
        loop_start = time.perf_counter()
        timestamp = time.strftime("[%H:%M:%S]", time.localtime())

        refresh_thread_1 = threading.Thread(target=motor_refresh_worker, args=(motor1,))
        refresh_thread_2 = threading.Thread(target=motor_refresh_worker, args=(motor2,))

        refresh_thread_1.start()
        refresh_thread_2.start()

        refresh_thread_1.join()
        refresh_thread_2.join()

        if not (motor1.is_valid() and motor2.is_valid()):
            print(f"{timestamp} [警告] 电机数据无效，跳过当前控制周期。")
            time.sleep(DT)
            continue

        pos1, vel1 = motor1.getPosition(), motor1.getVelocity()
        pos2, vel2 = motor2.getPosition(), motor2.getVelocity()

        pos_error_1 = pos2 - pos1
        vel_error_1 = vel2 - vel1

        pos_error_2 = pos1 - pos2
        vel_error_2 = vel1 - vel2

        torque1 = KP * pos_error_1 + KD * vel_error_1
        # print(f"pos_torque1:{KP * pos_error_1:.2f}, vel_torque1:{KD * vel_error_1:.2f}") # 可以减少打印以提高性能
        torque2 = KP * pos_error_2 + KD * vel_error_2
        # print(f"pos_torque2:{KP * pos_error_2:.2f}, vel_torque2:{KD * vel_error_2:.2f}") # pos_error_1 typo corrected

        torque1 = max(-TORQUE_LIMIT, min(TORQUE_LIMIT, torque1))
        torque2 = max(-TORQUE_LIMIT, min(TORQUE_LIMIT, torque2))

        print(f"{timestamp}")
        print(f"Motor1 - POS={radian_to_degree(pos1):+.2f}°, VEL={radian_to_degree(vel1):+.2f}°/s, TORQUE={motor1.getTorque():+.3f}Nm (目标:{torque1:+.3f}Nm)")
        print(f"Motor2 - POS={radian_to_degree(pos2):+.2f}°, VEL={radian_to_degree(vel2):+.2f}°/s, TORQUE={motor2.getTorque():+.3f}Nm (目标:{torque2:+.3f}Nm)")
        # print(f"误差 Motor1 ← pos_error={radian_to_degree(pos_error_1):+.2f}°, vel_error={radian_to_degree(vel_error_1):+.2f}°/s")
        # print(f"误差 Motor2 ← pos_error={radian_to_degree(pos_error_2):+.2f}°, vel_error={radian_to_degree(vel_error_2):+.2f}°/s")

        set_torque_thread_1 = threading.Thread(target=motor_set_torque_worker, args=(motor1, torque1))
        set_torque_thread_2 = threading.Thread(target=motor_set_torque_worker, args=(motor2, torque2))

        set_torque_thread_1.start()
        set_torque_thread_2.start()

        set_torque_thread_1.join() 
        set_torque_thread_2.join()

        loop_end = time.perf_counter()
        elapsed = loop_end - loop_start
        
        current_hz = 1 / elapsed if elapsed > 0 else 0
        print(f"循环耗时: {elapsed*1000:.2f} ms, 目标 DT: {DT*1000:.0f} ms, 实际频率: {current_hz:.2f} Hz")
        print("-" * 100)

        sleep_duration = DT - elapsed
        if sleep_duration > 0:
            time.sleep(sleep_duration)
        else:
            print(f"{timestamp} [警告] 循环执行超时! 耗时: {elapsed*1000:.2f}ms, DT: {DT*1000:.0f}ms")

except KeyboardInterrupt:
    print("控制中断，尝试关闭电机...")
finally:
    print("正在关闭电机...")
    try:
        motor1.disable()
    except Exception as e:
        print(f"关闭motor1失败: {e}")
    try:
        motor2.disable()
    except Exception as e:
        print(f"关闭motor2失败: {e}")
    print("电机已尝试关闭。")