import requests
from datetime import datetime,timedelta

url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/W-C0034-005?Authorization=CWA-3D385D45-EFD5-4BD3-9677-9100AD39A4A2"

def getTyphoonData():
    typhoonData = requests.get(url).json()["records"]["tropicalCyclones"]["tropicalCyclone"]
    resultData = []
    for element in typhoonData:
        for e in element["analysisData"]["fix"]:
            if e["movingPrediction"] :del e["movingPrediction"][1]
            else: 
                e["movingPrediction"].append(
                    {
                        "value": None,
                        "lang": None
                    }
                )
            e.setdefault("circleOf15Ms", {
                "radius": None,
                "quadrantRadii": {
                    "radius": [
                        { "value": None, "dir": None },
                        { "value": None, "dir": None },
                        { "value": None, "dir": None },
                        { "value": None, "dir": None }
                    ]
                }
            })
            e.setdefault("circleOf25Ms", {
                "radius": None,
                "quadrantRadii": {
                    "radius": [
                        { "value": None, "dir": None },
                        { "value": None, "dir": None },
                        { "value": None, "dir": None },
                        { "value": None, "dir": None }
                    ]
                }
            })
        for i,e in enumerate(element["forecastData"]["fix"]):
            del e["radiusOf70PercentProbability"]
            inittime = datetime.fromisoformat(e["initTime"])
            inittime += timedelta(hours=int(e["tau"]))
            del e["initTime"]
            del e["tau"]
            element["forecastData"]["fix"][i] = {**{"futureTime":str(inittime.strftime("%Y-%m-%d %H:%M:%S"))},**e}
                
        resultData.append({
            "name":element["typhoonName"],
            "cname":element["cwaTyphoonName"],
            "pastPosition":element["analysisData"]["fix"],
            "futurePosition":element["forecastData"]["fix"]
        })
        
    return resultData

print(getTyphoonData())