from motor.motor import LkMotor
import time

def main():
    motor = LkMotor(port="/dev/tty.usbserial-AQ04HHBG", motor_id=1)

    print("🟢 启动电机")
    motor.enable()
    time.sleep(0.5)

    print("📍 设置当前位置为零点")
    motor.set_zero_ram()
    time.sleep(0.5)

    # print("🔄 向正方向输出扭矩（Iq = +10）")
    # motor.set_torque(50),
    # time.sleep(1.5)

    # print("🔄 向负方向输出扭矩（Iq = -10）")
    # motor.set_torque(-50)
    # time.sleep(1.5)

    print("🛑 停止输出扭矩")
    motor.set_torque(0)
    time.sleep(0.5)
    
    # motor.refresh() // 控制前要先刷新
    # motor.apply_mit_control(
    #     q_desired=motor.position + 10.0,  # 偏离当前位置10°
    #     dq_desired=0.0,
    #     kp=2.0,
    #     kd=0.05
    # )
    
    motor.refresh()
    motor.apply_mit_control(
        q_desired=motor.position + 10.0,
        dq_desired=0.0,
        kp=2.0,
        kd=0.05
    )
    time.sleep(0.01)
    
    print("📥 刷新状态读取")
    motor.refresh()
    print(f"当前角度: {motor.position:.2f}°")
    print(f"当前速度: {motor.velocity:.2f} deg/s")
    print(f"当前电流/力矩: {motor.torque:.2f}")

    print("🔴 关闭电机")
    motor.disable()

if __name__ == "__main__":
    main()
