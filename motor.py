# motor.py
import serial
import time
from protocol import *

class LkMotor:
    def __init__(self, port: str, baudrate: int = 115200, motor_id: int = 1):
        self.motor_id = motor_id
        self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=0.5)

    def send_command(self, cmd: int, data: list[int] = [], expect_reply_len: int = 0) -> bytes:
        frame = build_frame(cmd, self.motor_id, data)
        self.ser.write(frame)
        time.sleep(0.01)

        if expect_reply_len > 0:
            resp = self.ser.read(expect_reply_len)
            if len(resp) != expect_reply_len:
                raise IOError("Timeout or incomplete response")
            return resp
        return b''

    def enable(self):
        self.send_command(0x88)  # 电机运行命令

    def disable(self):
        self.send_command(0x80)  # 电机关闭命令

    def clear_error(self):
        self.send_command(0x9B, [])  # 清除错误

    def read_status_1(self):
        resp = self.send_command(0x9A, [], expect_reply_len=13)
        return parse_status1(resp[5:])  # 跳过前5字节 CMD Header
    
    def read_status_2(self):
        resp = self.send_command(0x9C, [], expect_reply_len=13)
        return parse_status2(resp[5:])

    def set_open_loop(self, power: int):
        # power: -850 ~ +850
        power_bytes = power.to_bytes(2, 'little', signed=True)
        self.send_command(0xA0, list(power_bytes))

    def set_speed(self, speed_dps: float):
        # speed_dps 单位是 dps，协议单位是 0.01dps
        value = int(speed_dps * 100)
        speed_bytes = value.to_bytes(4, 'little', signed=True)
        self.send_command(0xA2, list(speed_bytes))

    def move_to_position(self, angle_deg: float):
        # angle_deg 单位是 degree，协议单位是 0.01°
        value = int(angle_deg * 100)
        angle_bytes = value.to_bytes(8, 'little', signed=True)
        self.send_command(0xA3, list(angle_bytes))

    def read_encoder(self):
        resp = self.send_command(0x90, [], expect_reply_len=12)
        return parse_encoder(resp[5:])
