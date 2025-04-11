# protocol.py
def checksum(data: list[int]) -> int:
    return sum(data) & 0xFF

def build_frame(cmd: int, motor_id: int, data: list[int] = []) -> bytes:
    header = 0x3E
    length = len(data)
    frame = [header, cmd, motor_id, length]
    frame.append(checksum(frame))  # CMD_SUM

    if data:
        frame.extend(data)
        frame.append(checksum(data))  # DATA_SUM

    return bytes(frame)

def parse_status1(data: bytes):
    if len(data) != 8:
        raise ValueError("Unexpected response length")

    temperature = int.from_bytes(data[0:1], 'little', signed=True)
    voltage = int.from_bytes(data[1:3], 'little')
    motor_state = data[5]
    error_flags = data[6]

    return {
        'temperature': temperature,
        'voltage': voltage * 0.01,
        'motor_state': motor_state,
        'error_flags': error_flags,
    }

def parse_status2(data: bytes):
    if len(data) != 8:
        raise ValueError("Unexpected response length")

    temperature = int.from_bytes(data[0:1], 'little', signed=True)
    iq_or_power = int.from_bytes(data[1:3], 'little', signed=True)
    speed = int.from_bytes(data[3:5], 'little', signed=True)
    encoder = int.from_bytes(data[5:7], 'little')

    return {
        'temperature': temperature,
        'iq_or_power': iq_or_power,
        'speed_dps': speed,
        'encoder_value': encoder,
    }

def parse_encoder(data: bytes):
    if len(data) != 7:
        raise ValueError("Unexpected response length")

    encoder = int.from_bytes(data[0:2], 'little')
    raw = int.from_bytes(data[2:4], 'little')
    offset = int.from_bytes(data[4:6], 'little')

    return {
        'encoder': encoder,
        'raw': raw,
        'offset': offset,
    }
