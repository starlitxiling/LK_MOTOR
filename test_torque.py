import time
from motor.motor import LkMotor

def main():
    motor = LkMotor(port="/dev/ttyUSB0", motor_id=1)

    print("启动电机")
    motor.enable()
    time.sleep(0.5)

    print("设置当前位置为零点")
    motor.set_zero_ram()
    time.sleep(0.5)

    KT = 0.0482
    target_torque = 0.05

    print(f"开始施加固定 {target_torque:.2f} N·m 扭矩...")

    try:
        while True:
            motor.set_torque_nm(target_torque, kt=KT)

            motor.refresh()

            if motor.is_valid():
                print(f"目标扭矩: {target_torque:+.2f} N·m | 反馈扭矩: {motor.torque:+.4f} N·m")
            else:
                print("电机状态无效，跳过...")

            time.sleep(1)

    except KeyboardInterrupt:
        print("中断，关闭电机")
        motor.disable()

if __name__ == "__main__":
    main()
