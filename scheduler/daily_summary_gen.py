from utils import get_db_handle, get_datetime_utc_now
from datetime import datetime, timedelta
import pymongo
from dotenv import load_dotenv
from pathlib import Path
import json
import os

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(Path.joinpath(BASE_DIR, '.env'))

DBNAME = os.getenv('DBNAME')
DBDEVELOP = os.getenv('DBDEVELOP')
DBHOST = os.getenv('DBHOST')
DBPORT = os.getenv('DBPORT')
DBUSER = os.getenv('DBUSER')
DBPASS = os.getenv('DBPASS')
DBAUTH = os.getenv('DBAUTH')


#Times in minutes
#Between meals
TIME_BETWEEN_MEALS = 21600
#Tooth brushing after meals
TIME_TOOTHBRUSHING_AFTER_MEALS = 2700 
#Meals offset
MEAL_OFFSET = 1800


db, client = get_db_handle(DBNAME, DBHOST, DBPORT, DBUSER, DBPASS, DBAUTH)
summary_days_collection = db.get_collection('summary_days')
patient_collection = db.get_collection('users')
contract_collection = db.get_collection('therapeutic_contracts')

db2, client2 = get_db_handle(DBDEVELOP, DBHOST, DBPORT, DBUSER, DBPASS, DBAUTH)


def calculate_minutes(start, end):
    if not start or not end:
        return 0

    t1 = datetime.strptime(start, "%H:%M")
    t2 = datetime.strptime(end, "%H:%M")

    if t2 < t1:
        t1 -= timedelta(days=1)

    delta = t2 - t1

    return int(delta.total_seconds()/60)

def calculate_minutes_timestamp(start, end):
    if not start or not end:
        return 0

    t1 = datetime.fromtimestamp(start)
    t2 = datetime.fromtimestamp(end)

    if t2 < t1:
        t1 -= timedelta(days=1)

    delta = t2 - t1

    return int(delta.total_seconds()/60)

def calculate_objetives(contract):
    objetives= {
        'shower': 0,
        'activity': 0,
        'sleep': 0,
        'medication': 0,
        'eat': 0,
        'brush_teeth': 0
    }

    if contract['shower']['start'] and contract['shower']['end']:
        objetives['shower'] = 1

    if contract['sleep']['start'] and contract['sleep']['end']:
        objetives['sleep'] = 300

    for key, content in contract['activity'].items():
        if content['start'] and content['end']:
            objetives['activity'] = 60
    
    for key, content in contract['medication'].items():
        if content['start'] and content['end']:
            objetives['medication'] += 1
    
    for key, content in contract['eat'].items():
        if content['start'] and content['end']:
            objetives['eat'] += 1
    
    for key, content in contract['brush_teeth'].items():
        if content['start'] and content['end']:
            objetives['brush_teeth'] += 1

    return objetives

#Function to calculate the minutes of activity done in the day
def calculate_activity_minutes(activities):
    total_minutes = 0
    for activity in activities:
        start = datetime.fromtimestamp(activity['start_timestamp'])
        end = datetime.fromtimestamp(activity['end_timestamp'])
        delta = end - start
        total_minutes += int(delta.total_seconds()/60)
    return total_minutes

#Function to check that brush teeth has been done before 30
def check_brush_teeth_after_meal(ameals, abrush_teeth, aschedule):
    copy_abrush_teeth = abrush_teeth.copy()
    subset = []
    times_done = 0
    times_done_in_schedule = 0
    for meal in ameals:
        meal_end = datetime.fromtimestamp(meal['end_timestamp'])
        for activity in abrush_teeth.copy():
            brush_teeth = datetime.fromtimestamp(activity['start_timestamp'])
            delta = brush_teeth - meal_end
            if delta.total_seconds() > 0 and delta.total_seconds() <= TIME_TOOTHBRUSHING_AFTER_MEALS:
                subset.append(activity.copy())
                abrush_teeth.remove(activity)
                times_done += 1
                times_done_in_schedule += 1
                break
            
            if delta.total_seconds() > 0 and delta.total_seconds() <= TIME_TOOTHBRUSHING_AFTER_MEALS * 6:
                subset.append(activity.copy())
                abrush_teeth.remove(activity)
                times_done += 1
                break

    return times_done, times_done_in_schedule, subset

#datetime.datetime.strptime(meal['end_timestamp'], "%H:%M")

#Function to check that medication has been done in the correct time
def check_medication_in_schedule(amedication, aschedule):
    times_done = len(amedication)
    times_done_in_schedule = 0
    for key in aschedule:
        if not aschedule[key]['start'] or not aschedule[key]['end']:
            continue
        schedule_start = datetime.strptime(aschedule[key]['start'], "%H:%M")
        schedule_end = datetime.strptime(aschedule[key]['end'], "%H:%M")
        delta_activity = schedule_end - schedule_start
        for activity in amedication.copy():
            medication = datetime.fromtimestamp(activity['start_timestamp']).strftime("%H:%M")
            medication = datetime.strptime(medication, "%H:%M")
            delta = medication - schedule_start
            if delta.total_seconds() > 0 and delta.total_seconds() <= delta_activity.total_seconds():
                amedication.remove(activity)
                times_done_in_schedule += 1
                break

    return times_done, times_done_in_schedule

#Function to check that meals has been done
def check_meals_in_schedule(ameals, aschedule):
    times_done_in_schedule = 0
    times_done = 0
    subset = []
    for key in aschedule:
        if not aschedule[key]['start'] or not aschedule[key]['end']:
            continue
        schedule_start = datetime.strptime(aschedule[key]['start'], "%H:%M")
        schedule_end = datetime.strptime(aschedule[key]['end'], "%H:%M")
        delta_activity = schedule_end - schedule_start
        for activity in ameals.copy():
            watchdog = False
            meal_start = datetime.fromtimestamp(activity['start_timestamp']).strftime("%H:%M")
            meal_end = datetime.fromtimestamp(activity['end_timestamp']).strftime("%H:%M")
            meal_start = datetime.strptime(meal_start, "%H:%M")
            meal_end = datetime.strptime(meal_end, "%H:%M")

            if meal_start >= schedule_start and meal_start <= schedule_end:
                watchdog = True
                subset.append(activity.copy())
                ameals.remove(activity)
                times_done_in_schedule += 1
                times_done += 1
                break
            
            if meal_end >= schedule_start and meal_end <= schedule_end:
                watchdog = True
                subset.append(activity.copy())
                ameals.remove(activity)
                times_done_in_schedule += 1
                times_done += 1
                break

            if meal_start >= (schedule_start - timedelta(hours=1, minutes=30)) and meal_start <= (schedule_end + timedelta(hours=1, minutes=30)):
                watchdog = True
                subset.append(activity.copy())
                ameals.remove(activity)
                times_done += 1
                break
            
            if meal_end >= (schedule_start - timedelta(hours=1, minutes=30)) and meal_end <= (schedule_end + timedelta(hours=1, minutes=30)):
                watchdog = True
                subset.append(activity.copy())
                ameals.remove(activity)
                times_done += 1
                break
           
            #now add a tolereance of 1:30 hours to the start and end of the meal

            ''' meal = datetime.fromtimestamp(activity['start_timestamp']).strftime("%H:%M")
            meal = datetime.strptime(meal, "%H:%M")
            delta = meal - schedule_start
            if delta.total_seconds() > 0 and delta.total_seconds() <= delta_activity.total_seconds():
                watchdog = True
                subset.append(activity.copy())
                ameals.remove(activity)
                times_done_in_schedule += 1
                break
            # now check if the end of the meal is in the schedule
            meal = datetime.fromtimestamp(activity['end_timestamp']).strftime("%H:%M")
            meal = datetime.strptime(meal, "%H:%M")
            delta = meal - schedule_start
            if delta.total_seconds() > 0 and delta.total_seconds() <= delta_activity.total_seconds():
                watchdog = True
                subset.append(activity.copy())
                ameals.remove(activity)
                times_done_in_schedule += 1
                break

            '''
            if watchdog:
                break 

    return times_done, times_done_in_schedule, subset

def calculate_timetable(done_in_schedule, objetive, activity):
    if activity == 'medication':
        if done_in_schedule == 0:
            return 0
        if done_in_schedule == objetive:
            return 2
        return 1
    else:
        if done_in_schedule == 0:
            return 0
        if done_in_schedule >= objetive:
            return 2
        return 1

#Fuction
def contract_helper(contract) -> dict: 
    try:
        return {
            "shower": contract["shower"],
            "activity": contract["activity"],
            "sleep": contract["sleep"],
            "medication": contract["medication"],
            "eat": contract["eat"],
            "brush_teeth": contract["brush_teeth"],
            "id": str(contract["id"])
        }
    except Exception as e:
        return None

#Function to get the percentage of the activity done
def get_percentage_activity_done(activity, objetive):
    if objetive == 0:
        return 0
    percentage = int(round(( activity/ objetive) * 100, 1))
    if percentage > 100:
        percentage = 100
    return percentage

def generate_daily_summary_for_patient(patient, house, beacon, previous_day, previous_day_start, previous_day_end):
        '''
        Generates and saves the daily summary of activities for a given patient on a given day.

        Args:
            patient (int): The ID of the patient.
            previous_day (datetime.date): The date of the day for which the summary is generated.
            previous_day_start (datetime): The start timestamp of the previous_day.
            previous_day_end (datetime): The end timestamp of the previous_day.

        Returns:
            None. The summary is saved to the database.
        '''

        #Check if the patient has a summary for that day, and if so, exit
        summary_exits = summary_days_collection.find_one({'id_user' : patient, 'date' : previous_day.strftime("%d/%m/%Y")})
        if summary_exits is not None:
            print("Summary already exists, previous day: " + str(previous_day) + " patient: " + str(patient))
            return
    
        #Get patient activities collection
        collection_name = "activities_house_" + str(house)
        patient_activities_collection = db.get_collection(collection_name)

        #Get last contract
        last_contract = contract_helper(contract_collection.find_one({'id_patient' : patient}, sort=[('$natural', pymongo.DESCENDING)]))
        if last_contract is None:
            return
            
        # Get all activities of the patient in the previous day
        activities = list(patient_activities_collection.find({ 
            '$and': [
                {'start_timestamp': {'$gte': previous_day_start}},
                {'end_timestamp': {'$lte': previous_day_end}},
                {'id_beacon': beacon},
                {'activity': {'$ne': 'sleep'}},
                ]
            }))
        
        #Get timesatmp of the day at 15:00
        timestamp_15 = datetime.timestamp(datetime.combine(previous_day, datetime.min.time()) + timedelta(hours=15))
        #Get timesatmp of the day before at 20:00
        timestamp_20 = datetime.timestamp(datetime.combine(previous_day - timedelta(days=1), datetime.min.time()) + timedelta(hours=20))
        #Get the sleep activiity before 15:00 of the previous day and after 20:00 of the day before
        sleep_activities = list(patient_activities_collection.find({'activity': 'sleep', 'end_timestamp': {'$lte': timestamp_15}, 'start_timestamp': {'$gte': timestamp_20}}, sort=[('$natural', pymongo.DESCENDING)]))
        
        if not activities and not sleep_activities:
            print("No activities, previous day: " + str(previous_day) + ", house: " + str(house) + ", patient: " + str(patient))
            #save the string to a csv file
            with open('no_activities.csv', 'a') as f:
                if house not in [0,4]:
                    f.write("previous day: " + str(previous_day) + ", house: " + str(house) + ", patient: " + str(patient) + "\n")
            return
        else:
            print("Activities found, previous day: " + str(previous_day) + " patient: " + str(patient))

        #Calculate objetives
        objetives = calculate_objetives(last_contract)
       
        #Create the sublist of activities
        brush_teeth_activities = list(filter(lambda activity: activity['activity'] == 'brush_teeth', activities))
        take_medicine_activities = list(filter(lambda activity: activity['activity'] == 'take_medicine', activities))
        eat_activities = list(filter(lambda activity: activity['activity'] == 'eat', activities))
        shower_activity = list(filter(lambda activity: activity['activity'] == 'shower', activities))
        exersices_activities = list(filter(lambda activity: activity['activity'] == 'exercise', activities))

        #Calculate meals
        td_meals, tds_meals, subset_eats = check_meals_in_schedule(eat_activities, last_contract['eat'])
        meals_percent = get_percentage_activity_done(td_meals, objetives['eat'])

        #Calculate toothbrushing
        td_brush_teeth, tds_brush_teeth, _ = check_brush_teeth_after_meal(subset_eats, brush_teeth_activities, last_contract['brush_teeth'])
        brush_teeth_percent = get_percentage_activity_done(td_brush_teeth, objetives['brush_teeth'])

        #Calculate shower
        td_shower = 1 if shower_activity else 0
        shower_percent = get_percentage_activity_done(td_shower, objetives['shower'])

        #Calculate activity
        td_activity = calculate_activity_minutes(exersices_activities)
        activity_percent = get_percentage_activity_done(td_activity, objetives['activity'])

        #Calculate sleep
        td_sleep = calculate_activity_minutes(sleep_activities)
        sleep_percent = get_percentage_activity_done(td_sleep, objetives['sleep'])

        #Calculate medication
        td_medication, tds_medication = check_medication_in_schedule(take_medicine_activities, last_contract['medication'])
        medication_percent = get_percentage_activity_done(td_medication, objetives['medication'])

        #Create the summary
        summary = {
            'id_user': patient,
            'date': previous_day.strftime("%d/%m/%Y"),
            'timestamp': previous_day_start,
            'id_contract': last_contract['id'],
            'version': 'test_v2',
            'eat': {
                'times': 0 if objetives['eat'] == 0 else td_meals,
                'objetive': objetives['eat'],
                'percent': 0 if objetives['eat'] == 0 else meals_percent,
                'timetable': -1 if objetives['eat'] == 0 else calculate_timetable(tds_meals, objetives['eat'], 'eat')
            },
            'medication': {
                'times': 0 if objetives['medication'] == 0 else td_medication,
                'objetive': objetives['medication'],
                'percent': 0 if objetives['medication'] == 0 else medication_percent,
                'timetable': -1 if objetives['medication'] == 0 else calculate_timetable(tds_medication, objetives['medication'], 'medication')
            },
            'shower': {
                'times': 0 if objetives['shower'] == 0 else td_shower,
                'objetive': objetives['shower'],
                'percent': 0 if objetives['shower'] == 0 else shower_percent,
                'timetable': -1 if objetives['shower'] == 0 else 2 if td_shower > 0 else 0
            },
            'brush_teeth': {
                'times': 0 if objetives['brush_teeth'] == 0 else td_brush_teeth,
                'objetive': objetives['brush_teeth'],
                'percent':  0 if objetives['brush_teeth'] == 0 else brush_teeth_percent,
                'timetable': -1 if objetives['brush_teeth'] == 0 else calculate_timetable(tds_brush_teeth, objetives['brush_teeth'],'brush_teeth')
            },
            'sleep': {
                'minutes': 0 if objetives['sleep'] == 0 else td_sleep,
                'objetive': objetives['sleep'],
                'percent': 0 if objetives['sleep'] == 0 else sleep_percent,
                'timetable': -1 if objetives['sleep'] == 0 else 2 if td_sleep > 300 else 0
            },
            'activity': {
                'minutes': 0 if objetives['activity'] == 0 else td_activity,
                'objetive': objetives['activity'],
                'percent':  0 if objetives['activity'] == 0 else activity_percent,
                'timetable': -1 if objetives['activity'] == 0 else 2 if td_activity > 60 else 0
            }
        }

        summary['mean_percent'] = 0
        division_by = 0

        if summary['eat']['objetive'] != 0:
            summary['mean_percent'] += summary['eat']['percent']
            division_by += 1

        if summary['medication']['objetive'] != 0:
            summary['mean_percent'] += summary['medication']['percent']
            division_by += 1
        
        if summary['shower']['objetive'] != 0:
            summary['mean_percent'] += summary['shower']['percent']
            division_by += 1
        
        if summary['brush_teeth']['objetive'] != 0:
            summary['mean_percent'] += summary['brush_teeth']['percent']
            division_by += 1
        
        if summary['sleep']['objetive'] != 0:
            summary['mean_percent'] += summary['sleep']['percent']
            division_by += 1
        
        if summary['activity']['objetive'] != 0:
            summary['mean_percent'] += summary['activity']['percent']
            division_by += 1

        if division_by > 0:
            summary['mean_percent'] = summary['mean_percent'] / division_by

        #Insert the summary
        summary_days_collection.insert_one(summary)       


def obtain_activities(patient, house, beacon, previous_day, date):
        
    previous_day = datetime.strptime(date, "%d/%m/%Y")

    #Get timestamp of previous day start and end
    previous_day_start = int(datetime(previous_day.year, previous_day.month, previous_day.day, 0, 0, 0).timestamp())
    previous_day_end = int(datetime(previous_day.year, previous_day.month, previous_day.day, 23, 59, 59).timestamp())

    #Get patient activities collection
    collection_name = "activities_house_" + str(house)
    patient_activities_collection = db.get_collection(collection_name)

    #Get last contract
    last_contract = contract_helper(contract_collection.find_one({'id_patient' : patient}, sort=[('$natural', pymongo.DESCENDING)]))
    if last_contract is None:
        return
    
    sleep_activities = []
    brush_teeth_activities = []
    eat_activities = []
        
    # Get all activities of the patient in the previous day
    activities = list(patient_activities_collection.find({ 
        '$and': [
            {'start_timestamp': {'$gte': previous_day_start}},
            {'end_timestamp': {'$lte': previous_day_end}},
            {'id_beacon': beacon},
            {'activity': {'$ne': ['sleep', 'medication','exercise']}},
            ]
        }))
    
    #Get timesatmp of the day at 15:00
    timestamp_15 = datetime.timestamp(datetime.combine(previous_day, datetime.min.time()) + timedelta(hours=15))
    #Get timesatmp of the day before at 20:00
    timestamp_20 = datetime.timestamp(datetime.combine(previous_day - timedelta(days=1), datetime.min.time()) + timedelta(hours=20))
    #Get the sleep activiity before 15:00 of the previous day and after 20:00 of the day before
    sleep_activities = list(patient_activities_collection.find({'activity': 'sleep', 'end_timestamp': {'$lte': timestamp_15}, 'start_timestamp': {'$gte': timestamp_20}}, sort=[('$natural', pymongo.DESCENDING)]))

    #Calculate objetives
    objetives = calculate_objetives(last_contract)

    #Create the sublist of activities
    brush_teeth_activities = list(filter(lambda activity: activity['activity'] == 'brush_teeth', activities))
    eat_activities = list(filter(lambda activity: activity['activity'] == 'eat', activities))

    #Calculate meals
    td_meals, tds_meals, subset_eats = check_meals_in_schedule(eat_activities, last_contract['eat'])

    #Calculate toothbrushing
    td_brush_teeth, tds_brush_teeth, subset_tooth = check_brush_teeth_after_meal(subset_eats, brush_teeth_activities, last_contract['brush_teeth'])

    return sleep_activities, subset_eats, subset_tooth
        
    
def generate_daily_summary(date = None, patient = None):
    # Get all patients
    patients = patient_collection.find()

    previous_day = None

    # Get previous day
    if date is None:
        date = get_datetime_utc_now()
        previous_day = date - timedelta(days=1)
    else:
        previous_day = datetime.strptime(date, "%d/%m/%Y")

    #Get timestamp of previous day start and end
    previous_day_start = int(datetime(previous_day.year, previous_day.month, previous_day.day, 0, 0, 0).timestamp())
    previous_day_end = int(datetime(previous_day.year, previous_day.month, previous_day.day, 23, 59, 59).timestamp())

    if patient is not None:
        patient = patient_collection.find_one({'id_patient': patient})
        id_house = patient['id_house']
        beacon = patient['id_beacon']
        patient = patient['id_patient']
        generate_daily_summary_for_patient(patient, id_house, beacon, previous_day, previous_day_start, previous_day_end)
        
    else:
        for patient in patients:
            id_house = patient['id_house']
            beacon = patient['id_beacon']
            patient = patient['id_patient']
            generate_daily_summary_for_patient(patient, id_house, beacon, previous_day, previous_day_start, previous_day_end)

def parche():
    collection_name = "activities_house_3"
    patient_activities_collection = db2.get_collection(collection_name)
    for doc in patient_activities_collection.find():
        fecha_strs = doc['start_timestamp'] # Fecha en formato string
        fecha_strst = doc['end_timestamp'] # Fecha en formato string
        fecha_datetime = datetime.strptime(fecha_strs, '%Y-%m-%d %H:%M:%S') # Convertimos a datetime
        fecha_timestamp = fecha_datetime.timestamp() # Convertimos a timestamp
        fecha_datetimet = datetime.strptime(fecha_strst, '%Y-%m-%d %H:%M:%S') # Convertimos a datetime
        fecha_timestampt = fecha_datetimet.timestamp() # Convertimos a timestamp
        patient_activities_collection.update_one({'_id': doc['_id']}, {'$set': {'start_timestamp': fecha_timestamp, 'end_timestamp': fecha_timestampt}})

def parche_2():
    collection_name = "activities_house_3"
    patient_activities_collection = db2.get_collection(collection_name)
    for doc in patient_activities_collection.find({'activity': 'exercise'}):
        patient_activities_collection.update_many({'_id': doc['_id']}, {'$set': {'id_beacon': 4}})


def parche_3():
    collection_name = "activities_house_10"
    patient_activities_collection_dev = db2.get_collection(collection_name)
    patient_activities_collection = db.get_collection(collection_name)
    documentos_origen = patient_activities_collection_dev.find({"end_timestamp": {"$gt": 1677397680}})
    patient_activities_collection.insert_many(documentos_origen)

def parche_4():
    collection_name = "activities_house_10"
    patient_activities_collection = db.get_collection(collection_name)
    patient_activities_collection.delete_many({"activity": "take_medicine", "id_beacon": 13})

if __name__ == "__main__":

    start_date = datetime(2022, 12, 1)  # Fecha de inicio
    end_date = datetime(2023, 5, 28)    # Fecha de fin

    delta = timedelta(days=1)  # Diferencia entre cada fecha (1 día en este caso)
    current_date = start_date

    #summary_days_collection.delete_many({})  # Eliminar todos los resúmenes existentes

    while current_date <= end_date:
        generate_daily_summary(date=current_date.strftime("%d/%m/%Y"))  # Generar resumen para la fecha actual
        current_date += delta  # Avanzar al siguiente día
        
    #parche_4()