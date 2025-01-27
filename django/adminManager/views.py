from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse, HttpResponseNotFound, FileResponse
from plotly.offline import plot
import datetime
import plotly.express as px
import pandas as pd
import pymongo
import time
import io
import zipfile
from . logger_sin import log_exceptions
from . decorators import allowed_users, timer
from . import helpers
from . import forms
from . import db
from . import models
from . import functions
# Create your views here.

login_url_string='/login'


@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['admin'])
@log_exceptions
def main(request):
    houses = []
    for house in db.house_collection.find() :
        house_h = models.House.dict_to_house(house)
        if house_h is not None:
            houses.append(house_h)
    wristbands = []
    for wristband in db.wristband_collection.find() :
        wristband_h = models.Wristband.dict_to_wristband(wristband)
        if wristband_h is not None:
            wristbands.append(wristband_h)
    anchors = []
    for anchor in db.anchor_collection.find() :
        anchor_h = models.Anchor.dict_to_anchor(anchor)
        if anchor_h is not None:
            anchors.append(anchor_h)
    sensors = []
    for sensor in db.sensor_collection.find() :
        sensor_h = models.Sensor.dict_to_sensor(sensor)
        if sensor_h is not None:
            sensors.append(sensor_h)

    context = { 'houses': houses,
                'wristbands': wristbands,
                'anchors': anchors,
                'sensors': sensors,
                'user': User.get_full_name(request.user),
                'group': str(request.user.groups.all()[0])
         }
    return render(request, 'adminManager/main.html', context)

@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['admin'])
@log_exceptions
def sensors(request):
    sensors = []
   
    if request.method == 'POST':
        form = forms.CreateNewSensor(request.POST)
        if form.is_valid():
            message = db.add_sensor(form.cleaned_data)

    for sensor in db.sensor_collection.find() :
        sensor_h = models.Sensor.dict_to_sensor(sensor)
        if sensor_h is not None:
            sensor_h.form= forms.CreateNewSensor(
                                        initial={   'type': sensor_h.type,
                                                    'id_house': sensor_h.id_house,
                                                    'name': sensor_h.name,
                                                    'description': sensor_h.description,
                                                    'ieee_address': sensor_h.ieee_address
                                                })
            sensors.append(sensor_h)

    context = { 'sensors': sensors,
                'form': forms.CreateNewSensor(),
                'user': User.get_full_name(request.user),
                'group': str(request.user.groups.all()[0])
                }
    return render(request, 'adminManager/sensors.html', context)

@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['admin'])
def delete_sensor(request, id):
    db.sensor_collection.delete_one({'_id': id})
    return redirect('adminManager:sensors')

@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['admin'])
@log_exceptions
def edit_sensor(request, id):

    if request.method == 'POST':
        form = forms.CreateNewSensor(request.POST)
        if form.is_valid():            
            id_house = form.cleaned_data['id_house']
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            type = form.cleaned_data['type']
            ieee_address = form.cleaned_data['ieee_address']

            if id_house not in ['',None] and name not in ['',None] and description not in ['',None] and type not in ['',None] and ieee_address not in ['',None]:
                db.update_sensor(id, id_house, name, description, ieee_address, type)

    return redirect('adminManager:sensors')
        
@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['admin'])
@log_exceptions
def anchors(request):
    anchors = []

    if request.method == 'POST':
        form = forms.CreateNewAnchor(request.POST)
        if form.is_valid():
            message = db.add_anchor(form.cleaned_data)

    for anchor in db.anchor_collection.find() :
        anchor_h = models.Anchor.dict_to_anchor(anchor)
        if anchor_h is not None:
            anchor_h.form = forms.CreateNewAnchor(
                                                initial={'id_house': anchor_h.id_house,
                                                         'name': anchor_h.name,
                                                         'description': anchor_h.description,
                                                         'mac': anchor_h.mac
                                                        })
            anchors.append(anchor_h)

    context = { 'anchors': anchors,
                'form': forms.CreateNewAnchor(),
                'user': User.get_full_name(request.user),
                'group': str(request.user.groups.all()[0])
             }
    return render(request, 'adminManager/anchors.html', context)

@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['admin'])
@log_exceptions
def delete_anchor(request, id):
    db.anchor_collection.delete_one({'_id': id})
    return redirect('adminManager:anchors')

@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['admin'])
@log_exceptions
def edit_anchor(request, id):

    if request.method == 'POST':
        form = forms.CreateNewAnchor(request.POST)
        if form.is_valid():
            id_house = form.cleaned_data['id_house']
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            mac = form.cleaned_data['mac']

            if id_house not in ['',None] and name not in ['',None] and description not in ['',None] and mac not in ['',None]:
                db.update_anchor(id, id_house, name, description, mac)
    
    return redirect('adminManager:anchors')

@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['admin'])
@log_exceptions
def wristbans(request):
    wristbands = []

    if request.method == 'POST':
        form = forms.CreateNewDevice(request.POST)
        if form.is_valid():
            message = db.add_wristband(form.cleaned_data)
           
    for wristband in db.wristband_collection.find() :
        wristband_h = models.Wristband.dict_to_wristband(wristband)
        if wristband_h is not None:
            wristband_h.form = forms.CreateNewDevice(
                                            initial={'id_house': wristband_h.id_house,
                                                     'name': wristband_h.name,
                                                     'description': wristband_h.description,
                                                     'mac': wristband_h.mac
                                                    })
            wristbands.append(wristband_h)

    context = { 'wristbands': wristbands,
                'form': forms.CreateNewDevice(), 
                'user': User.get_full_name(request.user),
                'group': str(request.user.groups.all()[0])
             }
    return render(request, 'adminManager/wristbands.html', context)

@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['admin'])
@log_exceptions
def delete_wristband(request, id):
    db.wristband_collection.delete_one({'_id': id})
    return redirect('adminManager:wristbands')

@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['admin'])
@log_exceptions
def edit_wristband(request, id):
    if request.method == 'POST':
        form = forms.CreateNewDevice(request.POST)
        if form.is_valid():
            id_house = form.cleaned_data['id_house']
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            mac = form.cleaned_data['mac']

            if id_house not in ['',None] and name not in ['',None] and description not in ['',None] and mac not in ['',None]:
                db.update_wristband(id, id_house, name, description, mac) 
    
    return redirect('adminManager:wristbands')

@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['admin'])
@log_exceptions
def houses(request):
    houses = []
    
    if request.method == 'POST':
        form = forms.CreateNewHouse(request.POST)
        if form.is_valid():
            message = db.add_house(form.cleaned_data)
            
    for house in db.house_collection.find() :
        house_h = models.House.dict_to_house(house)
        if house_h is not None:
            house_h.form = forms.CreateNewHouse(
                                                initial={   'name': house_h.name,
                                                            'description': house_h.description,
                                                            'mac': house_h.mac_node
                                                            
                                                        })
            houses.append(house_h)

    context = { 'houses': houses,
                'form': forms.CreateNewHouse(),
                'user': User.get_full_name(request.user),
                'group': str(request.user.groups.all()[0])
                }
    return render(request, 'adminManager/houses.html', context)

@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['admin'])
@log_exceptions
def delete_house(request, id):
    db.house_collection.delete_one({'_id': id})
    return redirect('adminManager:houses')

@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['admin'])
@log_exceptions
def edit_house(request, id):
    if request.method == 'POST':
        form = forms.CreateNewHouse(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            mac = form.cleaned_data['mac']

            if name not in ['', None] and description not in ['', None] and mac not in ['', None]:
                description = description
                db.update_house(id, name, description, mac)
        
    return redirect('adminManager:houses')
        
def register(request):
    if request.method == 'GET':
        return render(request, 'adminManager/register.html' ,{
            'form' : UserCreationForm
            })

    if request.POST["password1"].lstrip() != request.POST["password2"].lstrip():
        context = { "form" : forms.Register(), "error" : _('Las contraseñas no coinciden') }
        return render(request, 'adminManager/register.html', context)

    try:
        user = User.objects.create_user(
            request.POST["username"].lstrip(), password=request.POST["password1"].lstrip())
        user.save()
        login(request, user)
        return redirect('startPage:home')

    except IntegrityError:
        context = { "form" : forms.Register(), "error" : _('El nombre de usuario ya existe') }
        return render(request, 'adminManager/register.html', context)
    
@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['admin'])
@log_exceptions
@timer
def data_id(request, id = None):
    if id is None:
        id = db.house_collection.find_one(sort=[('_id', pymongo.ASCENDING)])['_id']
        return redirect('data/'+str(id))
    house_data = {}
    house = models.House.dict_to_house(db.house_collection.find_one(filter={'_id': id}))
    collection = db.get_collection('samples_house_' + str(id))
    if house is not None:
        name = house.name.replace('_', ' ').title()
        sensors = db.sensor_collection.find({'id_house': id})
        anchors = db.anchor_collection.find({'id_house': id})
        wristbands = db.wristband_collection.find({'id_house': id})
        
        house_data[name] = {}
        functions.collect_data(name, sensors, anchors, wristbands, collection, house_data)


    return render(request, 'adminManager/houseDataId.html',{
        'house_data': house_data,
        'form': forms.IdHouseData(),
        'id': id,
        'user': User.get_full_name(request.user),
        'group': str(request.user.groups.all()[0])
    } )

@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['admin'])
@log_exceptions
def data_id_post(request):
    if request.method == 'GET':
        id = request.GET.get('id_house')
        return redirect('adminManager:data_id',id=id)
    return redirect('adminManager:data_id')


@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['admin'])
@log_exceptions
def location_id(request, id = None):
    if id is None:
        id = db.house_collection.find_one(sort=[('_id', pymongo.ASCENDING)])['_id']
        return redirect('location/'+str(id))
    location_data = {}
    house = models.House.dict_to_house(db.house_collection.find_one(filter={'_id': id}))
    collection = db.get_collection('location_house_' + str(id))
    wristbands = db.wristband_collection.find({'id_house': id})
    if house is not None:
        for wristband in wristbands:
            wristband_info = models.Wristband.dict_to_wristband(wristband)
            if wristband_info is not None:
                name = wristband_info.description
                id = wristband_info.id
                locations = collection.find({"id_beacon": id}).sort('$natural', pymongo.DESCENDING).limit(600)
                data =[]
                for location in locations:
                    location_info = helpers.location_helper(location)
                    if location_info is not None:
                        data.append(location_info)

                if len(data) == 0:
                    location_data[name] = None
                    continue
                df = pd.DataFrame(data)
                fig = px.scatter(df, x='date', y='location', color='location', hover_data=['date', 'location'])
                plot_div = plot(fig, output_type='div', include_plotlyjs='cdn', include_mathjax=False)
                location_data[name] = plot_div
                
    return render(request, 'adminManager/locations.html',{
        'location_data': location_data,
        'form': forms.IdHouseData(),
        'id': id,
        'user': User.get_full_name(request.user),
        'group': str(request.user.groups.all()[0])
    } )

@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['admin'])
@log_exceptions
def location_id_post(request):
    if request.method == 'GET':
        id = request.GET.get('id_house')
        return redirect('adminManager:location_id',id=id)
    return redirect('adminManager:location_id')

@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['admin'])
@log_exceptions
@timer
def data_charts(request):
    if request.method == 'POST':
        return HttpResponse("Solo se aceptan peticiones GET")

    date = request.GET.get('date')
    id_house = request.GET.get('id_house')

    plot_div = None
    plot_div_2 = []
    plot_div_3 = None

    search_params = {}
    search_params_string = ''

    sensors = {}
    anchors = {}
    wristbands = {}
    
    if date not in ['',None] and id_house not in ['',None]:
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        search_params['date'] = date
        date_start = datetime.datetime(date.year, date.month, date.day, 0, 0, 0).timestamp()
        search_params['timestamp_start'] = date_start
        date_end = datetime.datetime(date.year, date.month, date.day, 23, 59, 59).timestamp()
        search_params['timestamp_end'] = date_end

        search_params['sensors'] = 0
        search_params['anchors'] = 0
        search_params['wristbands'] = 0
        
        for sensor in db.sensor_collection.find({'id_house': int(id_house)}):
            search_params['sensors'] += 1
            sensors[sensor['_id']] = sensor['name']
        
        for anchor in db.anchor_collection.find({'id_house': int(id_house)}):
            search_params['anchors'] += 1
            anchors[anchor['_id']] = anchor['name']
        
        for wristband in db.wristband_collection.find({'id_house': int(id_house)}):
            search_params['wristbands'] += 1
            wristbands[wristband['_id']] = wristband['name']

        start_time = time.time()
        result_humidity = []
        result_rssi = []
        result = []
        functions.process_steps(id_house, date_start, date_end, wristbands, result_humidity, result, result_rssi)
                                
        end_time = time.time()
        print("Tiempo de consulta: " + str(end_time - start_time) + " segundos")

        start_time = time.time()
        for a in result:
            a['date'] = datetime.datetime.fromtimestamp(a['timestamp'])
            a['name'] = sensors[a['id_sensor']]

        for container in result_rssi:
            for a in container:
                a['date'] = datetime.datetime.fromtimestamp(a['timestamp'])
                a['name'] = anchors[a['id_anchor']]
        
        for a in result_humidity:
            a['date'] = datetime.datetime.fromtimestamp(a['timestamp'])
            a['name'] = sensors[a['id_sensor']]

        end_time = time.time()
        print("Tiempo de formateo: " + str(end_time - start_time) + " segundos")
        
        start_time = time.time()
        if result:
            df = pd.DataFrame(result)
            fig = px.line(df, x='date', y ='id_sensor', markers=True, symbol = 'id_sensor', hover_data = ['date', 'id_sensor', 'state'], color = 'name', title='Estado de los sensores')
            plot_div = plot(fig, output_type='div', include_plotlyjs='cdn', include_mathjax=False)
        
        for container in result_rssi:
            df = pd.DataFrame(container)
            fig = px.scatter(df, x='date', y ='rssi', symbol='id_anchor', hover_data = ['date', 'rssi', 'id_anchor', 'id_beacon'], color = 'name', title='RSSI de los anclajes de la ' + str(wristbands[container[0]['id_beacon']]).lower())
            plot_div_2.append(plot(fig, output_type='div', include_plotlyjs='cdn', include_mathjax=False))
        
        if result_humidity:
            df = pd.DataFrame(result_humidity)
            fig = px.line(df, x='date', y ='humidity', markers=True, symbol = 'id_sensor', hover_data = ['date', 'id_sensor'], color = 'name', title='Sensor de humedad')
            plot_div_3 = plot(fig, output_type='div', include_plotlyjs='cdn', include_mathjax=False)
            
        end_time = time.time()
        print("Tiempo de creacion de graficas: " + str(end_time - start_time) + " segundos")
        #Crea el string de los parametros de busqueda indicando cada uno de los parametros
        search_params_string = "Fecha: " + str(date) + " | " + "Casa: " + str(id_house) \
            + " | " + "Sensores: " + str(search_params['sensors']) + " | " + "Anclajes: " \
            + str(search_params['anchors']) + " | " + "Pulseras: " + str(search_params['wristbands'])

    return render(request, 'adminManager/data_charts.html',{
        'form': forms.DateChartFilter(),
        'id': id,
        'search_params': search_params_string,
        'user': User.get_full_name(request.user),
        'group': str(request.user.groups.all()[0]),
        'plot_div': plot_div,
        'plot_div_2': plot_div_2,
        'plot_div_3': plot_div_3
    } )

@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['admin'])
@log_exceptions
def download_data(request):
    if request.method == 'POST':
        return HttpResponse("Solo se aceptan peticiones GET")

    date = request.GET.get('date')
    id_house = request.GET.get('id_house')

    plot_div = None
    plot_div_2 = []
    plot_div_3 = None

    search_params = {}
    search_params_string = ''

    sensors = {}
    anchors = {}
    wristbands = {}
    
    if date not in ['',None] and id_house not in ['',None]:
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        search_params['date'] = date
        date_start = datetime.datetime(date.year, date.month, date.day, 0, 0, 0).timestamp()
        search_params['timestamp_start'] = date_start
        date_end = datetime.datetime(date.year, date.month, date.day, 23, 59, 59).timestamp()
        search_params['timestamp_end'] = date_end

        search_params['sensors'] = 0
        search_params['anchors'] = 0
        search_params['wristbands'] = 0
        
        for sensor in db.sensor_collection.find({'id_house': int(id_house)}):
            search_params['sensors'] += 1
            sensors[sensor['_id']] = sensor['name']
        
        for anchor in db.anchor_collection.find({'id_house': int(id_house)}):
            search_params['anchors'] += 1
            anchors[anchor['_id']] = anchor['name']
        
        for wristband in db.wristband_collection.find({'id_house': int(id_house)}):
            search_params['wristbands'] += 1
            wristbands[wristband['_id']] = wristband['name']

        result_humidity = []
        result_rssi = []
        result = []
        functions.process_steps(id_house, date_start, date_end, wristbands, result_humidity, result, result_rssi)

        for a in result:
            a['date'] = datetime.datetime.fromtimestamp(a['timestamp'])
            a['name'] = sensors[a['id_sensor']]

        for container in result_rssi:
            for a in container:
                a['date'] = datetime.datetime.fromtimestamp(a['timestamp'])
                a['name'] = anchors[a['id_anchor']]
        
        for a in result_humidity:
            a['date'] = datetime.datetime.fromtimestamp(a['timestamp'])
            a['name'] = sensors[a['id_sensor']]

        df1, df2, df3 = None, None, None
        
        if result:
            df1 = pd.DataFrame(result)

        for container in result_rssi:
            df2 = pd.DataFrame(container)
        
        if result_humidity:
            df3 = pd.DataFrame(result_humidity)
    
        #Crea el string de los parametros de busqueda indicando cada uno de los parametros
        search_params_string = "Fecha: " + str(date) + " | " + "Casa: " + str(id_house) \
            + " | " + "Sensores: " + str(search_params['sensors']) + " | " + "Anclajes: " \
            + str(search_params['anchors']) + " | " + "Pulseras: " + str(search_params['wristbands'])

        csv_data1, csv_data2, csv_data3 = None, None, None
        if df1 is not None:
            csv_data1 = df1.to_csv(index=False)
        if df2 is not None:
            csv_data2 = df2.to_csv(index=False)
        if df3 is not None:
            csv_data3 = df3.to_csv(index=False)

        # Create a ZIP file that groups sensors, rssi and environment CSV files
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            # Add CSV data to the ZIP file
            if csv_data1:
                zip_file.writestr("sensors.csv", csv_data1)
            if csv_data2:
                zip_file.writestr("rssi.csv", csv_data2)
            if csv_data3:
                zip_file.writestr("environment.csv", csv_data3)

        file_name = "house_" + str(id_house) + "_" + str(date) + ".zip"
        zip_buffer.seek(0)
        response = FileResponse(zip_buffer, content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename={file_name}'
        return response
                
    return render(request, 'adminManager/data_charts.html',{
            'form': forms.DateChartFilter(),
            'id': id,
            'search_params': search_params_string,
            'user': User.get_full_name(request.user),
            'group': str(request.user.groups.all()[0]),
            'plot_div': plot_div,
            'plot_div_2': plot_div_2,
            'plot_div_3': plot_div_3
        } )


@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['admin'])
@log_exceptions
def incidences(request):
    if request.method == 'POST':
        form = forms.IncidenceForm(request.POST)
        if form.is_valid():
            db.add_incidence(form.cleaned_data)
    
    #obtain all the incidences
    incidences_result = db.incidence_collection.find()
    incidences = []
    for incidence in incidences_result:
        incidence_h = models.Incidence.dict_to_incidence(incidence)
        incidences.append(incidence_h)

    context = {
        'form': forms.IncidenceForm(),
        'incidences': incidences,
        'user': User.get_full_name(request.user),
        'group': str(request.user.groups.all()[0])
    }

    return render(request, 'adminManager/incidences.html', context)

@login_required(login_url=login_url_string)
@allowed_users(allowed_roles=['admin'])
@log_exceptions
def delete_incidence(request, id):
    db.delete_incidence(id)
    return redirect('adminManager:incidences')
