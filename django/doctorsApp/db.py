from django.utils.translation import gettext_lazy as _
from utils import get_db_handle, timestamp_now
from decimal import Decimal
from bson.decimal128 import Decimal128
from dotenv import load_dotenv
from pathlib import Path
from pymongo.cursor import Cursor
from pymongo.collection import Collection
from typing import Any, Dict
from datetime import datetime, timedelta
from . activities_extractor import obtain_activities
import os

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(Path.joinpath(BASE_DIR, '.env'))

DBNAME = os.getenv('DBNAME')
DBHOST = os.getenv('DBHOST')
DBPORT = os.getenv('DBPORT')
DBUSER = os.getenv('DBUSER')
DBPASS = os.getenv('DBPASS')
DBAUTH = os.getenv('DBAUTH')
DBDEVELOP = os.getenv('DBDEVELOP')

db, client = get_db_handle( DBNAME, DBHOST, DBPORT, DBUSER, DBPASS, DBAUTH)
db2, client2 = get_db_handle( DBDEVELOP, DBHOST, DBPORT, DBUSER, DBPASS, DBAUTH)
contract_collection = db.get_collection('therapeutic_contracts')
summary_days_collection = db.get_collection('summary_days')
summary_weeks_collection = db.get_collection('summary_weeks')
summary_months_collection = db.get_collection('summary_months')
activities_collection = db.get_collection('activities')
develop_activities_collection = db2.get_collection('activities')
patient_collection = db.get_collection('users')
incidence_collection = db.get_collection("incidences")

def find(collection : Collection, query : Dict[str, Any], limit : int = 10) -> Cursor:
    return collection.find(query).limit(limit)

def convert_decimal(dict_item: Dict[str, Any]) -> Dict[str, Any] | None:
    if dict_item is None: return None

    for k, v in list(dict_item.items()):
        if isinstance(v, dict):
            convert_decimal(v)
        elif isinstance(v, list):
            for l in v:
                convert_decimal(l)
        elif isinstance(v, Decimal):
            dict_item[k] = Decimal128(str(v))

    return dict_item

def convert_to_srt_time(time : datetime) -> str | None:
    if time is not None:
        return time.strftime("%H:%M")
    else:
        return None

def close_connection() -> None:
    client.close()

def get_patient_id_house(id_house: int) -> Dict[str, Any]:
    return patient_collection.find_one({"id_house": int(id_house)})

def obtain_activities_ajusted(patient: Dict[str, Any], date_start: datetime, date_end: datetime) -> Cursor:
    collection = db.get_collection('activities_house_' + str(patient['id_house']))
    contract = contract_collection.find_one({"id_patient": patient['id']}, sort = [("t-start", -1)])

def search_data_download(id_home : int , id_beacon: int, date_start : str, date_end : str , activity : str) -> Cursor:
    collection = db.get_collection('activities_house_' + str(id_home))
    date_start = datetime.strptime(date_start, "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0)
    date_end = datetime.strptime(date_end, "%Y-%m-%d").replace(hour=23, minute=59, second=59, microsecond=0)
    
    if activity in ["shower", "exercise", "take_medicine"]:
        result = collection.find({
            "id_beacon": int(id_beacon),
            "start_timestamp": {"$gte": date_start.timestamp()},
            "end_timestamp": {"$lte": date_end.timestamp()},
            "activity": activity
        })
        return result
    else:

        start_date =  datetime.fromtimestamp(date_start.timestamp())
        end_date = datetime.fromtimestamp(date_end.timestamp())

        delta = timedelta(days=1)  # Diferencia entre cada fecha (1 día en este caso)
        current_date = start_date

        sleep_activities = []
        brush_teeth_activities = []
        eat_activities = []

        while current_date <= end_date:
            s, e, t = obtain_activities(get_patient_id_house(id_home), current_date.strftime("%d/%m/%Y"))
            current_date += delta  # Avanzar al siguiente día
            sleep_activities.extend(s)
            eat_activities.extend(e)
            brush_teeth_activities.extend(t)

        return [sleep_activities, eat_activities, brush_teeth_activities]
        
    

def add_contract(contract: Dict[str, Any], id : int, user : Dict[str, Any]) -> str:
    current_contract = contract_collection.find_one({"id_patient": id}, sort = [("t-start", -1)])
    date = timestamp_now()
    if current_contract is not None:
        contract_collection.update_one({"_id": current_contract["_id"]}, {"$set": {"t-end": int(date)}})

    contract_collection.insert_one({
        "id_patient": int(id),
        "id": int(current_contract["id"] + 1) if current_contract is not None else 1,
        "t-start": int(date),
        "t-end": int(0),
        "shower": {
            "start": convert_to_srt_time(contract['shower_s']),
            "end": convert_to_srt_time(contract['shower_e'])
        },
        "activity": {
            "morning": {
                "start": convert_to_srt_time(contract['activity_morning_s']),
                "end": convert_to_srt_time(contract['activity_morning_e'])
            },
            "afternoon": {
                "start": convert_to_srt_time(contract['activity_afternoon_s']),
                "end": convert_to_srt_time(contract['activity_afternoon_e'])
            },
        },
        "sleep": {
            "start": convert_to_srt_time(contract['sleep_s']),
            "end": convert_to_srt_time(contract['sleep_e'])
        },
        "medication": {
            "med_1": {
                "start": convert_to_srt_time(contract['medication_1_s']),
                "end": convert_to_srt_time(contract['medication_1_e'])
            },
            "med_2": {
                "start": convert_to_srt_time(contract['medication_2_s']),
                "end": convert_to_srt_time(contract['medication_2_e'])
            },
            "med_3": {
                "start": convert_to_srt_time(contract['medication_3_s']),
                "end": convert_to_srt_time(contract['medication_3_e'])
            },
        },
        "eat": {
            "meal_1": {
                "start": convert_to_srt_time(contract['eat_1_s']),
                "end": convert_to_srt_time(contract['eat_1_e'])
            },
            "meal_2": {
                "start": convert_to_srt_time(contract['eat_2_s']),
                "end": convert_to_srt_time(contract['eat_2_e'])
            },
            "meal_3": {
                "start": convert_to_srt_time(contract['eat_3_s']),
                "end": convert_to_srt_time(contract['eat_3_e'])
            },
            "meal_4": {
                "start": convert_to_srt_time(contract['eat_4_s']),
                "end": convert_to_srt_time(contract['eat_4_e'])
            },
            "meal_5": {
                "start": convert_to_srt_time(contract['eat_5_s']),
                "end": convert_to_srt_time(contract['eat_5_e'])
            },
            "meal_6": {
                "start": convert_to_srt_time(contract['eat_6_s']),
                "end": convert_to_srt_time(contract['eat_6_e'])
            },
        },
        "brush_teeth": {
            "brushing_1": {
                "start": convert_to_srt_time(contract['brush_teeth_1_s']),
                "end": convert_to_srt_time(contract['brush_teeth_1_e'])
            },
            "brushing_2": {
                "start": convert_to_srt_time(contract['brush_teeth_2_s']),
                "end": convert_to_srt_time(contract['brush_teeth_2_e'])
            },
            "brushing_3": {
                "start": convert_to_srt_time(contract['brush_teeth_3_s']),
                "end": convert_to_srt_time(contract['brush_teeth_3_e'])
            },
        },
        "modified_by": user
    })
    
    
    return _("Contrato añadido correctamente")

def get_contract(id : int) -> Dict[str, Any] | None:
    return contract_collection.find_one({"id_patient": id}, sort = [("t-start", -1)])

def get_threrapeutic_results_days(id : int) -> Dict[str, Any] | None:
    return summary_days_collection.find_one({"id_user": id})

def contract_initial_data_form(contract : Dict[str, Any]) -> Dict[str, Any]:
    initial_dict = {
        "shower_s": contract['shower']['start'],
        "shower_e": contract['shower']['end'],
        "activity_morning_s": contract['activity']['morning']['start'],
        "activity_morning_e": contract['activity']['morning']['end'],
        "activity_afternoon_s": contract['activity']['afternoon']['start'],
        "activity_afternoon_e": contract['activity']['afternoon']['end'],
        "sleep_s": contract['sleep']['start'],
        "sleep_e": contract['sleep']['end'],
        "medication_1_s": contract['medication']['med_1']['start'],
        "medication_1_e": contract['medication']['med_1']['end'],
        "medication_2_s": contract['medication']['med_2']['start'],
        "medication_2_e": contract['medication']['med_2']['end'],
        "medication_3_s": contract['medication']['med_3']['start'],
        "medication_3_e": contract['medication']['med_3']['end'],
        "eat_1_s": contract['eat']['meal_1']['start'],
        "eat_1_e": contract['eat']['meal_1']['end'],
        "eat_2_s": contract['eat']['meal_2']['start'],
        "eat_2_e": contract['eat']['meal_2']['end'],
        "eat_3_s": contract['eat']['meal_3']['start'],
        "eat_3_e": contract['eat']['meal_3']['end'],
        "eat_4_s": contract['eat']['meal_4']['start'],
        "eat_4_e": contract['eat']['meal_4']['end'],
        "eat_5_s": contract['eat']['meal_5']['start'],
        "eat_5_e": contract['eat']['meal_5']['end'],
        "eat_6_s": contract['eat']['meal_6']['start'],
        "eat_6_e": contract['eat']['meal_6']['end'],
        "brush_teeth_1_s": contract['brush_teeth']['brushing_1']['start'],
        "brush_teeth_1_e": contract['brush_teeth']['brushing_1']['end'],
        "brush_teeth_2_s": contract['brush_teeth']['brushing_2']['start'],
        "brush_teeth_2_e": contract['brush_teeth']['brushing_2']['end'],
        "brush_teeth_3_s": contract['brush_teeth']['brushing_3']['start'],
        "brush_teeth_3_e": contract['brush_teeth']['brushing_3']['end']
    }

    return initial_dict

'''def contract_initial_data_form(contract):
    initial_dict = {}
    for key in initial_dict:
        parts = key.split("_")
        sub_dict = contract
        print(contract)
        for part in parts[:-1]:
            sub_dict = sub_dict[part]
        initial_dict[key] = sub_dict[parts[-1]]
    print(initial_dict)
    return initial_dict'''