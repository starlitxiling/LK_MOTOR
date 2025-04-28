import time
from motor.motor import LkMotor

def main():
    motor = LkMotor(port="/dev/ttyUSB0", motor_id=1)

    print("启动电机")
    motor.enable()
    time.sleep(0.5)

    print("设置零点")
    motor.set_zero_ram()
    time.sleep(0.5)

    print("清除圈数计数")
    motor.clear_turn_count()
    time.sleep(0.5)

    motor.refresh()
    if motor.position is None:
        print("初始位置获取失败，终止")
        return

    print("开始读取电机状态，手动拨动测试...")

    count = 0
    start_time = time.perf_counter()
    report_interval = 2.0
    last_report_time = start_time

    try:
        while True:
            motor.refresh()

            if motor.position is not None and motor.velocity is not None:
                single_turn = motor.read_single_turn_angle()

                print(f"角度(多圈): {motor.position:+.4f} rad，速度: {motor.velocity:+.4f} rad/s，力矩: {motor.torque:+.2f} Nm")

            else:
                print("状态无效，跳过本轮")

            count += 1
            now = time.perf_counter()

            if now - last_report_time >= report_interval:
                freq = count / (now - last_report_time)
                print(f"当前刷新频率: {freq:.2f} Hz")
                count = 0
                last_report_time = now

            time.sleep(0.005)

    except KeyboardInterrupt:
        print("中断，关闭电机")
        motor.disable()

if __name__ == "__main__":
    main()
