from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseNotAllowed
import datetime
import pymongo
from . import forms
from . import db
from . import helpers
from . import functions
from utils import date_utc, get_datetime_utc_now
from . decorators import allowed_users
from . logger_sin import log_exceptions



# Create your views here.

login_url_string='/login'

@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['doctor', 'admin'])
@log_exceptions
def main(request):
    date = get_datetime_utc_now()
    previous_date = (date - datetime.timedelta(days=1)).strftime('%d/%m/%Y')
    year, previous_week, day_of_week = (date -datetime.timedelta(weeks=1)).isocalendar()
    previous_week = f"{previous_week:02}-{year}" if previous_week < 10 else f"{previous_week}-{year}"
    previous_month = date.replace(day=1) - datetime.timedelta(days=1)
    previous_month = previous_month.strftime('%m/%Y')

    patients = []
    for patient in db.patient_collection.find():
        result = db.summary_days_collection.find_one({"id_user": patient["id_patient"]},
            projection={"mean_percent": True, "date":True}, sort=[('$natural', pymongo.DESCENDING)])
        result_week = db.summary_weeks_collection.find_one({"id_patient": patient["id_patient"]},
            projection={"mean_percent": True, "date":True}, sort=[('$natural', pymongo.DESCENDING)])
        result_month = db.summary_months_collection.find_one({"id_patient": patient["id_patient"]},
            projection={"mean_percent": True, "date":True}, sort=[('$natural', pymongo.DESCENDING)])

        if result :
            date = result["date"]
            if date == previous_date:
                patient["percentage"] = int(result["mean_percent"])
        if result_week:
            date = result_week["date"]
            if date == previous_week:
                patient["percentage_week"] = int(result_week["mean_percent"])
        if result_month:
            date = result_month["date"]
            if date == previous_month:
                patient["percentage_month"] = int(result_month["mean_percent"])

        if patient['id_patient'] == 0 and str(request.user.groups.all()[0]) == 'doctor':
            continue

        patients.append(patient)
    
    context = { 'patients': patients,
                'user': User.get_full_name(request.user),
                'group': str(request.user.groups.all()[0])
                }
    return render(request, 'doctorsApp/main.html', context = context)

@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['doctor', 'admin'])
@log_exceptions
def summary(request, id):
    patient = functions.get_patient(id)
    check_patient = functions.check_patient(request, patient)
    if check_patient is not None:
        return check_patient
    
    check_patient_0 = functions.check_patient_0(request, patient)
    if check_patient_0 is not None:
        return check_patient_0
    
    previous_date = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%d/%m/%Y')
    result = db.summary_days_collection.find_one({"id_user": id}, sort=[('$natural', pymongo.DESCENDING)])
    date = previous_date

    if not bool(result):
        result = None
    else:
        dateR = result["date"]
        if dateR != previous_date:
            result = None

    incidences_result = db.incidence_collection.find({'id_house': patient['id_house']}, sort=[('$natural', pymongo.DESCENDING)])
    incidences = []
    for incidence in incidences_result:
        incidence_h = helpers.incidence_helper(incidence)
        incidences.append(incidence_h)

    context = {
        'form': forms.DateForm(),
        'form_download': forms.DownloadSummary(),
        'form_custom': forms.CustomDateForm(),
        'incidences': incidences,
        'id_patient': id,
        'patient': patient,
        'result': result,
        'date': date,
        'user': User.get_full_name(request.user),
        'group': str(request.user.groups.all()[0])
    }
    return render(request, 'doctorsApp/summary.html', context=context)

@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['doctor', 'admin'])
@log_exceptions
def get_summary(request, id):
    patient = functions.get_patient(id)
    
    check_patient = functions.check_patient(request, patient)
    if check_patient is not None:
        return check_patient
    
    check_patient_0 = functions.check_patient_0(request, patient)
    if check_patient_0 is not None:
        return check_patient_0

    if request.method == 'POST':
        context = {
            'error_code': 'Error 405 - Method Not Allowed',
            'error_title': _('Método no permitido'),
            'error_description': _('El método POST no está permitido en esta página.'),
        }
        return render(request, 'doctorsApp/error.html', context=context)


    month = request.GET.get('month')
    week = request.GET.get('week')
    date = request.GET.get('date')

    fallback_year = request.GET.get('year-fallback')
    fallback_month = request.GET.get('month-fallback')
    fallback_week = request.GET.get('week-fallback')
    incidences_result = db.incidence_collection.find({'id_house': patient['id_house']}, sort=[('$natural', pymongo.DESCENDING)])
    incidences = []
    for incidence in incidences_result:
        incidence_h = helpers.incidence_helper(incidence)
        incidences.append(incidence_h)

    context = {}
    if date not in ['',None] or  week not in ['',None] or month not in ['',None] \
        or fallback_year not in ['',None] or fallback_month not in ['',None] or fallback_week not in ['',None]:
        context = {
            'form': forms.DateForm(),
            'form_download': forms.DownloadSummary(),
            'form_custom': forms.CustomDateForm(),
            'id_patient': id,
            'incidences': incidences,
            'patient': patient,
            'user': User.get_full_name(request.user),
            'group': str(request.user.groups.all()[0])
         }

    if month not in ['',None]:
        try:
            date = datetime.datetime.strptime(month, '%Y-%m').strftime('%m/%Y')
        except Exception as e:
            context['error'] = _("Formato de fecha incorrecto")
            return render(request, 'doctorsApp/summary.html', context=context)

        result = db.summary_months_collection.find_one({"id_patient":id, "date": date})
        context['result']= result
        context['date']= date
        return render(request, 'doctorsApp/summary_month.html', context=context)
    
    elif  week not in ['',None]:
        try:
            week = week.replace('W','').split('-')
            week = str.join('-', [week[1],week[0]])
        except:
            context['error'] = _("Formato de fecha incorrecto")
            return render(request, 'doctorsApp/summary.html', context=context)

        result = db.summary_weeks_collection.find_one({"id_patient": id,"date":week})
        context['result']= result
        context['date']= week
        return render(request, 'doctorsApp/summary_week.html', context=context)

    elif fallback_year not in ['',None] and fallback_month not in ['',None]:
        date = str.join('-', [fallback_month, fallback_year])
        try:
            date = datetime.datetime.strptime(date, '%m-%Y').strftime('%m/%Y')
        except:
            context['error'] = _("Formato de fecha incorrecto")
            return render(request, 'doctorsApp/summary.html', context=context)
            
        result = db.summary_months_collection.find_one({"id_patient":id, "date": date})
        context['result']= result
        context['date']= date
        return render(request, 'doctorsApp/summary_month.html', context=context)
    
    elif fallback_year not in ['',None] and fallback_week not in ['',None]:
        week = str.join('-', [fallback_week, fallback_year])
        print(week)
        result = db.summary_weeks_collection.find_one({"id_patient": id,"date":week})
        context['result']= result
        context['date']= week
        return render(request, 'doctorsApp/summary_week.html', context=context)

    elif  date not in ['',None]:
        try:
            date = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        except:
            context['error'] = _("Formato de fecha incorrecto")
            return render(request, 'doctorsApp/summary.html', context=context)
        
        timestamp = int(datetime.datetime.strptime(date, '%d/%m/%Y').timestamp())

        result = db.summary_days_collection.find_one({"id_user": id, "date": date, "timestamp": {"$lte": timestamp}})
        context['result']= result
        context['date']= date
        return render(request, 'doctorsApp/summary.html', context=context)
    

    return redirect('doctorsApp:summary', id=id)

@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['doctor', 'admin'])
@log_exceptions
def get_summary_custom(request, id):
    patient = functions.get_patient(id)

    if request.method == 'POST':
        return HttpResponse("Solo se aceptan peticiones GET")
    
    check_patient = functions.check_patient(request, patient)
    if check_patient is not None:
        return check_patient
    
    check_patient_0 = functions.check_patient_0(request, patient)
    if check_patient_0 is not None:
        return check_patient_0

    date_start = request.GET.get('start_date')
    date_end = request.GET.get('end_date')


    if date_start not in ['',None] and date_end not in ['',None]:
        timestamp_start_ = int(datetime.datetime.strptime(date_start, '%Y-%m-%d').timestamp())
        timestamp_end = int(datetime.datetime.strptime(date_end, '%Y-%m-%d').timestamp())
        date_start = datetime.datetime.strptime(date_start, '%Y-%m-%d').strftime('%d/%m/%Y')
        date_end = datetime.datetime.strptime(date_end, '%Y-%m-%d').strftime('%d/%m/%Y')

        result = db.summary_days_collection.find({"id_user": id,"timestamp":{"$gte":timestamp_start_, "$lte":timestamp_end}})
        result_f ={}
        result_f['contract_data'] = functions.custom_summary(result)

        incidences_result = db.incidence_collection.find({'id_house': patient['id_house']}, sort=[('$natural', pymongo.DESCENDING)])
        incidences = []
        for incidence in incidences_result:
            incidence_h = helpers.incidence_helper(incidence)
            incidences.append(incidence_h)

        context = {
            'form': forms.DateForm(),
            'form_download': forms.DownloadSummary(),
            'form_custom': forms.CustomDateForm(),
            'id_patient': id,
            'patient': patient,
            'result': result_f,
            'incidences': incidences,
            'date_start': date_start,
            'date_end': date_end,
            'user': User.get_full_name(request.user),
            'group': str(request.user.groups.all()[0])
        }
        return render(request, 'doctorsApp/summary_custom.html', context=context)
    return redirect('doctorsApp:summary', id=id)

    
    
@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['doctor', 'admin'])
@log_exceptions
def download_summary(request, id):
    if request.method == 'POST':
        return HttpResponse("Solo se aceptan peticiones GET")

    result = functions.file_download(request, id)

    if result is None:
        return redirect('doctorsApp:summary', id=id)
    else:
        return result


@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['doctor', 'admin'])
@log_exceptions
def info_contract(request, id):
    patient = functions.get_patient(id)

    if request.method == 'POST':
        return HttpResponse("Solo se aceptan peticiones GET")
    
    check_patient = functions.check_patient(request, patient)
    if check_patient is not None:
        return check_patient
    
    check_patient_0 = functions.check_patient_0(request, patient)
    if check_patient_0 is not None:
        return check_patient_0

    contract_data = db.get_contract(id)
    if contract_data is None:
            context = {
                'id_patient': id,
                'patient': patient,
                'no_data': True,
                'user': User.get_full_name(request.user),
                'group': str(request.user.groups.all()[0])
            }
            return render(request, 'doctorsApp/info_contract.html', context=context)
    else:
        contract = helpers.contract_helper(contract_data)
    context = {
        'id_patient': id,
        'contract': contract,
        'patient': patient,
        'date': contract['t_start'],
        'nmodi': int(contract['id']),
        'id_contract': contract["id"],
        'user': User.get_full_name(request.user),
        'group': str(request.user.groups.all()[0])
    }
    return render(request, 'doctorsApp/info_contract.html', context=context)

@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['doctor', 'admin'])
@log_exceptions
def view_all_contracts(request, id):
    patient = functions.get_patient(id)

    if request.method == 'POST':
        return HttpResponse("Solo se aceptan peticiones GET")
    
    check_patient = functions.check_patient(request, patient)
    if check_patient is not None:
        return check_patient
    
    check_patient_0 = functions.check_patient_0(request, patient)
    if check_patient_0 is not None:
        return check_patient_0

    contracts = db.contract_collection.find({'id_patient': id}).sort("t-start", -1)
    contracts = list(contracts)
    contracts_modi = []
    for contract in contracts:
        contracts_modi.append(helpers.contract_helper(contract))

    context = {
        'id_patient': id,
        'contracts': contracts_modi,
        'patient': patient,
        'user': User.get_full_name(request.user),
        'group': str(request.user.groups.all()[0])
    }
    return render(request, 'doctorsApp/all_contracts.html', context=context)

@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['doctor', 'admin'])
@log_exceptions
def create_new_contract(request,id):
    if request.method == 'POST':
        return HttpResponse("Solo se aceptan peticiones GET")

    return redirect('doctorsApp:editContract', id=id)

@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['doctor', 'admin'])
@log_exceptions
def edit_contract(request, id):
    patient = functions.get_patient(id)

    if request.method == 'POST':
        return HttpResponse("Solo se aceptan peticiones GET")
    
    check_patient = functions.check_patient(request, patient)
    if check_patient is not None:
        return check_patient
    
    check_patient_0 = functions.check_patient_0(request, patient)
    if check_patient_0 is not None:
        return check_patient_0

    form_data = db.get_contract(id)
    if form_data is None:
        context = {
            'id_patient': id,
            'form': forms.TherapeuticContractV2(),
            'patient': patient,
            'user': User.get_full_name(request.user),
            'group': str(request.user.groups.all()[0])
        }
        return render(request, 'doctorsApp/edit_contract.html', context=context)
    
    initial_data = db.contract_initial_data_form(form_data)
    date = date_utc(form_data["t-start"],'%d/%m/%Y')
    context = {
        'id_patient': id,
        'form': forms.TherapeuticContractV2(initial=initial_data),
        'form_data': form_data,
        'patient': patient,
        'date': date,
        'user': User.get_full_name(request.user),
        'group': str(request.user.groups.all()[0])
    }
    return render(request, 'doctorsApp/edit_contract.html', context=context)   
      
@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['doctor', 'admin'])
@log_exceptions
def save_contract(request, id):
    patient = functions.get_patient(id)
    if patient is None:
        return HttpResponseNotFound(_("Elemento no encontrado"))

    if request.method == 'GET':
        return HttpResponseNotAllowed(['POST'])
    
    check_patient = functions.check_patient(request, patient)
    if check_patient is not None:
        return check_patient
    
    check_patient_0 = functions.check_patient_0(request, patient)
    if check_patient_0 is not None:
        return check_patient_0

    form = forms.TherapeuticContractV2(request.POST)
    if not form.is_valid():
        form_data = db.get_contract(id)
        initial_data = db.contract_initial_data_form(form_data)
        date = date_utc(form_data["t-start"],'%d/%m/%Y')
    
        context = {
            'id_patient': id,
            'form': forms.TherapeuticContractV2(initial=initial_data),
            'form_data': form_data,
            'patient': patient,
            'date': date,
            'error': _('Error al guardar los datos'),
            'user': User.get_full_name(request.user),
            'group': str(request.user.groups.all()[0])
        }
        return render(request, 'doctorsApp/edit_contract.html', context=context)

    validate = forms.therapeutic_validation(form.cleaned_data)
    if not validate:
        context = {
            'id_patient': id,
            'form': form,
            'patient': patient,
            'error': _('Error en los datos'),
            'user': User.get_full_name(request.user),
            'group': str(request.user.groups.all()[0])
        }
        return render(request, 'doctorsApp/edit_contract.html', context=context)

    db.add_contract(form.cleaned_data, id, User.get_full_name(request.user))
    return redirect('doctorsApp:infoContract', id=id)