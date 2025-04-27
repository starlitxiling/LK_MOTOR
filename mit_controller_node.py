import time
from motor.motor import LkMotor

def main():
    motor = LkMotor(port="/dev/tty.usbserial-AQ04HHBG", motor_id=1)

    print("启动电机")
    motor.enable()
    time.sleep(0.5)

    print("设置零点")
    motor.set_zero_ram()
    time.sleep(0.5)

    motor.refresh()
    if motor.position is None:
        print("初始位置获取失败，终止")
        return

    q_des = motor.position + 20.0

    print("开始控制与频率测试...")

    count = 0
    start_time = time.perf_counter()
    report_interval = 2.0

    last_report_time = start_time

    try:
        while True:
            motor.refresh()

            # if motor.position is None:
            #     print("无法获取电机位置，跳过")
            #     time.sleep(0.001)
            #     continue

            motor.apply_mit_control(
                q_desired=q_des,
                dq_desired=0.0,
                kp=0.008,
                kd=0.00
            )

            count += 1
            now = time.perf_counter()

            if now - last_report_time >= report_interval:
                freq = count / (now - last_report_time)
                print(f"刷新频率: {freq:.2f} Hz")
                count = 0
                last_report_time = now


    except KeyboardInterrupt:
        print("中断，关闭电机")
        motor.disable()

if __name__ == "__main__":
    main()
