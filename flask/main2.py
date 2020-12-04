from flask import Flask, request
from flask import render_template
#from db import mysql
import requests
import time
import json
import os
import ssl
import urllib.request


app = Flask(__name__)
#db = mysql.Testdb()

my_lat = 0.0 # 내 위치의 위도
my_lon = 0.0 # 내 위치의 경도

url_google_place = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=36.765696,127.2872959999999&radius=3000&type=restaurant&key="
key_google_place = "AIzaSyC-6broabl69bcgNIlIrHGXtRcwHO-i6fk"

response_google_place = requests.get(url_google_place + key_google_place)
store_cnt = len(response_google_place.json()["results"])
db_list = []

for i in range(0, store_cnt):
    store_info = [1, "멕카", "qwdpqjwdio", 36.0, 127.0, -1, -1, -1]
    store_info[0] = (i+1)
    store_info[1] = response_google_place.json()["results"][i]["name"]
    store_info[2] = response_google_place.json()["results"][i]["place_id"]
    store_info[3] = response_google_place.json()["results"][i]["geometry"]["location"]["lat"]
    store_info[4] = response_google_place.json()["results"][i]["geometry"]["location"]["lng"]
    db_list.append(store_info)

url_front_google_details = "https://maps.googleapis.com/maps/api/place/details/json?place_id="
url_back_google_details = "&fields=name,rating,opening_hours,formatted_phone_number&key="
key_google_details = "AIzaSyC-6broabl69bcgNIlIrHGXtRcwHO-i6fk"


for i in range(0, store_cnt):
    response_google_details = requests.get(url_front_google_details + db_list[i][2] + url_back_google_details + key_google_details)
    try:
        db_list[i][5] = response_google_details.json()["result"]["opening_hours"]["periods"][1]["open"]["time"]
        db_list[i][6] = response_google_details.json()["result"]["opening_hours"]["periods"][1]["close"]["time"]
    except:
        db_list[i][5] = "-1"
        db_list[i][6] = "-1"




##########################################################
for i in range(0, store_cnt):
    #print(db_list[i][3])
    #print(db_list[i][4])
    
    client = None
    with open("./google_key.json","r") as clientJson :
        client = json.load(clientJson)
    

    origin          = "37.5728359,126.9746922"
    destination     = str(db_list[i][3])+","+str(db_list[i][4])
    #destination     = "37.5129907,127.1005382"
    mode            = "transit"
    departure_time  = "now"
    key             = client["key"]

    url = "https://maps.googleapis.com/maps/api/directions/json?origin="+ origin \
            + "&destination=" + destination \
            + "&mode=" + mode \
            + "&departure_time=" + departure_time\
            + "&language=ko" \
            + "&key=" + key

    request         = urllib.request.Request(url)
    context         = ssl._create_unverified_context()
    response        = urllib.request.urlopen(request, context=context)
    responseText    = response.read().decode('utf-8')
    responseJson    = json.loads(responseText)

    with open("./Agent_Transit_Directions.json","w") as rltStream :
        json.dump(responseJson,rltStream)

    ###########################################################

    wholeDict = None
    with open("./Agent_Transit_Directions.json","r") as transitJson :
        wholeDict = dict(json.load(transitJson))

    path            = wholeDict["routes"][0]["legs"][0]
    duration_sec    = path["duration"]["value"]
    start_geo       = path["start_location"]
    end_geo         = path["end_location"]

    #print(duration_sec) # 전체 걸리는 시간을 초로 나타낸 것
    #print(start_geo)    # 출발지 위도,경도
    #print(end_geo)  # 도착지 위도,경도

    try:
        db_list[i][7] = round(duration_sec/60,1)
        
    except:
        db_list[i][7] = "-1"
        
"""
response_google_details = requests.get(url_front_google_details + db_list[4][2] + url_back_google_details + key_google_details)
db_list[4][5] = response_google_details.json()["result"]["opening_hours"]["periods"][1]["open"]["time"]
db_list[4][6] = response_google_details.json()["result"]["opening_hours"]["periods"][1]["close"]["time"]
"""

@app.route("/")
def hello():
    for i in range(0, store_cnt):
        print(db_list[i])
    print("음식점 수 : " + str(store_cnt))
    return render_template('map.html')

@app.route('/test')
def get_html():
   return render_template('view.html', aa ='전달데이터', bb="1234", cc =[1,2,3])

@app.route('/hello/<user>')
def hello_name(user):
   return render_template('view.html', data=user)

@app.route("/index")
def index():
    result = db.select_all()
    return render_template('index.html', aaa = str(result))

@app.route("/map", methods=['POST'])
def map():
    my_lat = request.form['test']
    print(my_lat)
    return my_lat

if __name__ == "__main__":
    app.run()