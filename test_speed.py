import time
from motor.motor import LkMotor
from motor.protocol import degree_to_radian

def main():
    motor = LkMotor(port="/dev/ttyUSB0", motor_id=1)

    print("启动电机")
    motor.enable()
    time.sleep(0.5)

    print("设置零点")
    motor.set_zero_ram()
    time.sleep(0.5)

    target_speed_dps = 36 * 2
    print(f"发送目标速度 {target_speed_dps:.2f} deg/s")
    motor.set_speed(target_speed_dps)

    print("开始监测电机反馈速度...")

    count = 0
    start_time = time.perf_counter()
    report_interval = 2.0
    last_report_time = start_time

    try:
        while True:
            motor.refresh()

            if motor.position is not None and motor.velocity is not None:
                print(f"目标: {degree_to_radian(target_speed_dps):+.2f} rad/s | 实际: {motor.velocity:+.2f} rad/s ")
                print(f"angel = {motor.position:+.4f} rad")
                print(f"torque={motor.torque:+.2f} N/m")
            count += 1
            now = time.perf_counter()

            if now - last_report_time >= report_interval:
                freq = count / (now - last_report_time)
                print(f"刷新频率: {freq:.2f} Hz")
                count = 0
                last_report_time = now

            time.sleep(0.005)

    except KeyboardInterrupt:
        print("中断，关闭电机")
        motor.set_speed(0)
        motor.disable()

if __name__ == "__main__":
    main()
