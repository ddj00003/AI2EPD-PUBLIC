from django.http import FileResponse, HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.template.defaulttags import register
import os
import pandas as pd
from . import db
from . import helpers
from typing import Any, Dict

#This funcion enable to use get method of a dictionary in a template
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

#This function is called when the user click on the download button in the summary template
#Takes the request and the id of the patient as parameters
#Returns a csv file with the activities of the patient
def file_download(request, id : int) -> FileResponse | None:
    patient = db.patient_collection.find_one({"id_patient": id})
    date_start = request.GET.get('start_date')
    date_end = request.GET.get('end_date')
    activity = request.GET.get('activity')

    result = db.search_data_download(patient["id_house"], patient["id_beacon"], date_start, date_end, activity)
    result_list = []
    df_columns = []

    if activity == 'exercise':
        result_list = [helpers.activity_helper_exercise(r) for r in result]
        df_columns = ['Actividad', 'Inicio', 'Fin', 'Duración', 'Pasos']

    elif  activity == 'sleep':
        result = result[0]
        result_list = [helpers.activity_helper(r) for r in result]
        df_columns = ['Actividad', 'Inicio', 'Fin', 'Duración']

    elif activity == "eat":
        result = result[1]
        result_list = [helpers.activity_helper(r) for r in result]
        df_columns = ['Actividad', 'Inicio', 'Fin', 'Duración']

    elif activity == "brush_teeth":
        result = result[2]
        result_list = [helpers.activity_helper(r) for r in result]
        df_columns = ['Actividad', 'Inicio', 'Fin', 'Duración']
    
    else:
        result_list = [helpers.activity_helper(r) for r in result]
        df_columns = ['Actividad', 'Inicio', 'Fin', 'Duración']

    if not result_list:
        return None

    filename = f'Actividades_{patient["name"]}_{patient["surname"]}_{activity}_{date_start}_{date_end}.csv'
    df = pd.DataFrame(result_list, columns=df_columns)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={filename}; charset=utf-8-sig'
    df.to_csv(path_or_buf=response, sep=';', index=False, encoding='utf-8')
    return response

#Returns the patient object or None if the patient does not exist
def get_patient(id : int) -> Dict[str, Any] | None:
    patient = db.patient_collection.find_one({"id_patient": id})
    if patient is not None:
        patient = helpers.patient_helper(patient)

    return patient

#This is the function that is called when the user use the custom filter in the summary template
#Takes the summarys as a parameter
#It returns a json with the summary of the patient, gruoped by contract
def custom_summary(results : list) -> Dict[str, Any]:
    summary = {}
    ndays = {}
    for r in results:
        id_contract = r["id_contract"]
        aux = helpers.contract_helper_custom(r)
        if id_contract not in summary:
            summary[id_contract] = aux.copy()
            ndays[id_contract] = 1
        else:
            for key, value in aux.items():
                if key in ['shower', 'medication', 'eat', 'brush_teeth']:
                    summary[id_contract][key]["times"] += value["times"]
                else:
                    summary[id_contract][key]["minutes"] += value["minutes"]
                summary[id_contract][key]["percent"] += value["percent"]
            ndays[id_contract] += 1

    for key in summary:
        for key2, value2 in summary[key].items():
            if key2 in ['shower', 'medication', 'eat', 'brush_teeth']:
                if value2["times"] != 0:
                    value2["times"] = round((value2["times"] / ndays[key]),1)
            elif key2 in ['sleep', 'activity']:
                if value2["minutes"] != 0:
                    value2["minutes"] = int(value2["minutes"] / ndays[key])
            if value2["percent"] != 0:
                value2["percent"] = int(value2["percent"] / ndays[key])

    return summary

def check_patient(request, patient: None | Dict[str, Any]) -> None | HttpResponse:
    if patient is None:
        context = {
                    'error_code': 'Error 404 - Not Found',
                    'error_title': _('Elemento no encontrado'),
                    'error_description': _('El paciente no existe.'),
                }
        return render(request, 'doctorsApp/error.html', context=context)
    
def check_patient_0(request, patient: Dict[str, Any]) -> None | HttpResponse:
    if patient['id_patient'] == 0 and str(request.user.groups.all()[0]) == 'doctor':
        context ={
                    'error_code': 'Error 403 - Forbidden',
                    'error_title': _('No estás autorizado'),
                    'error_description': _('No puedes acceder a la información de este paciente.'),
                }
        return render(request, 'doctorsApp/error.html', context=context)
   