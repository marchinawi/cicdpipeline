import numbers
import requests
import configparser
from geopy.geocoders import Nominatim
from flask import Flask, render_template, request,abort,send_file
from datetime import datetime
import datetime
import calendar
import boto3
from boto3.session import Session
import os
import socket
from decimal import Decimal
global data_list
global todays_date
data_list = []
app = Flask(__name__)

@app.route('/')
def weather_dashboard():
    return render_template('home.html',id=socket.gethostname())
@app.route('/savadata')
def savedata():
    Access_KEY_ID = 'AKIAW57T7R35YOZUM4K3'
    Secret_KEY = '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'

    session = Session(aws_access_key_id=Access_KEY_ID,
                      aws_secret_access_key=Secret_KEY)

    dynamodb = session.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('test_table')
    table.put_item(
        Item={
            'location': data_list[33],
            'date' : str(data_list[34]),
            'day_temp C' : str(data_list[0]),
            'night_temp C' : str(data_list[1]),
            'humidity %' : str(data_list[2])
        }
    )
    print(data_list)
    return render_template('results.html',
                           location=data_list[33], country=data_list[32],
                           todays_date=data_list[34],
                           day_name0=data_list[3], day0=data_list[0], night0=data_list[1], humidity0=data_list[2],
                           day_name1=data_list[7], day1=data_list[4], night1=data_list[5], humidity1=data_list[6],
                           day_name2=data_list[11], day2=data_list[8], night2=data_list[9], humidity2=data_list[10],
                           day_name3=data_list[15], day3=data_list[12], night3=data_list[13], humidity3=data_list[14],
                           day_name4=data_list[19], day4=data_list[16], night4=data_list[17], humidity4=data_list[18],
                           day_name5=data_list[23], day5=data_list[20], night5=data_list[21], humidity5=data_list[22],
                           day_name6=data_list[27], day6=data_list[24], night6=data_list[25], humidity6=data_list[26],
                           day_name7=data_list[31], day7=data_list[28], night7=data_list[29], humidity7=data_list[30])
@app.route('/sky')
def sky():
    try:
        Access_KEY_ID = 'AKIAW57T7R35YOZUM4K3'
        Secret_KEY = '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'

        session = Session(aws_access_key_id=Access_KEY_ID,
                         aws_secret_access_key=Secret_KEY)
        s3 = session.resource('s3')
        bucket = 'marcspythonprojectbucket'

        my_bucket = s3.Bucket(bucket)
        for s3_files in my_bucket.objects.all():
                print(s3_files.key)
        s3 = boto3.client('s3')
        my_bucket.download_file('sky.jpeg','./sky.jpeg')
        return send_file('./sky.jpeg',as_attachment=True)
    finally:
        os.remove('./sky.jpeg')


@app.route('/results', methods=['POST'])
def render_results():
    """getting the city name and country from lat/long of the location"""
    location = request.form['location']
    address = str(location)
    geolocator = Nominatim(user_agent="Your_Name")
    location2 = geolocator.geocode(address)
    try:
        location_reverse = geolocator.reverse(str(location2.latitude) + "," + str(location2.longitude))
    except AttributeError:
        error_statement = "Can not find location, Try again"
        return render_template("errors.html",error_statement=error_statement)
    address_reverse = location_reverse.raw['address']
    country = address_reverse.get('country', '')

    """"getting api key"""
    api_key ="27b6d0044c6b90357f39d27471742272"

    """"getting all the weather data about the location that
    the user entered"""
    data = get_weather_result(location,api_key)
    location_temp_humidity= temp_humidity_list(data)

    """"todays date"""
    todays_date = datetime.date.today().strftime('%d/%m/%Y')

    """"creating an instance 8 times, once per day starting from today
    following sequence:
    temp during the day , temp during the night, humidity, name of the day"""
    data_list.clear()
    for i in range(8):
        all_data = weather(location_temp_humidity,i)
        data_list.append(round(all_data.day_temp,1))
        data_list.append(round(all_data.night_temp,1))
        data_list.append(all_data.humidity)
        data_list.append(all_data.day)
    data_list.append(country.capitalize())
    data_list.append(location.capitalize())
    data_list.append(todays_date)
    return render_template('results.html',
                           location=data_list[33], country=data_list[32],
                           todays_date=data_list[34],
                           day_name0=data_list[3] ,day0=data_list[0] ,night0=data_list[1] ,humidity0=data_list[2],
                           day_name1=data_list[7] ,day1=data_list[4] ,night1=data_list[5] ,humidity1=data_list[6],
                           day_name2=data_list[11],day2=data_list[8] ,night2=data_list[9] ,humidity2=data_list[10],
                           day_name3=data_list[15],day3=data_list[12],night3=data_list[13],humidity3=data_list[14],
                           day_name4=data_list[19],day4=data_list[16],night4=data_list[17],humidity4=data_list[18],
                           day_name5=data_list[23],day5=data_list[20],night5=data_list[21],humidity5=data_list[22],
                           day_name6=data_list[27],day6=data_list[24],night6=data_list[25],humidity6=data_list[26],
                           day_name7=data_list[31],day7=data_list[28],night7=data_list[29],humidity7=data_list[30])

""""gets api key from file config.ini"""
# def get_api_key():
#     config = configparser.ConfigParser()
#     config.read('config.ini')
#     return config['openweathermap']['api']


""""takes in location and api and return all the weather data in json format"""
def get_weather_result(location,api_key):
    address = str(location)
    geolocator = Nominatim(user_agent="Your_Name")
    location = geolocator.geocode(address)
    api_url = "https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&units=metric&exclude=hourly&appid={}".format(location.latitude,location.longitude,api_key)
    print(api_url)
    r = requests.get(api_url)
    return r.json()


""""this class is used to create objects that contains the
temp during the day/night, humidity and name of the day"""
class weather:
    todays_date = datetime.date.today().strftime('%d/%m/%Y')
    def __init__(self,data,num):
        self.num = num*3
        self.data =data
        self.day_temp = self.data[self.num]
        self.night_temp=self.data[self.num+1]
        self.humidity=self.data[self.num+2]
        self.day = get_day(num)

""""takes in data in json format and returns a list containing
temp in day,night and humidity"""
def temp_humidity_list(data):
    data_list = []
    for i in range(8):
        data_list.append(data["daily"][i]["temp"]["day"])
        data_list.append(data["daily"][i]["temp"]["night"])
        data_list.append(data["daily"][i]["humidity"])
    return data_list
""""is a function that returns the name of the day
"x" amounts from today. 0 being today 1 being tomorrow etc.."""
def get_day(num):
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=num)
    return (calendar.day_name[tomorrow.weekday()])



if __name__== '__main__':
    app.run(host='0.0.0.0',debug=True)

