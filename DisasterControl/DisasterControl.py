from flask import Blueprint, request, jsonify, make_response,send_file,url_for
from dataHandler.earthQuakeData import getEarthData2, getEarthData
import dataHandler.earthQuakeData
import dataHandler.typhoonData as t
from flask_socketio import emit
from dataHandler.methodPack import getStorageCity,generate_earthquake_image,OutPutEarthPicture
import threading
from io import BytesIO
from flask_cors import CORS
import os
from PIL import Image, ImageDraw, ImageFont


import dataHandler.typhoonData
disasterControl_blueprint = Blueprint('disasterControl_blueprint', __name__)
CORS(disasterControl_blueprint)
background_tasks = {}

@disasterControl_blueprint.route('/test',methods=['GET'])
def test():
    sid = request.args.get('sid')
    last_earthquake_data = {
        "color": "綠色",
        "content": "11/20-12:23嘉義縣義竹鄉發生規模4.6有感地震，最大震度嘉義縣義竹、嘉義縣太保市4級。",
        "depth": "11.7",
        "distance": "239.92",
        "intensity": [
            {
                "AreaDesc": "最大震度1級地區",
                "AreaIntensity": "1級",
                "CountyName": "南投縣、臺東縣、臺中市、花蓮縣、苗栗縣"
            },
            {
                "AreaDesc": "最大震度2級地區",
                "AreaIntensity": "2級",
                "CountyName": "嘉義市、高雄市、澎湖縣、彰化縣"
            },
            {
                "AreaDesc": "最大震度3級地區",
                "AreaIntensity": "3級",
                "CountyName": "臺南市、雲林縣"
            },
            {
                "AreaDesc": "最大震度4級地區",
                "AreaIntensity": "4級",
                "CountyName": "嘉義縣"
            }
        ],
        "latitude": 23.35,
        "location": "嘉義縣政府南南西方  13.9  公里 (位於嘉義縣義竹鄉)",
        "longitude": 120.23,
        "magnitude": "4.6",
        "nowLocation": "臺北市",
        "nowLocationIntensity": "該地區未列入最大震度範圍",
        "reportImg": "https://scweb.cwa.gov.tw/webdata/OLDEQ/202411/2024112012232246496_H.png",
        "shakeImg": "https://scweb.cwa.gov.tw/webdata/drawTrace/plotContour/2024/2024496i.png",
        "time": "2024-11-20 12:23:22"
    }
    result = {
    "地震資訊": last_earthquake_data["content"],
    "深度": last_earthquake_data["depth"],
    "距離": last_earthquake_data["distance"],
    "時間": last_earthquake_data["time"],
    "規模": last_earthquake_data["magnitude"],
    "所在地區震度": last_earthquake_data["nowLocationIntensity"],
    }
    OutPutEarthPicture(last_earthquake_data["latitude"],last_earthquake_data["longitude"],last_earthquake_data["intensity"])
    generate_earthquake_image(result,sid,f'/assest/earthQuakeBackground/earthquake_map_{last_earthquake_data["time"]}.png')
    return send_file(f'./assest/images/earthquake_card_{sid}.png', mimetype='image/png')


@disasterControl_blueprint.route('/GetTyphoonData',methods=['GET'])
def getTyphoonData():
    return jsonify(t.getTyphoonData())

@disasterControl_blueprint.route('/TestEarthQuakeSimulation', methods=['GET', 'POST'])
def testEarthQuakeSimulation():
    if request.method == 'GET':
        return getEarthData2('1', '1', 'test')
    if request.method == 'POST':
        data = request.get_json()
        dataHandler.earthQuakeData.testData.append(data)
        if len(dataHandler.earthQuakeData.testData) > 10:
            dataHandler.earthQuakeData.testData.pop(0)
        return "update successful"


@disasterControl_blueprint.route('/GetEarthQuakeData', methods=['POST'])
def getEarthQuackData():
    data = request.get_json()
    userID = data.get('userID')
    pre_longtitude = data.get('longitude')
    pre_latitude = data.get('latitude')
    if pre_latitude == None or pre_longtitude == None:
        response = make_response(
            {"Status": "Index Error. Please Follow Documentaion Instructions"}, 404)
        return response
    latitude = float(pre_latitude)
    longtitude = float(pre_longtitude)
    print(getStorageCity(userID))
    response = make_response(getEarthData(
        longtitude, latitude, getStorageCity(userID)), 201)
    return response
# 定義地震polling專用事件
def check_and_broadcast_updates(socketio, sid, latitude, longitude, userID, stop_event):
    """
    每秒檢查 API 是否有新的地震資訊，並根據經緯度推送給相關客戶端。
    """
    try:
        socketio.sleep(0.5)
        last_earthquake_data = None
        print('I get into background')
        while not stop_event.is_set():
            socketio.sleep(1)  # 每秒輪詢一次
            # 獲取每個客戶端對應經緯度的最新地震資料
            earthquake_data = getEarthData(
                float(longitude), float(latitude), getStorageCity(userID))
            if last_earthquake_data is None and len(earthquake_data) > 0:
                last_earthquake_data = earthquake_data[0]
                continue
            # 如果地震資料有變化，推送給該用戶
            if len(earthquake_data) > 0 and earthquake_data[0] != last_earthquake_data:
                print("change data")
                last_earthquake_data = earthquake_data[0]
                result = {
                    "地震資訊": last_earthquake_data["content"],
                    "深度": last_earthquake_data["depth"],
                    "距離": last_earthquake_data["distance"],
                    "時間": last_earthquake_data["time"],
                    "規模": last_earthquake_data["magnitude"],
                    "所在地區震度": last_earthquake_data["nowLocationIntensity"],
                }
                if not stop_event.is_set():
                    generate_earthquake_image(sid=sid,data=result)
                    api_full_route = url_for('test', _external=True)
                    result["社交連結url"] = api_full_route + '/' + sid
                    socketio.emit('earthquake_update', result, to=sid)
    except Exception as e:
        print(f"Error during message handling: {e}")

def check_and_broadcast_updates_fake(socketio, sid, latitude, longitude, userID, stop_event):
    """
    每秒檢查 API 是否有新的地震資訊，並根據經緯度推送給相關客戶端。
    """
    try:
        socketio.sleep(0.5)
        last_earthquake_data = None
        print('I get into background')
        while not stop_event.is_set():
            socketio.sleep(1)  # 每秒輪詢一次
            # 獲取每個客戶端對應經緯度的最新地震資料
            earthquake_data = getEarthData2(
                float(longitude), float(latitude), getStorageCity(userID))
            if last_earthquake_data is None and len(earthquake_data) > 0:
                last_earthquake_data = earthquake_data[len(earthquake_data)-1]
                continue
            # 如果地震資料有變化，推送給該用戶
            if len(earthquake_data) > 0 and earthquake_data[len(earthquake_data)-1] != last_earthquake_data:
                print("change data")
                
                last_earthquake_data = earthquake_data[len(earthquake_data)-1]
                _earthQuakeBackgroundPath = f'/assest/earthQuakeBackground/earthquake_map_{last_earthquake_data["time"]}.png'
                #產圖
                if not os.path.exists(_earthQuakeBackgroundPath):
                    OutPutEarthPicture(last_earthquake_data["latitude"],last_earthquake_data["longitude"],last_earthquake_data["intensity"],last_earthquake_data["time"])
                result = {
                    "地震資訊": last_earthquake_data["content"],
                    "深度": last_earthquake_data["depth"],
                    "距離": last_earthquake_data["distance"],
                    "時間": last_earthquake_data["time"],
                    "規模": last_earthquake_data["magnitude"],
                    "所在地區震度": last_earthquake_data["nowLocationIntensity"],
                }
                if not stop_event.is_set():
                    socketio.emit('earthquake_update_fake', result, to=sid)
    except Exception as e:
        print(f"Error during message handling: {e}")


def register_socketio_events(socketio):
    @socketio.on('connect')
    def handle_connect():
        print(f'Client {request.sid} connected')
    @socketio.on('set_location_fake')
    def handle_set_location(data):
        """
        客戶端在連接後發送經緯度，綁定到 socket id。
        """
        try:
            userID = data.get('userID')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            sid = request.sid
            event_sid = sid + '2'
            stop_event = threading.Event()
            if event_sid in background_tasks:
                emit('error', {'message': 'You have connected it'}, to=sid)
                return
            if event_sid not in background_tasks and latitude is not None and longitude is not None:
                # 綁定經緯度到客戶端的 socket id
                print(f'Location set for {sid}: ({latitude}, {longitude})')
                background_task = socketio.start_background_task(
                    check_and_broadcast_updates_fake, socketio, sid, latitude, longitude, userID, stop_event)
                background_tasks[event_sid] = stop_event
                emit('registration_success', {
                     'message': 'Location registered successfully'}, to=sid)
            else:
                emit('error', {'message': 'Invalid location data'}, to=sid)
        except Exception as e:
            print(f"Error during message handling: {e}")
    @socketio.on('set_location')
    def handle_set_location(data):
        """
        客戶端在連接後發送經緯度，綁定到 socket id。
        """
        try:
            userID = data.get('userID')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            sid = request.sid
            event_sid = sid + '1'
            stop_event = threading.Event()
            if event_sid in background_tasks:
                emit('error', {'message': 'You have connected it'}, to=sid)
                return
            if event_sid not in background_tasks and latitude is not None and longitude is not None:
                # 綁定經緯度到客戶端的 socket id
                print(f'Location set for {sid}: ({latitude}, {longitude})')
                background_task = socketio.start_background_task(
                    check_and_broadcast_updates, socketio, sid, latitude, longitude, userID, stop_event)
                background_tasks[event_sid] = stop_event
                emit('registration_success', {
                     'message': 'Location registered successfully'}, to=sid)
            else:
                emit('error', {'message': 'Invalid location data'}, to=sid)
        except Exception as e:
            print(f"Error during message handling: {e}")

    @socketio.on('disconnect')
    def handle_disconnect():
        """
        當客戶端斷開連接時，移除它的 socket id 和位置資料。
        """
        try:
            sid1 = request.sid + '1'
            sid2 = request.sid + '2'
            stop_event1 = background_tasks.get(sid1)
            stop_event2 = background_tasks.get(sid2)
            if stop_event1:
                stop_event1.set()
                print(f'Client {request.sid} disconnected')
            if stop_event2:
                stop_event2.set()
                print(f'Client {request.sid} disconnected')
        except Exception as e:
            print(f"Error during message handling: {e}")
