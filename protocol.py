class MotorProtocolError(Exception): pass
class MotorTimeoutError(IOError): pass
class InvalidHeaderError(MotorProtocolError): pass
class ChecksumError(MotorProtocolError): pass


def checksum(data: list[int]) -> int:
    return sum(data) & 0xFF

def verify_checksum(data: bytes) -> bool:
    return checksum(list(data[:-1])) == data[-1]

def build_frame(cmd: int, motor_id: int, data: list[int] = []) -> bytes:
    header = 0x3E
    length = len(data)
    frame = [header, cmd, motor_id, length]
    frame.append(checksum(frame))
    if data:
        frame.extend(data)
        frame.append(checksum(data))
    return bytes(frame)


def parse_status1(data: bytes):
    return {
        'temperature': int.from_bytes(data[0:1], 'little', signed=True),
        'voltage': int.from_bytes(data[1:3], 'little') * 0.01,
        'motor_state': data[5],
        'error_flags': data[6],
    }

def parse_status2(data: bytes):
    return {
        'temperature': int.from_bytes(data[0:1], 'little', signed=True),
        'iq_or_power': int.from_bytes(data[1:3], 'little', signed=True),
        'speed_dps': int.from_bytes(data[3:5], 'little', signed=True),
        'encoder_value': int.from_bytes(data[5:7], 'little'),
    }

def parse_encoder(data: bytes):
    return {
        'encoder': int.from_bytes(data[0:2], 'little'),
        'raw': int.from_bytes(data[2:4], 'little'),
        'offset': int.from_bytes(data[4:6], 'little'),
    }

def parse_angle64(data: bytes):
    return int.from_bytes(data[0:8], 'little', signed=True) / 100.0

def parse_circle_angle(data: bytes):
    return int.from_bytes(data[0:4], 'little') / 100.0
