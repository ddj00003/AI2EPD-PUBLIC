import threading
import pymongo
from pymongo.cursor import Cursor
from pymongo.collection import Collection
from typing import Any, Dict
from . import models
from . import db
import pandas as pd
from plotly.offline import plot
import datetime
import plotly.express as px
import concurrent.futures

def collect_sensor_data(name, sensors, collection, house_data):
    house_data[name]['sensors'] = {}
    for sensor in sensors:
        sensor_info = models.Sensor.dict_to_sensor(sensor)
        if sensor_info is not None:
            data = collection.find_one({'id_sensor': sensor_info.id}, sort=[('$natural', pymongo.DESCENDING)])
            if data is not None:
                house_data[name]['sensors'][sensor_info.name] = sensor_info.get_data(data)
            else:
                house_data[name]['sensors'][sensor_info.name] = None

def collect_anchor_data(name, anchors, wristbands, collection, house_data):
    house_data[name]['anchors'] = {}
    for anchor in anchors:
        anchor_info = models.Anchor.dict_to_anchor(anchor)
        if anchor_info is not None:
            house_data[name]['anchors'][anchor_info.name] = []
            for wristband in wristbands.__copy__():
                wristband_info = models.Wristband.dict_to_wristband(wristband)
                if wristband_info is not None:
                    data = collection.find_one({'id_anchor': anchor_info.id, 'id_beacon': wristband_info.id}, sort=[('$natural', pymongo.DESCENDING)])
                    if data is not None:
                        house_data[name]['anchors'][anchor_info.name].append(anchor_info.get_data(data))

def collect_wristband_data(name, wristbands, collection, house_data):
    house_data[name]['wristbands'] = {}
    for wristband in wristbands:
        wristband_info = models.Wristband.dict_to_wristband(wristband)
        if wristband_info is not None:
            data = collection.find_one({'id_beacon': wristband_info.id, "steps": {"$exists": True}}, sort=[('$natural', pymongo.DESCENDING)])
            if data is not None:
                house_data[name]['wristbands'][wristband_info.name] = wristband_info.get_data(data)
            else:
                house_data[name]['wristbands'][wristband_info.name] = None

def collect_data(name : str, sensors : Cursor, anchors : Cursor, wristbands : Cursor, collection : Collection, house_data : Dict[str, Any]):
    sensor_thread = threading.Thread(target=collect_sensor_data, args=(name, sensors, collection, house_data))
    sensor_thread.start()
    anchor_thread = threading.Thread(target=collect_anchor_data, args=(name, anchors, wristbands, collection, house_data))
    anchor_thread.start()
    wristband_thread = threading.Thread(target=collect_wristband_data, args=(name, wristbands, collection, house_data))
    wristband_thread.start()

    sensor_thread.join()
    anchor_thread.join()
    wristband_thread.join()

def search_data(collection, query, output_list, lock):
    data = list(collection.find(query, {'_id': 0, 'time_window': 0}))
    with lock:
        output_list.extend(data)



def process_rssi(id_house, wristbands, date_start, date_end, result_rssi):
    collection = db.get_collection('samples_house_' + str(id_house))
    for key, value in wristbands.items():
        aux = list(collection.find({'id_beacon': key, 'timestamp': {'$gte': date_start, '$lte': date_end}, 'rssi': {'$exists': True}},{'_id': 0, 'time_window': 0}))
        if len(aux) > 0:
            result_rssi.append(list(aux))

def process_humidity(id_house, date_start, date_end, result_humidity):
    collection = db.get_collection('samples_house_' + str(id_house))
    result_humidity.extend(list(collection.find({'timestamp': {'$gte': date_start, '$lte': date_end}, 'temperature': {'$exists': True}},{'_id': 0, 'time_window': 0})))

def process_state(id_house, date_start, date_end, result_state):
    collection = db.get_collection('samples_house_' + str(id_house))
    result_state.extend(list(collection.find({'timestamp': {'$gte': date_start, '$lte': date_end}, 'state': {'$exists': True}} ,{'_id': 0})))

def process_steps(id_house, date_start, date_end, wristbands, result_humidity, result, result_rssi):
    threads = []
    threads.append(threading.Thread(target=process_rssi, args=(id_house, wristbands, date_start, date_end, result_rssi)))
    threads.append(threading.Thread(target=process_humidity, args=(id_house, date_start, date_end, result_humidity)))
    threads.append(threading.Thread(target=process_state, args=(id_house, date_start, date_end, result)))
    for t in threads:
        t.start()

    # Wait for all the threads to finish
    for t in threads:
        t.join()

