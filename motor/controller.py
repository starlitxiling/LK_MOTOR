class MITController:
    """
    MIT 控制器：
    - 每轮调用时执行一次 control step
    - 使用 motor1 的状态控制 motor2，反之亦然（对称控制）
    """

    def __init__(self, motor1, motor2, kp=2.0, kd=0.05):
        self.m1 = motor1
        self.m2 = motor2
        self.kp = kp
        self.kd = kd

    def step(self):
        """
        单步控制：
        - 刷新状态
        - 相互计算并施加力矩（MIT控制律）
        """
        self.m1.refresh()
        self.m2.refresh()

        self.m1.apply_mit_control(
            q_desired=self.m2.position,
            dq_desired=self.m2.velocity,
            kp=self.kp,
            kd=self.kd
        )

        self.m2.apply_mit_control(
            q_desired=self.m1.position,
            dq_desired=self.m1.velocity,
            kp=self.kp,
            kd=self.kd
        )
