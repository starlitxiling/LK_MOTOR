import serial
import time
from motor.protocol import *


class LkMotor:
    """
    用于控制瓴控电机的串口控制类，封装了所有典型控制命令。
    支持：开环、闭环扭矩、速度、多圈位置、单圈位置、增量控制等。
    """
    def __init__(self, port: str, baudrate: int = 115200, motor_id: int = 1):
        """
        初始化串口连接和电机 ID。
        """
        self.motor_id = motor_id
        self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=3)
        if not self.ser.is_open:
            self.ser.open()
        self.position = None  # 多圈角度，单位度
        self.velocity = None  # 速度，单位 deg/s
        self.torque = None    # 当前 Iq 电流，近似力矩

    def send_command(self, cmd: int, data: list[int] = [], expect_reply_len: int = 0) -> bytes:
        """
        构造、发送一条指令并读取应答，包含头部/数据段校验。
        """
        self.ser.reset_input_buffer()
        frame = build_frame(cmd, self.motor_id, data)
        self.ser.write(frame)
        time.sleep(0.5)

        if expect_reply_len > 0:
            resp = self.ser.read(expect_reply_len)

            if len(resp) != expect_reply_len:
                raise MotorTimeoutError("Timeout or incomplete response")

            if resp[0] != 0x3E:
                raise InvalidHeaderError("Invalid frame header")

            if not verify_checksum(resp[5:]):
                raise ChecksumError("Invalid data checksum")

            return resp
        return b''

    def enable(self):
        """命令 0x88：启动电机"""
        self.send_command(0x88)

    def disable(self):
        """命令 0x80：关闭电机"""
        self.send_command(0x80)

    def stop(self):
        """命令 0x81：立即停止电机（停止控制输出）"""
        self.send_command(0x81)

    def clear_error(self):
        """命令 0x9B：清除错误位"""
        self.send_command(0x9B)

    def set_zero_ram(self):
        """命令 0x19：设置当前位置为零点（断电失效）"""
        self.send_command(0x19)

    def set_zero_rom(self):
        """命令 0x19：持久化零点（部分版本支持 ROM）"""
        self.send_command(0x19)

    def clear_turn_count(self):
        """命令 0x93：清除圈数信息（恢复为单圈）"""
        self.send_command(0x93)

    def read_status_1(self):
        """命令 0x9A：读取状态1（温度、电压、运行状态等）"""
        resp = self.send_command(0x9A, [], expect_reply_len=13)
        return parse_status1(resp[5:])

    def read_status_2(self):
        """命令 0x9C：读取状态2（Iq、电流、速度、编码器）"""
        resp = self.send_command(0x9C, [], expect_reply_len=13)
        return parse_status2(resp[5:])

    def read_encoder(self):
        """命令 0x90：读取编码器值、原始编码值与偏移"""
        resp = self.send_command(0x90, [], expect_reply_len=12)
        return parse_encoder(resp[5:])

    def read_multi_turn_angle(self):
        """命令 0x92：读取多圈角度（单位：0.01°，8字节）"""
        resp = self.send_command(0x92, [], expect_reply_len=14)
        return parse_angle64(resp[5:])

    def read_single_turn_angle(self):
        """命令 0x94：读取单圈角度（单位：0.01°，4字节）"""
        resp = self.send_command(0x94, [], expect_reply_len=10)
        return parse_circle_angle(resp[5:])

    def set_open_loop(self, power: int):
        """
        命令 0xA0：开环控制，输入功率值（-850~850）
        """
        bytes_ = list(power.to_bytes(2, 'little', signed=True))
        self.send_command(0xA0, bytes_)

    def set_torque(self, iq: int):
        """
        命令 0xA1：扭矩环控制，输入目标电流Iq
        """
        bytes_ = list(iq.to_bytes(2, 'little', signed=True))
        self.send_command(0xA1, bytes_)

    def set_speed(self, speed_dps: float):
        """
        命令 0xA2：速度环控制，单位 deg/s，内部以 0.01°/s 表示
        """
        val = int(speed_dps * 100)
        bytes_ = list(val.to_bytes(4, 'little', signed=True))
        self.send_command(0xA2, bytes_)

    def move_to_position(self, angle_deg: float):
        """
        命令 0xA3：位置环控制（多圈），单位为 0.01°
        """
        val = int(angle_deg * 100)
        bytes_ = list(val.to_bytes(8, 'little', signed=True))
        self.send_command(0xA3, bytes_)

    def move_to_position_with_speed(self, angle_deg: float, speed_dps: float):
        """
        命令 0xA4：位置+速度环控制（多圈）
        """
        a = int(angle_deg * 100).to_bytes(8, 'little', signed=True)
        s = int(speed_dps * 100).to_bytes(4, 'little')
        self.send_command(0xA4, list(a + s))

    def move_single_circle(self, angle_deg: float, clockwise: bool):
        """
        命令 0xA5：单圈位置控制（不带速度）
        - clockwise: True=顺时针, False=逆时针
        """
        direction = 0x00 if clockwise else 0x01
        val = int(angle_deg * 100)
        a = list(val.to_bytes(2, 'little'))
        self.send_command(0xA5, [direction] + a + [0x00])

    def move_single_circle_with_speed(self, angle_deg: float, clockwise: bool, speed_dps: float):
        """
        命令 0xA6：单圈位置+速度控制
        """
        direction = 0x00 if clockwise else 0x01
        a = int(angle_deg * 100).to_bytes(2, 'little')
        s = int(speed_dps * 100).to_bytes(4, 'little')
        self.send_command(0xA6, [direction] + list(a) + [0x00] + list(s))

    def move_incremental(self, angle_delta_deg: float):
        """
        命令 0xA7：增量移动（相对位移，单位 0.01°）
        """
        val = int(angle_delta_deg * 100)
        self.send_command(0xA7, list(val.to_bytes(4, 'little', signed=True)))

    def move_incremental_with_speed(self, angle_delta_deg: float, speed_dps: float):
        """
        命令 0xA8：增量移动 + 速度控制
        """
        a = int(angle_delta_deg * 100).to_bytes(4, 'little', signed=True)
        s = int(speed_dps * 100).to_bytes(4, 'little')
        self.send_command(0xA8, list(a + s))

    def read_param(self, param_id: int):
        """
        命令 0x40：读取设定参数
        - 返回值为 6 字节参数体（根据 ID 解释）
        """
        data = [param_id, 0x00]
        resp = self.send_command(0x40, data, expect_reply_len=13)
        return resp[6:-1]

    def write_param_ram(self, param_id: int, param_data: list[int]):
        """
        命令 0x42：将参数写入 RAM（掉电失效）
        """
        assert len(param_data) == 6
        data = [param_id] + param_data
        self.send_command(0x42, data)

    def write_param_rom(self, param_id: int, param_data: list[int]):
        """
        命令 0x44：将参数写入 ROM（掉电保留）
        """
        assert len(param_data) == 6
        data = [param_id] + param_data
        self.send_command(0x44, data)

    def getPosition(self):
        return self.position

    def getVelocity(self):
        return self.velocity

    def getTorque(self):
        return self.torque

    def refresh(self):
        """
        刷新当前电机状态，更新 self.position / velocity / torque。
        建议在控制循环中每次调用一次。
        """
        try:
            self.position = self.read_multi_turn_angle()
            status = self.read_status_2()
            self.velocity = status.get("speed_dps", 0.0)
            self.torque = status.get("iq_or_power", 0.0)
        except Exception as e:
            print(f"[Motor ID {self.motor_id}] 刷新失败: {e}")
            self.position = self.velocity = self.torque = None

    def apply_mit_control(self, q_desired, dq_desired, kp, kd):
        """
        MIT 控制接口：根据目标位置/速度计算目标力矩并通过 set_torque() 发出。
        注意：你应确保先调用 refresh() 更新实际状态。
        """
        if self.position is None or self.velocity is None:
            raise RuntimeError("请先调用 refresh() 刷新状态")

        error_pos = self.position - q_desired
        error_vel = self.velocity - dq_desired
        torque = -kp * error_pos - kd * error_vel

        iq = int(torque)
        self.set_torque(iq)
