from flask import Flask, request
from flask import render_template
#from db import mysql
import requests
import json

app = Flask(__name__)
#db = mysql.Testdb()

my_lat = 0.0 # 내 위치의 위도
my_lng = 0.0 # 내 위치의 경도


#구글 api에서 현재 위치 위도와 경도 받아오기
url_geolocation = f'https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyC-6broabl69bcgNIlIrHGXtRcwHO-i6fk'
data_geolocation = {
    'considerIp': True,
}

response_geolocation = requests.post(url_geolocation, data_geolocation)
my_lat = response_geolocation.json()["location"]["lat"]
my_lng = response_geolocation.json()["location"]["lng"]

url_front_google_place = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="
url_loc_google_place = str(my_lat) + "," + str(my_lng)
url_back_google_place = "&radius=3000&type=restaurant&key="
key_google_place = "AIzaSyC-6broabl69bcgNIlIrHGXtRcwHO-i6fk"

response_google_place = requests.get(url_front_google_place + url_loc_google_place + url_back_google_place + key_google_place)
store_cnt = len(response_google_place.json()["results"])
db_list = {"result": []}

url_front_google_direction = "https://maps.googleapis.com/maps/api/directions/json?origin="
url_front_google_direction = url_front_google_direction + url_loc_google_place

#네이버 direction api로 자동차 소요시간(ms)
url_front_naver_direction = "https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving?start="
url_loc_naver_direction = str(my_lng) + "," + str(my_lat)

url_naver_direction = url_front_naver_direction + url_loc_naver_direction

data_naver_direction = {
    'X-NCP-APIGW-API-KEY-ID': "xf7h9usrza",
    'X-NCP-APIGW-API-KEY': "nJ7c2Mgd41KDy6yVLZRerzUkYhDuFTY5ZBqFQGWU"
}


#음식점 이름, 장소_id, 위도, 경도
for i in range(0, store_cnt):
    store_info = {"index": 1, "name": "멕카", "placeID": "qwdpqjwdio", "lat": 36.0, "lng": 127.0, "open": -1, "close": -1, "transit": 0000, "driving": 0000}
    store_info["index"] = i
    store_info["name"] = response_google_place.json()["results"][i]["name"]
    store_info["placeID"] = response_google_place.json()["results"][i]["place_id"]
    store_info["lat"] = response_google_place.json()["results"][i]["geometry"]["location"]["lat"]
    store_info["lng"] = response_google_place.json()["results"][i]["geometry"]["location"]["lng"]

    url_back_naver_direction = "&goal="
    url_back_naver_direction = url_back_naver_direction + str(store_info["lng"]) + "," + str(store_info["lat"])
    url_back_naver_direction = url_back_naver_direction + "&option=trafast"

    url_back_google_direction = "&destination="
    url_back_google_direction = url_back_google_direction + str(store_info["lat"]) + "," + str(store_info["lng"])
    url_back_google_direction = url_back_google_direction + "&mode=transit&departure_time=now&key="
    url_back_google_direction = url_back_google_direction + key_google_place
    response_google_direction = requests.get(url_front_google_direction + url_back_google_direction)

    store_info["transit"] = response_google_direction.json()["routes"][0]["legs"][0]["duration"]["value"]

    """
    response_naver_direction = requests.get(url_naver_direction + url_back_naver_direction,
                                            headers=data_naver_direction)
    store_info["driving"] = int(response_naver_direction.json()["route"]["trafast"][0]["summary"]["duration"]/1000)
    """
    db_list["result"].append(store_info)

url_front_google_details = "https://maps.googleapis.com/maps/api/place/details/json?place_id="
url_back_google_details = "&fields=name,rating,opening_hours,formatted_phone_number&key="
key_google_details = "AIzaSyC-6broabl69bcgNIlIrHGXtRcwHO-i6fk"


"""
#등록되어 있는 음식점 정보 중 오픈시간, 마감시간
for i in range(0, store_cnt):
    response_google_details = requests.get(url_front_google_details + db_list[i][2] + url_back_google_details + key_google_details)
    try:
        db_list[i][5] = response_google_details.json()["result"]["opening_hours"]["periods"][1]["open"]["time"]
        db_list[i][6] = response_google_details.json()["result"]["opening_hours"]["periods"][1]["close"]["time"]
    except:
        db_list[i][5] = "-1"
        db_list[i][6] = "-1"
"""
result_json = json.dumps(db_list, indent=3, ensure_ascii=False)

@app.route("/")
def hello():

    """
    for i in range(0, store_cnt):
        print(db_list[i])
    print("음식점 수 : " + str(store_cnt))
    """
    print(result_json)
    print(my_lat, my_lng)
    return render_template('index.html')

@app.route('/view')
def get_html():
    return render_template('view.html', aa=result_json)
   #return render_template('view.html', aa ='전달데이터', bb="1234", cc =[1,2,3])

@app.route('/hello/<user>')
def hello_name(user):
   return render_template('view.html', data=user)

@app.route("/index")
def index():
    return render_template('index.html', aaa = str(result))

@app.route("/map")
def map():
    return render_template('map.html', location_x = my_lat, location_y = my_lng)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")