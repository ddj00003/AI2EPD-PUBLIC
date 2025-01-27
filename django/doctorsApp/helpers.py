from datetime import datetime
from django.utils.translation import gettext_lazy as _
from typing import Any, Dict

activities ={ 
    'shower': 'Ducha',
    'exercise': 'Ejercicio',
    'brush_teeth': 'Cepillado',
    'eat': 'Comer',
    'take_medicine': 'Medicación',
    'sleep': 'Dormir',
    }

#Helper to get the data of a patient
def patient_helper(user) -> Dict[str, Any]:
    return {
        "id_patient": str(user["id_patient"]),
        "name": user["name"],
        "surname": user["surname"],
        "doctor_name": user["doctor_name"],
        "doctor_surname": user["doctor_surname"],
        "id_house": int(user["id_house"]),
        "id_beacon": int(user["id_beacon"]),
        "date_start": str(user["date_start"])
    }

#Helper to get the activity data
def activity_helper(activity) -> Dict[str, Any]:
    return{
        "Inicio": datetime.fromtimestamp(activity["start_timestamp"]).strftime("%d/%m/%Y, %H:%M:%S"),
        "Fin": datetime.fromtimestamp(activity["end_timestamp"]).strftime("%d/%m/%Y, %H:%M:%S"),
        "Actividad": str(activities[activity["activity"]]),
        "Duración": int((datetime.fromtimestamp(activity["end_timestamp"]) - datetime.fromtimestamp(activity["start_timestamp"])).total_seconds() / 60),
    }

def activity_helper_exercise(activity) -> Dict[str, Any]:
    return{
        "Inicio": datetime.fromtimestamp(activity["start_timestamp"]).strftime("%d/%m/%Y, %H:%M:%S"),
        "Fin": datetime.fromtimestamp(activity["end_timestamp"]).strftime("%d/%m/%Y, %H:%M:%S"),
        "Actividad": str(activities[activity["activity"]]),
        "Duración": int((datetime.fromtimestamp(activity["end_timestamp"]) - datetime.fromtimestamp(activity["start_timestamp"])).total_seconds() / 60),
        "Pasos": int(activity["steps"])
    }

#Helper to get the contract data
def contract_helper(contract) -> Dict[str, Any]:
    return {
        "id_patient": str(contract["id_patient"]),
        "t_start": datetime.fromtimestamp(contract["t-start"]).strftime("%d/%m/%Y, %H:%M:%S"),
        "t_end": datetime.fromtimestamp(contract["t-end"]).strftime("%d/%m/%Y, %H:%M:%S") \
             if contract['t-end'] != 0 else _("Vigente"),
        "modified_by": contract["modified_by"],
        "shower": contract["shower"],
        "activity": contract["activity"],
        "sleep": contract["sleep"],
        "medication": contract["medication"],
        "eat": contract["eat"],
        "brush_teeth": contract["brush_teeth"],
        "id": str(contract["id"])
    }

#Hleper to get the contract data to show in the contract form
def contract_helper_custom(contract) -> Dict[str, Any]:
    return {
        "shower": contract["shower"],
        "activity": contract["activity"],
        "sleep": contract["sleep"],
        "medication": contract["medication"],
        "eat": contract["eat"],
        "brush_teeth": contract["brush_teeth"],
    }

def incidence_helper(data) -> Dict[str, Any] | None:
    try:
        return {
            "id": int(data["_id"]),
            "date_start": datetime.fromtimestamp(data["date_start"]).strftime("%d/%m/%Y"),
            "date_end": datetime.fromtimestamp(data["date_end"]).strftime("%d/%m/%Y"),
            "id_house": str(data["id_house"]),
            "description": str(data["description"]),
        }
    except:
        return None