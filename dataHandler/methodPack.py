from geopy.geocoders import Nominatim
import geopy.geocoders,certifi,ssl,math
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from flask import render_template
from PIL import Image
from html2image import Html2Image
from webdriver_manager.chrome import ChromeDriverManager
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



def generate_earthquake_image(data,sid):
    rendered_html = render_template(
        'card.html',
        time=data.get("時間"),
        magnitude=data.get("規模"),
        depth=data.get("深度"),
        distance=data.get("距離"),
        location_intensity=data.get("所在地區震度"),
        description=data.get("地震資訊"),
    )
    output_dir = "assest/images"
    temp_dir = "assest/temp"
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

        # 保存 HTML 文件以供 Selenium 加載
    html_file = "assest/temp/card.html"
    with open(html_file, 'w', encoding='utf-8') as file:
        file.write(rendered_html)
    hti = Html2Image(output_path=output_dir)
    screenshot_filename = f"earthquake_card_{sid}.png"
# 將 HTML 保存為圖片
    hti.screenshot(
    html_file=html_file,  # 指向你的 HTML 文件
        save_as=screenshot_filename,                      # 僅文件名
        size=(360, 340)                                   # 指定尺寸
    )
    screenshot_path = os.path.join(output_dir, screenshot_filename)

