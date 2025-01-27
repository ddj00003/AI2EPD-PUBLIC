#Program to check that the devices has sent data in the last hours
import pymongo
import datetime
import json
import os
from dotenv import load_dotenv
from pathlib import Path
from .email_sender import send_email
from pymongo import MongoClient

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(Path.joinpath(BASE_DIR, '.env'))

DBNAME = os.getenv('DBNAME')
DBHOST = os.getenv('DBHOST')
DBPORT = os.getenv('DBPORT')
DBUSER = os.getenv('DBUSER')
DBPASS = os.getenv('DBPASS')
DBAUTH = os.getenv('DBAUTH')
DBDEVELOP = os.getenv('DBDEVELOP')

def get_db_handle(db_name, host, port, username, password, auth_source):
    client = MongoClient(
        host=host,
        port=int(port),
        username=username,
        password=password,
        authSource=auth_source
    )
    return client[db_name], client

db, client = get_db_handle( DBNAME, DBHOST, DBPORT, DBUSER, DBPASS, DBAUTH)
house_collection = db.get_collection('houses')
anchor_collection = db.get_collection('house_anchors')
wristband_collection = db.get_collection('house_beacons')
sensor_collection = db.get_collection('house_sensors')

# List of houses to check
checklist = [ 
    2,3,4,7,9,10
]

hours_to_check ={
    'sensors': 24,
    'anchors': 0.25,
    'wristbands': 6
}

def get_diference(hours):
    return (datetime.datetime.now() - datetime.timedelta(hours=hours)).timestamp()

def get_date(timestamp, device):
    return str(device) + " offline, last data: " + str(datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'))

def check_devices():

    house_data = {}
    for houseid in checklist:
        
        collection = db.get_collection('samples_house_' + str(houseid))
        house = house_collection.find_one({'_id': houseid})

        if house is not None:

            name = house['name'].replace('_', ' ').title()
            sensors = sensor_collection.find({'id_house': houseid})
            anchors = anchor_collection.find({'id_house': houseid})
            wristbands = wristband_collection.find({'id_house': houseid})
            
            house_data[name] = {}
            house_data[name]['sensors'] = {}
            for sensor in sensors:
                sensor_info = sensor
                if sensor_info is not None:
                    data = collection.find_one({'id_sensor': sensor['_id']}, sort=[('$natural', pymongo.DESCENDING)])
                    if data is not None:
                        if data['timestamp'] < get_diference(hours_to_check['sensors']):
                            house_data[name]['sensors'][str(sensor_info['name'])] = get_date(data['timestamp'], "Sensor")
            
            if not house_data[name]['sensors']:
                del house_data[name]['sensors']
                       
                    
            house_data[name]['anchors'] = {}
            for anchor in anchors:
                anchor_info = anchor
                if anchor_info is not None:
                        data = collection.find_one({'id_anchor': anchor['_id']}, sort=[('$natural', pymongo.DESCENDING)])
                        if data is not None:
                            if data['timestamp'] < get_diference(hours_to_check['anchors']):
                                house_data[name]['anchors'][str(anchor_info['name'])] = get_date(data['timestamp'], "Anchor")

            if not house_data[name]['anchors']:
                del house_data[name]['anchors']

            
            house_data[name]['wristbands'] = {}
            for wristband in wristbands:
                wristband_info = wristband
                if wristband_info is not None:
                    data = collection.find_one({'id_beacon': wristband['_id']}, sort=[('$natural', pymongo.DESCENDING)])
                    if data is not None:
                        if data['timestamp'] < get_diference(hours_to_check['wristbands']):
                            house_data[name]['wristbands'][str(wristband_info['name'])] = get_date(data['timestamp'], "Wristband")
            
            if not house_data[name]['wristbands']:
                del house_data[name]['wristbands']

            
            if not house_data[name]:
                del house_data[name]

    send_email( message_text="The following devices are not reporting data to the platform: \n" 
               + json.dumps(house_data, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    check_devices()