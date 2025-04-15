"""
group.py

定义 MotorGroup 类用于统一管理多个 LkMotor 实例。
"""

class MotorGroup:
    def __init__(self):
        self.motors = {}

    def add_motor(self, name: str, motor):
        """
        注册一个电机实例（按名称标识）
        """
        self.motors[name] = motor

    def get_motor(self, name: str):
        return self.motors.get(name)

    def all_motors(self):
        return list(self.motors.values())

    def refresh_all(self):
        """
        刷新所有电机的状态（适用于 MIT 控制预热阶段）
        """
        for motor in self.motors.values():
            motor.refresh()

    def enable_all(self):
        for motor in self.motors.values():
            motor.enable()

    def disable_all(self):
        for motor in self.motors.values():
            motor.disable()
