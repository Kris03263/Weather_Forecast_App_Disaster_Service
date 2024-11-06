import requests

url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/W-C0034-005?Authorization=CWA-3D385D45-EFD5-4BD3-9677-9100AD39A4A2"

def getTyphoonData():
    typhoonData = requests.get(url).json()["records"]["tropicalCyclones"]["tropicalCyclone"]
    resultData = []
    for element in typhoonData:
        for e in element["analysisData"]["fix"]:
            if e["movingPrediction"] :del e["movingPrediction"][1]
            else: del e["movingPrediction"]
        resultData.append({
            "name":element["typhoonName"],
            "cname":element["cwaTyphoonName"],
            "pastPosition":element["analysisData"]["fix"],
            "futurePosition":element["forecastData"]["fix"]
        })
    return resultData

#print(getTyphoonData())