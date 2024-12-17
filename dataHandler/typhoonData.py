import requests,json
from datetime import datetime,timedelta

url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/W-C0034-005?Authorization=CWA-3BEF89AA-6B46-445D-999F-DB043639E781"

def getTyphoonData():
    typhoonData = requests.get(url).json()["records"]["tropicalCyclones"]["tropicalCyclone"]
    resultData = []
    direction = None
    with open('direction.json') as f:direction = json.load(f)
    for element in typhoonData:
        for e in element["analysisData"]["fix"]:
            if e["movingPrediction"] :del e["movingPrediction"][1]
            else: e["movingPrediction"].append({"value": None,"lang": None})

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

            e["fixTime"] = (datetime.fromisoformat(e["fixTime"])).strftime("%Y-%m-%d %H:%M:%S")

        for i,e in enumerate(element["forecastData"]["fix"]):
            inittime = datetime.fromisoformat(e["initTime"])
            inittime += timedelta(hours=int(e["tau"]))

            del e["radiusOf70PercentProbability"],e["initTime"],e["tau"]
            if "stateTransfers" in e :del e["stateTransfers"][1]

            e.setdefault("stateTransfers",{"value": None, "lang": None})
            e.setdefault("circleOf15Ms",{ "radius": None })
            e.setdefault("circleOf25Ms",{ "radius": None })

            element["forecastData"]["fix"][i] = {**{"futureTime":str(inittime.strftime("%Y-%m-%d %H:%M:%S"))},**e,**{"chineseDirection":direction[e["movingDirection"]]}}
                
        resultData.append({
            "name":element["typhoonName"],
            "cname":element["cwaTyphoonName"],
            "pastPosition":element["analysisData"]["fix"],
            "futurePosition":element["forecastData"]["fix"]
        })
        
    return resultData