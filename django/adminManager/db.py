from django.utils.translation import gettext_lazy as _
from utils import get_db_handle
from . import helpers
from dotenv import load_dotenv
from pathlib import Path
import os
import datetime
from .import models
from typing import Any, Dict
from pymongo.collection import Collection
from pymongo.cursor import Cursor

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(Path.joinpath(BASE_DIR, '.env'))

DBNAME = os.getenv('DBNAME')
DBHOST = os.getenv('DBHOST')
DBPORT = os.getenv('DBPORT')
DBUSER = os.getenv('DBUSER')
DBPASS = os.getenv('DBPASS')
DBAUTH = os.getenv('DBAUTH')
DBDEVELOP = os.getenv('DBDEVELOP')

db, client = get_db_handle(DBNAME, DBHOST, DBPORT, DBUSER, DBPASS, DBAUTH)
house_collection = db.get_collection('houses')
anchor_collection = db.get_collection('house_anchors')
wristband_collection = db.get_collection('house_beacons')
sensor_collection = db.get_collection('house_sensors')
users_collection = db.get_collection("users")
incidence_collection = db.get_collection("incidences")

filter = {"name": {"$regex": r"^samples_house.*"}}

filter_location = {"name": {"$regex": r"^location_house.*"}}

def find(collection : Collection, query : Dict[str, Any], limit : int = 10) -> Cursor:
    return collection.find(query).limit(limit)

def list_collections() -> list:
    return db.list_collection_names(filter=filter)

def get_collection(name : str) -> Collection:
    return db.get_collection(name)

def update_house(id : int , name : str, description : str, mac : str) -> None:
    house_collection.update_one({'_id': id}, {'$set': {'name': name, 'description': description, 'mac_node': mac}})

def update_wristband(id :int, id_house : int, name : str, description : str, mac : str) -> None:
    wristband_collection.update_one({'_id': id}, {'$set': {'id_house': id_house, 'name': name, 'description': description, 'mac': mac}})

def update_anchor(id : int , id_house: int, name : str, description : str, mac :str) -> None:
    anchor_collection.update_one({'_id': id}, {'$set': {'id_house': id_house, 'name': name, 'description': description, 'mac': mac}})

def update_sensor(id : int , id_house : int, name : str , description : str, mac : str, type : str) -> None:
    sensor_collection.update_one({'_id': id}, {'$set': {'id_house': id_house, 'name': name, 'description': description, 'type': type, 'ieee_address': mac}})

def add_house(house :Dict[str, Any]) -> str:
    last_house = house_collection.find_one(sort=[("_id", -1)])
    id = 1
    print(last_house)
    if last_house is not None:
        id = int(last_house["_id"] + 1)
    house_collection.insert_one({
        "_id": id,
        "name": house["name"],
        "description": house["description"],
        "mac_node": house["mac"]
    })
   
    return _('Vivienda añadida correctamente')

def delete_house(id : int) -> None:
    house_collection.delete_one({"_id": id})

def add_anchor(anchor : Dict[str, Any]) -> str:
    last_anchor = anchor_collection.find_one(sort=[("_id", -1)])
    id = 1
    if last_anchor is not None:
        id = int(last_anchor["_id"] + 1)
    try:
        anchor_collection.insert_one({
        "_id": id,
        "id_house": anchor["id_house"],
        "name": anchor["name"],
        "description": anchor["description"],
        "mac": anchor["mac"]
    })
    except Exception as e:
        return _('Error: Clave primaria duplicada')
    
    return _('Ancla añadida correctamente')

def delete_anchor(id : int) -> None:
    anchor_collection.delete_one({"_id": id})

def add_wristband(wristband : Dict[str, Any]) -> str:
    last_wristband = wristband_collection.find_one(sort=[("_id", -1)])
    id = 1
    if last_wristband is not None:
        id = int(last_wristband["_id"] + 1)

    try:
        wristband_collection.insert_one({
        "_id": id,
        "id_house": wristband["id_house"],
        "name": wristband["name"],
        "description": wristband["description"],
        "mac": wristband["mac"]
    })
    except Exception as e:
        return _('Error: Clave primaria duplicada')
    
    return _('Pulsera añadida correctamente')

def delete_wristband(id : int) -> None:
    wristband_collection.delete_one({"_id": id})

def add_sensor(sensor : Dict[str, Any]) -> str:
    last_sensor = sensor_collection.find_one(sort=[("_id", -1)])
    id = 1
    if last_sensor is not None:
        id = int(last_sensor["_id"] + 1)
    try:
        sensor_collection.insert_one({
        "_id": id,
        "id_house": sensor["id_house"],
        "name": sensor["name"],
        "description": sensor["description"],
        "ieee_address": sensor["ieee_address"],
        "type": sensor["type"]
    })
    except Exception as e:
        return _('Error: Clave primaria duplicada')
    
    return _('Sensor añadido correctamente')

def delete_sensor(id : int) -> None:
    sensor_collection.delete_one({"_id": id})

def getUser(username : str) -> Dict[str, Any] | None:
    user =  users_collection.find_one({"username": username})
    if user:
        return helpers.user_helper(user)

def create_user(username, hashed_password, disabled) -> bool:
    if not getUser(username):
        users_collection.insert_one({"username": username, "hashed_password": hashed_password, "disabled": disabled})
        return True
    return False

def get_list_houses() -> list:
    houses = []
    for house in house_collection.find():
        house_aux = models.House(house['_id'], house['name'], house['description'], house['mac_node'])
        if house_aux is not None:
            if house_aux.id is not None and house_aux.name is not None:
                " ".join([str(house_aux.id),house_aux.name])
                houses.append(((house_aux.id), " ".join([str(house_aux.id),house_aux.name])))
    return houses

def get_list_houses_edit() -> list:
    houses = []
    houses.extend(get_list_houses())
    return houses

def add_incidence(incidence : Dict[str, Any]) -> str:
    last_incidence= incidence_collection.find_one(sort=[("_id", -1)])
    id = 1
    if last_incidence is not None:
        id = int(last_incidence["_id"] + 1)

    start = datetime.datetime(incidence["date_start"].year, incidence["date_start"].month, incidence["date_start"].day).timestamp()
    end = datetime.datetime(incidence["date_end"].year, incidence["date_end"].month, incidence["date_end"].day).timestamp()

    try:
        incidence_collection.insert_one({
        "_id": id,
        "id_house": incidence["id_house"],
        "description": incidence["description"],
        "date_start": start,
        "date_end": end
    })
    except Exception as e:
        print(e)
        return _('Error: Clave primaria duplicada')
    
    return _('Incidencia añadida correctamente')

def delete_incidence(id : int) -> None:
    incidence_collection.delete_one({"_id": id})