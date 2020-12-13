from flask import Flask, request
from flask import render_template
#from db import mysql
import requests
import json

app = Flask(__name__)
#db = mysql.Testdb()

def green_light_api_auto(radius = 2000, meals_time = 20):

    my_radius = radius
    my_meals_time = meals_time

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
    url_mid_google_place = "&radius=" + str(my_radius) + "&pagetoken="
    pagetoken = ""
    url_back_google_place = "&type=restaurant&key="
    key_google_place = "AIzaSyC-6broabl69bcgNIlIrHGXtRcwHO-i6fk"

    response_google_place = requests.get(url_front_google_place + url_loc_google_place
                                         + url_mid_google_place + pagetoken + url_back_google_place + key_google_place)
    store_cnt = len(response_google_place.json()["results"])
    db_list = {"my_information": {"lat": my_lat, "lng": my_lng, "radius": my_radius, "meals_time": my_meals_time},
               "result": []}

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

    i = 0
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

    is_many = True

    try:
        pagetoken = response_google_place.json()["next_page_token"]

    except KeyError:
        is_many = False

    i = i + 1
    pageNum = 1
    acc_store_cnt = store_cnt

    while is_many:

        response_google_place = requests.get(url_front_google_place + url_loc_google_place
                                             + url_mid_google_place + pagetoken + url_back_google_place + key_google_place)
        store_cnt = len(response_google_place.json()["results"])

        print("acc : " + str(acc_store_cnt))
        for j in range(0, store_cnt):

            store_info = {"index": 1, "name": "멕카", "placeID": "qwdpqjwdio", "lat": 36.0, "lng": 127.0, "open": -1, "close": -1,
                          "transit": 0000, "driving": 0000}

            store_info["index"] = j + acc_store_cnt
            store_info["name"] = response_google_place.json()["results"][j]["name"]
            store_info["placeID"] = response_google_place.json()["results"][j]["place_id"]
            store_info["lat"] = response_google_place.json()["results"][j]["geometry"]["location"]["lat"]
            store_info["lng"] = response_google_place.json()["results"][j]["geometry"]["location"]["lng"]

            url_back_naver_direction = "&goal="
            url_back_naver_direction = url_back_naver_direction + str(store_info["lng"]) + "," + str(store_info["lat"])
            url_back_naver_direction = url_back_naver_direction + "&option=trafast"

            url_back_google_direction = "&destination="
            url_back_google_direction = url_back_google_direction + str(store_info["lat"]) + "," + str(store_info["lng"])
            url_back_google_direction = url_back_google_direction + "&mode=transit&departure_time=now&key="
            url_back_google_direction = url_back_google_direction + key_google_place
            response_google_direction = requests.get(url_front_google_direction + url_back_google_direction)

            store_info["transit"] = response_google_direction.json()["routes"][0]["legs"][0]["duration"]["value"]


            #response_naver_direction = requests.get(url_naver_direction + url_back_naver_direction,
            #                                        headers=data_naver_direction)
            #store_info["driving"] = int(response_naver_direction.json()["route"]["trafast"][0]["summary"]["duration"]/1000)

            db_list["result"].append(store_info)

        try:
            pagetoken = response_google_place.json()["next_page_token"]

        except KeyError:
            is_many = False

        acc_store_cnt = acc_store_cnt + store_cnt
        pageNum = pageNum + 1

    #등록 되어 있는 음식점 정보 중 오픈시간, 마감시간
    for j in range(0, acc_store_cnt):
        response_google_details = requests.get(url_front_google_details + db_list["result"][j]["placeID"] +
                                               url_back_google_details + key_google_details)
        try:
            db_list["result"][j]["open"] = response_google_details.json()["result"]["opening_hours"]["periods"][1]["open"]["time"]
            db_list["result"][j]["close"] = response_google_details.json()["result"]["opening_hours"]["periods"][1]["close"]["time"]
        except:
            db_list["result"][j]["open"] = "-1"
            db_list["result"][j]["close"] = "-1"
    result_json = json.dumps(db_list, indent=3, ensure_ascii=False)

    return result_json

def green_light_api(lat = 0, lng = 0, radius = 2000, meals_time = 20):

    my_radius = radius
    my_meals_time = meals_time

    my_lat = lat  # 내 위치의 위도
    my_lng = lng  # 내 위치의 경도

    url_front_google_place = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="
    url_loc_google_place = str(my_lat) + "," + str(my_lng)
    url_mid_google_place = "&radius=" + str(my_radius) + "&pagetoken="
    pagetoken = ""
    url_back_google_place = "&type=restaurant&key="
    key_google_place = "AIzaSyC-6broabl69bcgNIlIrHGXtRcwHO-i6fk"

    response_google_place = requests.get(url_front_google_place + url_loc_google_place
                                         + url_mid_google_place + pagetoken + url_back_google_place + key_google_place)
    store_cnt = len(response_google_place.json()["results"])
    db_list = {"my_information": {"lat": my_lat, "lng": my_lng, "radius": my_radius, "meals_time": my_meals_time},
               "result": []}

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

    i = 0
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

        try:
            store_info["transit"] = response_google_direction.json()["routes"][0]["legs"][0]["duration"]["value"]

        except:
            store_info["transit"] = -1

        #response_naver_direction = requests.get(url_naver_direction + url_back_naver_direction,
        #                                        headers=data_naver_direction)
        #store_info["driving"] = int(response_naver_direction.json()["route"]["trafast"][0]["summary"]["duration"]/1000)

        db_list["result"].append(store_info)

    url_front_google_details = "https://maps.googleapis.com/maps/api/place/details/json?place_id="
    url_back_google_details = "&fields=name,rating,opening_hours,formatted_phone_number&key="
    key_google_details = "AIzaSyC-6broabl69bcgNIlIrHGXtRcwHO-i6fk"

    is_many = True

    try:
        pagetoken = response_google_place.json()["next_page_token"]

    except KeyError:
        is_many = False

    i = i + 1
    pageNum = 1
    acc_store_cnt = store_cnt

    while is_many:

        response_google_place = requests.get(url_front_google_place + url_loc_google_place
                                             + url_mid_google_place + pagetoken + url_back_google_place + key_google_place)
        store_cnt = len(response_google_place.json()["results"])

        print("acc : " + str(acc_store_cnt))
        for j in range(0, store_cnt):

            store_info = {"index": 1, "name": "멕카", "placeID": "qwdpqjwdio", "lat": 36.0, "lng": 127.0, "open": -1, "close": -1,
                          "transit": 0000, "driving": 0000}

            store_info["index"] = j + acc_store_cnt
            store_info["name"] = response_google_place.json()["results"][j]["name"]
            store_info["placeID"] = response_google_place.json()["results"][j]["place_id"]
            store_info["lat"] = response_google_place.json()["results"][j]["geometry"]["location"]["lat"]
            store_info["lng"] = response_google_place.json()["results"][j]["geometry"]["location"]["lng"]

            url_back_naver_direction = "&goal="
            url_back_naver_direction = url_back_naver_direction + str(store_info["lng"]) + "," + str(store_info["lat"])
            url_back_naver_direction = url_back_naver_direction + "&option=trafast"

            url_back_google_direction = "&destination="
            url_back_google_direction = url_back_google_direction + str(store_info["lat"]) + "," + str(store_info["lng"])
            url_back_google_direction = url_back_google_direction + "&mode=transit&departure_time=now&key="
            url_back_google_direction = url_back_google_direction + key_google_place
            response_google_direction = requests.get(url_front_google_direction + url_back_google_direction)

            store_info["transit"] = response_google_direction.json()["routes"][0]["legs"][0]["duration"]["value"]


            response_naver_direction = requests.get(url_naver_direction + url_back_naver_direction,
                                                    headers=data_naver_direction)
            store_info["driving"] = int(response_naver_direction.json()["route"]["trafast"][0]["summary"]["duration"]/1000)

            db_list["result"].append(store_info)

        try:
            pagetoken = response_google_place.json()["next_page_token"]

        except KeyError:
            is_many = False

        acc_store_cnt = acc_store_cnt + store_cnt
        pageNum = pageNum + 1

    #등록 되어 있는 음식점 정보 중 오픈시간, 마감시간
    for j in range(0, acc_store_cnt):
        response_google_details = requests.get(url_front_google_details + db_list["result"][j]["placeID"] +
                                               url_back_google_details + key_google_details)
        try:
            db_list["result"][j]["open"] = response_google_details.json()["result"]["opening_hours"]["periods"][1]["open"]["time"]
            db_list["result"][j]["close"] = response_google_details.json()["result"]["opening_hours"]["periods"][1]["close"]["time"]
        except:
            db_list["result"][j]["open"] = "-1"
            db_list["result"][j]["close"] = "-1"

    result_json = json.dumps(db_list, indent=3, ensure_ascii=False)

    return result_json

@app.route("/home")
def hello():

    """
    for i in range(0, store_cnt):
        print(db_list[i])
    print("음식점 수 : " + str(store_cnt))
    """
    #print(response_server_test.json()["result"][0])
    return render_template('index.html')

@app.route('/api/')
def get_html():
    my_auto_loc = request.args.get('auto', 0)
    my_lt = request.args.get('lat', 36.7657)
    my_ln = request.args.get('lng', 127.2873)
    my_rad = request.args.get('radius', 2000)
    my_meals_t = request.args.get('mealstime', 20)

    if(my_auto_loc == 1):
        return render_template('view.html', aa=green_light_api_auto(radius=my_rad, meals_time=my_meals_t))
    elif(my_auto_loc == 0):
        return render_template('view.html',
                               aa=green_light_api(lat=my_lt, lng=my_ln, radius=my_rad, meals_time=my_meals_t))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
    #app.run()

