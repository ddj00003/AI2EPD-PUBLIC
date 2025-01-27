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
        objetives['sleep'] = calculate_minutes(contract['sleep']['start'], contract['sleep']['end'])

    for key, content in contract['activity'].items():
        if content['start'] and content['end']:
            objetives['activity'] += calculate_minutes(content['start'], content['end'])
    
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


def obtain_activities(patient_data, date):
        
    previous_day = datetime.strptime(date, "%d/%m/%Y")

    #Get timestamp of previous day start and end
    previous_day_start = int(datetime(previous_day.year, previous_day.month, previous_day.day, 0, 0, 0).timestamp())
    previous_day_end = int(datetime(previous_day.year, previous_day.month, previous_day.day, 23, 59, 59).timestamp())

    #Get patient activities collection
    collection_name = "activities_house_" + str(patient_data['id_house'])
    patient_activities_collection = db.get_collection(collection_name)

    #Get last contract
    last_contract = contract_helper(contract_collection.find_one({'id_patient' : patient_data['id_patient']}, sort=[('$natural', pymongo.DESCENDING)]))
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
            {'id_beacon': patient_data['id_beacon']},
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
        
