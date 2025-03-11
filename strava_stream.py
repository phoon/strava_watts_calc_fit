import requests
from datetime import datetime
import pytz
from dotenv import dotenv_values

ACCESS_TOKEN = dotenv_values().get('ACCESS_TOKEN')

if ACCESS_TOKEN is None:
    print('请在.env文件设置ACCESS_TOKEN')
    exit(-1)

def fetch_strava(url: str, params: dict[str, str] = None):
    HEAHDERS = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    resp = requests.get(url, headers=HEAHDERS, params=params)
    return resp.json()

def get_act_start_time(activity_id: str):
    url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    res = fetch_strava(url, {})
    start_date = res['start_date']
    return datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC)

def get_act_streams(activity_id: str):
    url = f"https://www.strava.com/api/v3/activities/{activity_id}/streams"
    params = {
        "keys": "time,latlng,distance,altitude,heartrate,cadence,watts_calc,velocity_smooth",
        "key_by_type": True
    }

    return fetch_strava(url, params=params)

def fix_data(start_time: float,streams: object):
    time_stream = streams['time']['data']
    latlng_stream = streams['latlng']['data']
    distance_stream = streams['distance']['data']
    altitude_stream = streams['altitude']['data']
    heartrate_stream = streams['heartrate']['data']
    cadene_stream = streams['cadence']['data']
    watts_calc_stream = streams['watts_calc']['data']
    velocity_stream = streams['velocity_smooth']['data']

    processed_data = []
    for i in range(len(time_stream)):
        elapsed_seconds = time_stream[i]
        current_time:float = start_time + elapsed_seconds
        
        lat, lon = latlng_stream[i]
        altitude = altitude_stream[i]
        heartrate = heartrate_stream[i]
        power = watts_calc_stream[i]
        cadence = cadene_stream[i]
        distance = distance_stream[i]
        speed = velocity_stream[i]
        
        processed_data.append({
            'timestamp': current_time,
            'lat': lat,
            'lon': lon,
            'cadence': cadence,
            'distance': distance,
            'altitude': altitude,
            'heartrate': heartrate,
            'power': power,
            'speed': speed
        })
    
    return processed_data
