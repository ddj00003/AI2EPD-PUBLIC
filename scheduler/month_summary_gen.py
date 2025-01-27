from utils import get_db_handle, get_datetime_utc_now
import datetime
from dotenv import load_dotenv
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(Path.joinpath(BASE_DIR, '.env'))

DBNAME = os.getenv('DBNAME')
DBDEVNAME = os.getenv('DBDEVELOP')
DBHOST = os.getenv('DBHOST')
DBPORT = os.getenv('DBPORT')
DBUSER = os.getenv('DBUSER')
DBPASS = os.getenv('DBPASS')
DBAUTH = os.getenv('DBAUTH')


db, client = get_db_handle(DBNAME, DBHOST, DBPORT, DBUSER, DBPASS, DBAUTH)
summary_days_collection = db.get_collection('summary_days')
summary_months_collection = db.get_collection('summary_months')
patient_collection = db.get_collection('users')

def get_first_date_and_end_date_of_current_month(year, month):
  
    first_date = datetime.datetime(year, month, 1)
    if month == 12:
        last_date = datetime.datetime(year, month, 31)
    else:
        last_date = datetime.datetime(year, month + 1, 1) + datetime.timedelta(days=-1)
    
    return first_date.timestamp(), last_date.timestamp()


def contract_helper_custom(contract) -> dict:
    return {
        "shower": contract["shower"],
        "activity": contract["activity"],
        "sleep": contract["sleep"],
        "medication": contract["medication"],
        "eat": contract["eat"],
        "brush_teeth": contract["brush_teeth"]
    }

def generate_month_summary(month=None, year=None):

    # Get all patients
    patients = patient_collection.find()

    # Get previous month
    
    if month is None or year is None:
        date = get_datetime_utc_now()
        current_month =  date.month
        year = date.year
        month = current_month - 1
        if current_month == 1:
            month = 12
            year -= 1
    
    start_date, end_date = get_first_date_and_end_date_of_current_month(year, month)

    for patient in patients:
        results = list(summary_days_collection.find({"id_user": patient["id_patient"], "timestamp": {"$gte": start_date, "$lte": end_date}}))
        summary = {}
        ndays = {}
        percent = 0
        for r in results:
            aux = contract_helper_custom(r)
            percent += r["mean_percent"]
            id = str(r["id_contract"])
            if summary.get(id) is None:
                summary[id] = aux
                ndays[id] = 1
                summary[id]["mean_percent"] = r["mean_percent"]
            else:
                for key in aux:
                    if key in ['shower', 'medication', 'eat', 'brush_teeth']:
                        summary[id][key]["times"] += aux[key]["times"]
                    elif key in ['activity', 'sleep']:
                        summary[id][key]["minutes"] += aux[key]["minutes"]
                    summary[id][key]["percent"] += aux[key]["percent"]
                ndays[id] += 1

        for key in summary:
            for key2 in summary[key]:
                if key2 in ['shower', 'medication', 'eat', 'brush_teeth']:
                    if summary[key][key2]["percent"] != 0:
                        summary[key][key2]["percent"] = int(summary[key][key2]["percent"] / ndays[key])
                    if summary[key][key2]["times"] != 0:
                        summary[key][key2]["times"] = round(float(summary[key][key2]["times"] / ndays[key]),1)
                elif key2 in ['sleep','activity']:
                    if summary[key][key2]["percent"] != 0:
                        summary[key][key2]["percent"] = int(summary[key][key2]["percent"] / ndays[key])
                    if summary[key][key2]["minutes"] != 0:
                        summary[key][key2]["minutes"] = int(summary[key][key2]["minutes"] / ndays[key])
        if percent != 0:
            percent = int(percent / len(results))

        if len(results) != 0:
            summary_week = {}
            summary_week['date'] = str.join('/', [str(month) if month > 10 else "0" + str(month), str(year)])
            summary_week['id_patient'] = patient["id_patient"]
            summary_week['contract_data'] = summary
            summary_week['mean_percent'] = percent
            summary_week['version'] = 'test_v2'
            summary_months_collection.insert_one(summary_week)


if __name__ == "__main__":
    summary_months_collection.delete_many({})
    generate_month_summary(month=12, year=2022)
    generate_month_summary(month=1, year=2023)
    generate_month_summary(month=2, year=2023)
    generate_month_summary(month=3, year=2023)
    generate_month_summary(month=4, year=2023)
    generate_month_summary(month=5, year=2023)
   

    
            