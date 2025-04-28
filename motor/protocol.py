import math

class MotorProtocolError(Exception): pass
class MotorTimeoutError(IOError): pass
class InvalidHeaderError(MotorProtocolError): pass
class ChecksumError(MotorProtocolError): pass

def checksum(data: list[int]) -> int:
    """计算 checksum：对所有字节求和后 & 0xFF"""
    return sum(data) & 0xFF

def verify_checksum(data: bytes) -> bool:
    """校验数据段是否符合 checksum 规则"""
    return checksum(list(data[:-1])) == data[-1]

def build_frame(cmd: int, motor_id: int, data: list[int] = []) -> bytes:
    """
    构造完整控制帧（命令 + 数据）

    参数:
    - cmd: 命令字节（如 0xA2 = 速度环）
    - motor_id: 电机 ID（1 ~ 32）
    - data: 负载数据字段，按协议要求字节排列

    返回:
    - 完整发送帧（含命令校验和 + 数据校验和）
    """
    header = [0x3E, cmd, motor_id, len(data)]
    frame = header + [checksum(header)]
    if data:
        frame += data + [checksum(data)]
    return bytes(frame)

def parse_status1(data: bytes) -> dict:
    """
    解析“状态1”数据结构（命令 0x9A）
    包括温度、电压、电机状态位、错误位等
    """
    return {
        'temperature': int.from_bytes(data[0:1], 'little', signed=True),
        'voltage': int.from_bytes(data[1:3], 'little') * 0.01,
        'motor_state': data[5],
        'error_flags': data[6],
    }

def parse_status2(data: bytes) -> dict:
    """解析“状态2”结构（命令 0x9C）"""
    return {
        'temperature': int.from_bytes(data[0:1], 'little', signed=True),
        'iq_or_power': int.from_bytes(data[1:3], 'little', signed=True),
        'speed_dps': int.from_bytes(data[3:5], 'little', signed=True),
        'encoder_value': int.from_bytes(data[5:7], 'little'),
    }

def parse_encoder(data: bytes) -> dict:
    """解析编码器读取帧（命令 0x90）"""
    return {
        'encoder': int.from_bytes(data[0:2], 'little'),
        'raw': int.from_bytes(data[2:4], 'little'),
        'offset': int.from_bytes(data[4:6], 'little'),
    }

def parse_angle64(data: bytes) -> float:
    """
    解析多圈角度，单位是 0.01°
    :param data: 8 bytes from frame
    :return: 角度值，单位为°
    """
    if len(data) < 8:
        raise ValueError(f"parse_angle64 需要至少8字节数据，实际收到 {len(data)} 字节")
    
    motor_angle_raw = int.from_bytes(data[0:8], byteorder='little', signed=True)

    motor_angle_deg = motor_angle_raw / 100.0

    return motor_angle_deg


def parse_circle_angle(data: bytes) -> float:
    """解析 4 字节单圈角度数据（0x94），单位 0.01°"""
    return int.from_bytes(data[0:4], 'little') / 100.0

def float_to_uint(x: float, x_min: float, x_max: float, bits: int) -> int:
    span = x_max - x_min
    base = x_min
    x = min(max(x, x_min), x_max)
    return int((x - base) * ((1 << bits) - 1) / span)

def degree_to_radian(degree: float) -> float:
    return degree * ( math.pi / 180.0)

def radian_to_degree(radian: float) -> float:
    return (radian * 180.0) / math.pi