import time
from motor.motor import LkMotor # 假设这是你导入 LkMotor 的方式
# from motor.protocol import radian_to_degree # 这个测试脚本不需要转换角度

# --- 配置参数 ---
SERIAL_PORT = "/dev/tty.usbmodem01234567895"  # 修改为你要测试的电机串口
MOTOR_ID = 1                               # 修改为你要测试的电机ID
NUM_TEST_ITERATIONS = 100                   # 执行 refresh 测试的次数
INITIAL_STABILIZATION_DELAY = 0.5           # 启动电机后的稳定延时 (秒)
# --- --------- ---

def test_single_motor_refresh_performance():
    """
    测试单个电机 motor.refresh() 方法的性能。
    """
    print(f"准备测试电机 (ID: {MOTOR_ID})，串口: {SERIAL_PORT}")

    motor = None  # 先声明变量
    try:
        # 初始化电机
        print("正在初始化电机...")
        motor = LkMotor(SERIAL_PORT, motor_id=MOTOR_ID)
        print("电机初始化成功。")

        # 启动电机
        print("正在启动电机...")
        motor.enable()
        time.sleep(INITIAL_STABILIZATION_DELAY) # 等待电机稳定
        print("电机已启动。")

    except Exception as e:
        print(f"错误：电机设置失败 - {e}")
        if motor:
            try:
                motor.disable() # 尝试关闭电机
            except Exception as e_disable:
                print(f"尝试关闭电机时出错: {e_disable}")
        return # 无法继续测试

    refresh_timings_ms = []
    print(f"\n开始执行 {NUM_TEST_ITERATIONS} 次 motor.refresh() 测试...")

    try:
        for i in range(NUM_TEST_ITERATIONS):
            # 记录refresh调用前的时间
            time_before_refresh = time.perf_counter()

            # 调用 motor.refresh()
            motor.refresh()

            # 记录refresh调用后的时间
            time_after_refresh = time.perf_counter()

            # 计算耗时并转换为毫秒
            duration_ms = (time_after_refresh - time_before_refresh) * 1000
            refresh_timings_ms.append(duration_ms)

            # 打印当次耗时
            # 为了避免过多打印影响测试，可以考虑注释掉或每N次打印一次
            print(f"测试 {i+1}/{NUM_TEST_ITERATIONS}: motor.refresh() 耗时 = {duration_ms:.3f} ms")

            # 可选：在两次refresh之间加入一个极短的延时，
            # 一般来说，为了纯粹测试refresh性能，不需要这个延时。
            # time.sleep(0.001) # 1毫秒

            # 检查电机状态 (可选, 如果refresh后需要验证)
            # if not motor.is_valid():
            #     print(f"警告: 测试 {i+1} 后电机数据无效!")
            #     break # 可以选择中断测试

    except KeyboardInterrupt:
        print("\n测试被用户中断。")
    except Exception as e:
        print(f"\n测试过程中发生严重错误: {e}")
    finally:
        # 无论如何都尝试关闭电机
        if motor:
            print("\n正在关闭电机...")
            try:
                motor.disable()
                print("电机已关闭。")
            except Exception as e:
                print(f"关闭电机时发生错误: {e}")

    # 打印统计结果
    if refresh_timings_ms:
        print("\n--- motor.refresh() 耗时统计 ---")
        print(f"总测试次数: {len(refresh_timings_ms)}")
        average_time = sum(refresh_timings_ms) / len(refresh_timings_ms)
        min_time = min(refresh_timings_ms)
        max_time = max(refresh_timings_ms)
        print(f"平均耗时: {average_time:.3f} ms")
        print(f"最小耗时: {min_time:.3f} ms")
        print(f"最大耗时: {max_time:.3f} ms")

        # 如果需要更详细的统计，可以计算标准差
        # import statistics
        # if len(refresh_timings_ms) > 1:
        #     std_dev = statistics.stdev(refresh_timings_ms)
        #     print(f"耗时标准差: {std_dev:.3f} ms")
    else:
        print("未能收集到任何耗时数据。")

if __name__ == "__main__":
    test_single_motor_refresh_performance()