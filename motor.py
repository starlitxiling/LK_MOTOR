import serial
import time
# from protocol import (
#     checksum, verify_checksum, build_frame,
#     parse_status1, parse_status2, parse_encoder,
#     parse_angle64, parse_circle_angle,
#     MotorTimeoutError, InvalidHeaderError, ChecksumError
# )
from protocol import *

class LkMotor:
    def __init__(self, port: str, baudrate: int = 115200, motor_id: int = 1):
        self.motor_id = motor_id
        self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=3)
        if not self.ser.is_open:
            self.ser.open()

    def send_command(self, cmd: int, data: list[int] = [], expect_reply_len: int = 0) -> bytes:
        frame = build_frame(cmd, self.motor_id, data)
        self.ser.write(frame)
        time.sleep(0.2)

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
        self.send_command(0x88)

    def disable(self):
        self.send_command(0x80)

    def stop(self):
        self.send_command(0x81)

    def clear_error(self):
        self.send_command(0x9B)

    def read_status_1(self):
        resp = self.send_command(0x9A, [], expect_reply_len=13)
        return parse_status1(resp[5:])

    def read_status_2(self):
        resp = self.send_command(0x9C, [], expect_reply_len=13)
        return parse_status2(resp[5:])

    def read_encoder(self):
        resp = self.send_command(0x90, [], expect_reply_len=12)
        return parse_encoder(resp[5:])

    def read_multi_turn_angle(self):
        resp = self.send_command(0x92, [], expect_reply_len=14)
        return parse_angle64(resp[5:])

    def read_single_turn_angle(self):
        resp = self.send_command(0x94, [], expect_reply_len=10)
        return parse_circle_angle(resp[5:])

    def set_zero_ram(self):
        self.send_command(0x95)

    def set_zero_rom(self):
        self.send_command(0x19)

    def clear_turn_count(self):
        self.send_command(0x93)

    def set_open_loop(self, power: int):
        bytes_ = list(power.to_bytes(2, 'little', signed=True))
        self.send_command(0xA0, bytes_)

    def set_torque(self, iq: int):
        bytes_ = list(iq.to_bytes(2, 'little', signed=True))
        self.send_command(0xA1, bytes_)

    def set_speed(self, speed_dps: float):
        val = int(speed_dps * 100)
        bytes_ = list(val.to_bytes(4, 'little', signed=True))
        self.send_command(0xA2, bytes_)

    def move_to_position(self, angle_deg: float):
        val = int(angle_deg * 100)
        bytes_ = list(val.to_bytes(8, 'little', signed=True))
        self.send_command(0xA3, bytes_)

    def move_to_position_with_speed(self, angle_deg: float, speed_dps: float):
        a = int(angle_deg * 100).to_bytes(8, 'little', signed=True)
        s = int(speed_dps * 100).to_bytes(4, 'little')
        self.send_command(0xA4, list(a + s))

    def move_single_circle(self, angle_deg: float, clockwise: bool):
        direction = 0x00 if clockwise else 0x01
        val = int(angle_deg * 100)
        a = list(val.to_bytes(2, 'little'))
        self.send_command(0xA5, [direction] + a + [0x00])

    def move_single_circle_with_speed(self, angle_deg: float, clockwise: bool, speed_dps: float):
        direction = 0x00 if clockwise else 0x01
        a = int(angle_deg * 100).to_bytes(2, 'little')
        s = int(speed_dps * 100).to_bytes(4, 'little')
        self.send_command(0xA6, [direction] + list(a) + [0x00] + list(s))

    def move_incremental(self, angle_delta_deg: float):
        val = int(angle_delta_deg * 100)
        self.send_command(0xA7, list(val.to_bytes(4, 'little', signed=True)))

    def move_incremental_with_speed(self, angle_delta_deg: float, speed_dps: float):
        a = int(angle_delta_deg * 100).to_bytes(4, 'little', signed=True)
        s = int(speed_dps * 100).to_bytes(4, 'little')
        self.send_command(0xA8, list(a + s))

    def read_param(self, param_id: int):
        data = [param_id, 0x00]
        resp = self.send_command(0x40, data, expect_reply_len=13)
        return resp[6:-1]  # 参数值部分

    def write_param_ram(self, param_id: int, param_data: list[int]):
        assert len(param_data) == 6
        data = [param_id] + param_data
        self.send_command(0x42, data)

    def write_param_rom(self, param_id: int, param_data: list[int]):
        assert len(param_data) == 6
        data = [param_id] + param_data
        self.send_command(0x44, data)
