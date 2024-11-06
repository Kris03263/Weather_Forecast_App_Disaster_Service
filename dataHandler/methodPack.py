from geopy.geocoders import Nominatim
import geopy.geocoders,certifi,ssl,math
import sqlite3
import requests
ctx = ssl.create_default_context(cafile=certifi.where())
geopy.geocoders.options.default_ssl_context = ctx

# 實例化
geolocator = Nominatim(scheme='http',user_agent='test')

def setLocate(latitude,longitude):
    # 進行反向地理編碼
    location = geolocator.reverse((latitude, longitude))
    nowCity = location.raw['address']['city'] if location.raw['address'].get('city') else location.raw['address']['county']
    nowdistrict = location.raw['address']['suburb'] if location.raw['address'].get('suburb') else location.raw['address']['town']
    return {
         "city":nowCity,
         "district":nowdistrict
    }

def getStorageCity(userID):
    url = f'http://host.docker.internal:8000/Users/GetStorageCity?ID={userID}'#這邊還需要更改
    response = requests.get(url,verify=False)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        return None
# print(setLocate(10.375919347291584, 114.36556088669015))

def haversine(lat1, lon1, lat2, lon2):
    # 將經緯度轉換為弧度
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # 計算經緯度差
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    # 哈弗辛公式
    a = math.sin(delta_lat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # 地球半徑（公里）
    R = 6371.0
    distance = R * c

    return f"{distance:.2f}"
