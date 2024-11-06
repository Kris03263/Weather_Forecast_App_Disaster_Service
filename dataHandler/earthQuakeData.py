import requests
from .methodPack import haversine,setLocate

url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001?Authorization=CWA-3D385D45-EFD5-4BD3-9677-9100AD39A4A2&limit=10"
testData = [{
        "color": "testColor",
        "content": "這是初始化的地震",
        "depth": "100",
        "distance": "50",
        "intensity": [
            {
                "AreaDesc": "最大震度1級地區",
                "AreaIntensity": "1級",
                "CountyName": "臺北市、臺東縣、嘉義市、臺南市"
            },
            {
                "AreaDesc": "最大震度2級地區",
                "AreaIntensity": "2級",
                "CountyName": "臺中市、新北市、桃園市、新竹市、苗栗縣、彰化縣、雲林縣、嘉義縣"
            },
            {
                "AreaDesc": "最大震度3級地區",
                "AreaIntensity": "3級",
                "CountyName": "南投縣、新竹縣"
            },
            {
                "AreaDesc": "最大震度4級地區",
                "AreaIntensity": "4級",
                "CountyName": "花蓮縣、宜蘭縣"
            },
        ],
        "location": "花蓮縣政府東北方  31.8  公里 (位於臺灣東部海域)",
        "magnitude": "6.0",
        "nowLocationIntensity": "3級",
        "reportImg": "https://scweb.cwa.gov.tw/webdata/OLDEQ/202410/2024101421171650480_H.png",
        "shakeImg": "https://scweb.cwa.gov.tw/webdata/drawTrace/plotContour/2024/2024480i.png",
        "time": "2024-10-14 21:19:16"}]
def getEarthData2(lon,lat,city):
    return testData

def getEarthData(lon,lat,city):
    earthquakeData = requests.get(url,verify=False).json()["records"]["Earthquake"]
    resultData = []
    _city = city
    for i in range(len(earthquakeData)):
        shakeLon = earthquakeData[i]["EarthquakeInfo"]["Epicenter"]["EpicenterLongitude"]
        shakeLat = earthquakeData[i]["EarthquakeInfo"]["Epicenter"]["EpicenterLatitude"]
        intensity = []
        AreaIntensity = ""
        shakeArea = earthquakeData[i]["Intensity"]["ShakingArea"]
        for nowElement in shakeArea:
            if not -nowElement["AreaDesc"].find("最"):
                del nowElement["EqStation"]
                intensity.append(nowElement)
                if _city is None:
                    _city = setLocate(lat,lon)["city"]
                for name in nowElement["CountyName"].split('、'):
                    if name == _city:AreaIntensity = nowElement["AreaIntensity"]
            intensity = sorted(intensity, key=lambda x: int(x['AreaIntensity'][0]))

        resultData.append({
            "color":                earthquakeData[i]["ReportColor"],
            "content":              earthquakeData[i]["ReportContent"],
            "nowLocation":          _city,
            "reportImg":            earthquakeData[i]["ReportImageURI"],
            "shakeImg":             earthquakeData[i]["ShakemapImageURI"],
            "time":                 earthquakeData[i]["EarthquakeInfo"]["OriginTime"],
            "depth":                str(earthquakeData[i]["EarthquakeInfo"]["FocalDepth"]),
            "location":             earthquakeData[i]["EarthquakeInfo"]["Epicenter"]["Location"],
            "magnitude":            str(earthquakeData[i]["EarthquakeInfo"]["EarthquakeMagnitude"]["MagnitudeValue"]),
            "distance":             haversine(lat,lon,shakeLat,shakeLon),
            "intensity":            intensity,
            "nowLocationIntensity": AreaIntensity if AreaIntensity else "該地區未列入最大震度範圍"
        })
    return resultData
