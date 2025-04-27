from motor.motor import LkMotor
import time

def read_motor_info(port: str):
    motor_id = int(input("输入电机 ID: "))
    try:
        motor = LkMotor(port=port, motor_id=motor_id)
        info = motor.read_device_info()

        print("\n获取设备信息成功：")
        print(f"驱动型号      : {info['driver_name']}")
        print(f"电机型号      : {info['motor_name']}")
        print(f"电机标识      : {info['motor_id']}")
        print(f"硬件版本      : {info['hardware_version'] / 10:.1f}")
        print(f"电机版本      : {info['motor_version'] / 10:.1f}")
        print(f"固件版本      : {info['firmware_version'] / 10:.1f}")

    except Exception as e:
        print(f"读取失败: {e}")

def scan_motor_ids(port: str):
    print("正在扫描电机 ID（1~10）...")
    for i in range(1, 11):
        try:
            motor = LkMotor(port=port, motor_id=i)
            motor.refresh()
            if motor.position is not None:
                print(f"ID={i}：角度={motor.position:.2f}°  速度={motor.velocity:.2f}°/s  扭矩={motor.torque:.2f}")
            else:
                print(f"ID={i}：连接成功但未返回状态数据")
        except Exception as e:
            print(f"ID={i} 无响应: {e}")

def main():
    print("=== LK Motor 工具菜单 ===")
    port = "/dev/tty.usbserial-AQ04HHBG"

    while True:
        print("\n请选择操作:")
        print("1. 读取电机信息（驱动型号 / 电机型号 / 版本）")
        print("2. 扫描当前串口下的电机 ID（读取状态）")
        print("3. 退出")

        choice = input("请输入操作编号：").strip()
        if choice == "1":
            read_motor_info(port)
        elif choice == "2":
            scan_motor_ids(port)
        elif choice == "3":
            print("再见！")
            break
        else:
            print("无效选项，请重新输入")

if __name__ == "__main__":
    main()
