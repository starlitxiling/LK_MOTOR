#!/usr/bin/env python3
import rospy
from motor.motor import LkMotor
import time

motor = None
q_des = None

def control_step(event):
    global motor, q_des
    motor.refresh()
    if motor.position is None:
        rospy.logwarn("无法获取电机位置，跳过本轮")
        return

    motor.apply_mit_control(
        q_desired=q_des,
        dq_desired=0.0,
        kp=2.0,
        kd=0.05
    )

    rospy.loginfo(f"位置: {motor.position:.2f}°, 速度: {motor.velocity:.2f}, 扭矩: {motor.torque:.2f}")

def main():
    global motor, q_des
    rospy.init_node("mit_controller_node")

    motor = LkMotor(port="/dev/ttyUSB0", motor_id=1)

    rospy.loginfo("🟢 启动电机")
    motor.enable()
    time.sleep(0.5)

    rospy.loginfo("📍 设置零点")
    motor.set_zero_ram()
    time.sleep(0.5)

    motor.refresh()
    if motor.position is None:
        rospy.logerr("初始位置获取失败，终止")
        return

    q_des = motor.position + 20.0  # 相对目标角度

    # 每 0.02s 控制一次（即 50Hz）
    rospy.Timer(rospy.Duration(0.02), control_step)

    rospy.spin()

    motor.disable()

if __name__ == "__main__":
    main()
