import datetime
import time
timestamp = time.time()  # 示例时间戳（2025-10-19 13:00:26 CST对应的UTC时间戳）
utc_time = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)  # UTC时间
local_time = utc_time.astimezone(datetime.timezone(datetime.timedelta(hours=8)))  # 转换为CST（UTC+8）
print("本地时间（CST）:", local_time.strftime("%Y-%m-%d %H:%M:%S"))