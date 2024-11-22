import requests
from .methodPack import haversine,setLocate

url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001?Authorization=CWA-3D385D45-EFD5-4BD3-9677-9100AD39A4A2&limit=10"
testData = [{
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
    }]
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
            "nowLocationIntensity": AreaIntensity if AreaIntensity else "該地區未列入最大震度範圍",
            "latitude":             shakeLat,
            "longitude":            shakeLon
        })
    return resultData
