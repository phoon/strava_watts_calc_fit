from fit_tool.fit_file import FitFile, FitFileHeader
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.record_message import RecordMessage
from fit_tool.profile.messages.session_message import SessionMessage
from fit_tool.profile.messages.activity_message import ActivityMessage
from fit_tool.profile.profile_type import FileType, Manufacturer, Sport, GarminProduct
from fit_tool.fit_file_builder import FitFileBuilder
import strava_stream

def write2fit(path: str = "rewrite_act.fit", activity_id: str=""):
    start_time = strava_stream.get_act_start_time(activity_id).timestamp()
    processed_data = strava_stream.fix_data(start_time, strava_stream.get_act_streams(activity_id))
    end_time = processed_data[-1]['timestamp']
    builder = FitFileBuilder(auto_define=True, min_string_size=50)
    #File id message
    file_id = FileIdMessage()
    file_id.type = FileType.ACTIVITY
    file_id.manufacturer = Manufacturer.GARMIN
    file_id.serial_number = 123456789
    file_id.time_created = start_time * 1000
    file_id.product = GarminProduct.EDGE_1030

    builder.add(file_id)

    # Activity message
    activity = ActivityMessage()
    activity.sport = Sport.CYCLING
    activity.timestamp = end_time * 1000
    activity.num_sessions = 1

    # 计算移动时间
    total_timer_time = 0
    last_lat, last_lon = 0,0
    for record in processed_data:
        if record['lat'] == last_lat and record['lon'] == last_lon: 
            continue
        last_lat = record['lat']
        last_lon = record['lon']
        total_timer_time +=1
    

    activity.total_timer_time = total_timer_time

    builder.add(activity)

    records = []
    for entry in processed_data:
        record = RecordMessage()
        
        timestamp = entry['timestamp']
        record.timestamp = timestamp * 1000
        
        # ==== 修复坐标转换逻辑 ====
        lat = entry['lat']
        lon = entry['lon']
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            print(f"坐标异常: lat={lat}, lon={lon}, 已跳过")
            continue
        
        record.position_lat = lat
        record.position_long = lon
        
        record.altitude = entry['altitude']
        record.heart_rate = entry['heartrate']
        record.power = entry['power']
        record.speed = entry['speed']
        record.cadence = entry['cadence']
        record.distance = entry['distance']

        records.append(record)

    builder.add_all(records)

    # Seession message
    session = SessionMessage()
    session.timestamp = end_time * 1000
    session.start_time = processed_data[0]['timestamp']*1000
    session.total_timer_time = total_timer_time
    session.total_elapsed_time =processed_data[-1]['timestamp'] - processed_data[0]['timestamp']
    session.total_distance = processed_data[-1]['distance']
    session.sport = Sport.CYCLING


    builder.add(session)

    records_bytes = b''.join([record.to_bytes() for record in records])
    records_size = len(records_bytes)

    header = FitFileHeader(
        protocol_version=16,        # 协议版本
        profile_version=2132,       # 配置文件版本
        records_size=records_size,  # 记录部分的总字节数
    )

    fit_file = FitFile(header=header, records=builder.records)
    fit_file = builder.build()
    fit_file.to_file(path)
    

if __name__ == "__main__":
    from sys import argv
    if len(argv) != 2:
        print('Usage:python write_fit.py ACTVITY_ID')
        exit(-1)
    write2fit(activity_id=argv[1])