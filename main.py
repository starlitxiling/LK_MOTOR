from motor import LkMotor

def safe_test():
    try:
        motor = LkMotor(port="/dev/ttyUSB0", motor_id=1)

        print("🟢 启动电机")
        motor.enable()

        print("📍 设置当前位置为零点（RAM）")
        motor.set_zero_ram()

        print("🌀 转动 +30° 单圈（顺时针）")
        motor.move_single_circle(angle_deg=30.0, clockwise=True)

        print("⏳ 等待 1 秒")
        time.sleep(1)

        angle = motor.read_multi_turn_angle()
        print(f"📊 当前多圈角度: {angle:.2f}°")

        print("🔴 关闭电机")
        motor.disable()

    except MotorTimeoutError:
        print("❌ 通信超时，未收到电机回应")
    except InvalidHeaderError:
        print("❌ 帧头错误")
    except ChecksumError:
        print("❌ 校验失败")
    except Exception as e:
        print(f"❌ 其他异常: {e}")

if __name__ == "__main__":
    safe_test()
