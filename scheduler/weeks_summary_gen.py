from utils import get_db_handle, get_datetime_utc_now
from datetime import datetime, timedelta
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
summary_weeks_collection = db.get_collection('summary_weeks')
summary_months_collection = db.get_collection('summary_months')
patient_collection = db.get_collection('users')

def get_start_and_end_date_from_calendar_week(year, calendar_week):       
    monday = datetime.strptime(f'{year}-{calendar_week}-1', "%Y-%W-%w")
    return monday.timestamp(), (monday + timedelta(days=7)).timestamp()

def contract_helper_custom(contract) -> dict:
    return {
        "shower": contract["shower"],
        "activity": contract["activity"],
        "sleep": contract["sleep"],
        "medication": contract["medication"],
        "eat": contract["eat"],
        "brush_teeth": contract["brush_teeth"]
    }

def generate_weeks_summary(week=None, year=None):
    """
    Generate weekly summaries of patient activities and store them in the database.

    If no week and year are specified, the function will use the previous week as the week to generate summary for.

    Args:
        week (int, optional): The week to generate a summary for. Defaults to None.
        year (int, optional): The year to generate a summary for. Defaults to None.

    Returns:
        None
    """

    # Get all patients
    patients = patient_collection.find()

    if week is None or year is None:
        # Get previous week
        year, week, day = (get_datetime_utc_now() - timedelta(weeks=1)).isocalendar()
    start_date, end_date = get_start_and_end_date_from_calendar_week(year, week)
    print(start_date, end_date)

    for patient in patients:
        results = list(summary_days_collection.find({"id_user": patient["id_patient"], "timestamp": {"$gte": start_date, "$lte": end_date}}))
        #print patient and results in the console
        print(patient["id_patient"], results)

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
            summary_week['date'] = str.join('-', [str(week) if week > 10 else "0" + str(week), str(year)])
            summary_week['id_patient'] = patient["id_patient"]
            summary_week['contract_data'] = summary
            summary_week['mean_percent'] = percent
            summary_week['timestamp'] = int((start_date + end_date) / 2)
            summary_week['version'] = 'test'
            summary_weeks_collection.insert_one(summary_week)


if __name__ == "__main__":

    summary_weeks_collection.delete_many({})
    
    year = 2023  # Año para el que se generarán los resúmenes
    start_date = datetime(2022, 12, 1)  # Fecha de inicio (1 de enero del año)
    end_date = datetime(year, 5, 30)  # Fecha de fin (31 de diciembre del año)

    current_date = start_date

    while current_date <= end_date:
        week_number = current_date.isocalendar()[1]  # Obtener el número de semana
        generate_weeks_summary(week=week_number, year=year)  # Generar resumen para la semana actual
        current_date += timedelta(days=7)  # Avanzar al siguiente domingo (inicio de la siguiente semana)


    
