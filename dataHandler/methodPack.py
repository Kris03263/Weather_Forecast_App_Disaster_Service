from geopy.geocoders import Nominatim
import geopy.geocoders,certifi,ssl,math
import time
import os
from flask import render_template
from PIL import Image
from html2image import Html2Image
import requests
import cv2
import json
import numpy as np
import shutil
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
    url = f'http://420269.xyz/Users/GetStorageCity?ID={userID}'#這邊還需要更改
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

def OutPutEarthPicture(latitude,longitude,intensity,nowTime):
    def lat_lon_to_pixels(lat, lon, min_lat, max_lat, min_lon, max_lon, img_width, img_height):
        x = int((lon - min_lon) / (max_lon - min_lon) * img_width)
        y = int((1 - (lat - min_lat) / (max_lat - min_lat)) * img_height)  # Y 軸應反轉
        return x, y

    def GetJsonData(path):
        with open(path) as f:
            iData = json.load(f)
        return iData

    # 繪製地震數據層
    def draw_earthquake_layer(Data, img_height, img_width):
        earthquake_layer = np.zeros((img_height, img_width, 4), dtype="uint8")  # RGBA 層
        min_lat, max_lat = 21.0, 26.0  # 緯度範圍
        min_lon, max_lon = 119.0, 123.0  # 經度範圍
        cityAxisCode = GetJsonData('cityAxisCode.json')

        eq = Data 
        lat = eq["latitude"]
        lon = eq["longitude"]
        tens = eq["intensity"]
        x, y = lat_lon_to_pixels(lat, lon, min_lat, max_lat, min_lon, max_lon, img_width, img_height)
        for i,t in enumerate(tens):
            alpha = (i+1)*28
            county = t["CountyName"].split('、')
            radius_pixel = 0
            for c in county:
                delta_lat = cityAxisCode[c]["lat"] - lat
                delta_lon = cityAxisCode[c]["lon"] - lon

                # 將經緯度距離轉換為像素距離
                pixel_x_per_lon = img_width / (max_lon - min_lon)
                pixel_y_per_lat = img_height / (max_lat - min_lat)
                distance_pixel = ((delta_lon * pixel_x_per_lon)**2 + (delta_lat * pixel_y_per_lat)**2)**0.5
                radius_pixel = max(radius_pixel, distance_pixel) 

            cv2.circle(earthquake_layer, (x, y), int(radius_pixel), (0, 0, 255, alpha), -1)
        cv2.circle(earthquake_layer, (x, y), 15, (0, 0, 0, 255), -1)  
        cv2.circle(earthquake_layer, (x, y), 5, (255, 255, 255, 255), -1)  
        
        return earthquake_layer

    map_image_path = 'assest/earthQuakeBackground/background.png'
    map_image = cv2.imread(map_image_path, cv2.IMREAD_UNCHANGED)  # 包括透明通道
    if map_image is None:
        raise FileNotFoundError(f"底圖讀取失敗，請確認路徑是否正確：{map_image_path}")

    # 獲取底圖尺寸
    img_height, img_width = map_image.shape[:2]
    earthQuakeData = {"latitude":latitude,"longitude":longitude,"intensity":intensity}

    # 繪製地震數據層
    earthquake_layer = draw_earthquake_layer(earthQuakeData, img_height, img_width)
    
    # 確保底圖有透明通道（RGBA）
    if map_image.shape[2] == 3:
        map_image = cv2.cvtColor(map_image, cv2.COLOR_BGR2BGRA)

    # 半透明疊加：按 alpha 比例混合
    alpha_layer = earthquake_layer[:, :, 3] / 255.0  # 透明度歸一化到 [0, 1]
    for c in range(3):  # 混合 RGB 三個通道
        map_image[:, :, c] = (1 - alpha_layer) * map_image[:, :, c] + alpha_layer * earthquake_layer[:, :, c]

    # 保留底圖透明度通道
    map_image[:, :, 3] = np.maximum(map_image[:, :, 3], earthquake_layer[:, :, 3])
    output_path = f'earthquake_map_{nowTime}.png'
    if not os.path.exists("assest/earthQuakeBackground/"+output_path):
        cv2.imwrite(output_path, map_image)
        shutil.move(output_path,"assest/earthQuakeBackground/")
        print(f"圖片已保存至：{'assest/earthQuakeBackground/'+output_path}")
