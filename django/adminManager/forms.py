from django import forms
from django.utils.translation import gettext_lazy as _
from . db import get_list_houses

SENSORS_TYPES= [
    ('motion', _('Movimiento')),
    ('open/close', _('Apertura/Cierre')),
    ('temp&hm&presion', _('Temperatura, humedad y presión')),
    ('energy_consumption', _('Consumo de energía')),
    ('energy_consumption_v2', _('Consumo de energía V2'))
    ]
class CreateNewHouse(forms.Form):
    name = forms.CharField(label=_('Nombre'), max_length=100,required= True)
    description = forms.CharField(label=_('Descripción'), widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}), max_length=1000, required= True)
    mac = forms.CharField(label=_('Mac'), max_length=100, required= True)

class CreateNewAnchor(forms.Form):
    id_house = forms.IntegerField(label=_('Vivienda'), widget=forms.Select(choices=get_list_houses()), required= True)
    name = forms.CharField(label=_('Nombre'), max_length=100,required= True)
    description = forms.CharField(label=_('Descripción'), widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}), max_length=1000, required= True)
    mac = forms.CharField(label=_('Mac'), max_length=100, required= True)
    def __init__(self, *args, **kwargs):
        super(CreateNewAnchor, self).__init__(*args, **kwargs)
        self.fields['id_house'] = forms.IntegerField(label=_('Vivienda'), widget=forms.Select(choices=get_list_houses()), required= True)

class CreateNewDevice(forms.Form):
    id_house = forms.IntegerField(label=_('Vivienda'), widget=forms.Select(choices=get_list_houses()), required= True)
    name = forms.CharField(label=_('Nombre'), max_length=100,required= True)
    description = forms.CharField(label=_('Descripción'), widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}), max_length=1000, required= True)
    mac = forms.CharField(label=_('Mac'), max_length=100, required= True)
    def __init__(self, *args, **kwargs):
        super(CreateNewDevice, self).__init__(*args, **kwargs)
        self.fields['id_house'] = forms.IntegerField(label=_('Vivienda'), widget=forms.Select(choices=get_list_houses()), required= True)

class IdHouseData(forms.Form):
    id_house = forms.IntegerField(label='', widget=forms.Select(choices=get_list_houses()), required= True)
    def __init__(self, *args, **kwargs):
        super(IdHouseData, self).__init__(*args, **kwargs)
        self.fields['id_house'] = forms.IntegerField(label='', widget=forms.Select(choices=get_list_houses()), required= True)

class CreateNewSensor(forms.Form):
    id_house = forms.IntegerField(label=_('Vivienda'), widget=forms.Select(choices=get_list_houses()), required= True)
    name = forms.CharField(label=_('Nombre'), max_length=100,required= True)
    description = forms.CharField(label=_('Descripción'), widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}), max_length=1000, required= True)
    ieee_address = forms.CharField(label=_('Dirección ieee'), max_length=100, required= True)
    type = forms.CharField(label=_('Tipo de sensor'), widget=forms.Select(choices=SENSORS_TYPES), required= True)
    def __init__(self, *args, **kwargs):
        super(CreateNewSensor, self).__init__(*args, **kwargs)
        self.fields['id_house'] = forms.IntegerField(label=_('Vivienda'), widget=forms.Select(choices=get_list_houses()), required= True)

class Register(forms.Form):
    username = forms.CharField(label=_('Usuario'), max_length=100, required= True)
    password = forms.CharField(label=_('Contraseña'), max_length=100, required= True)
    password2 = forms.CharField(label=_('Repetir contraseña'), max_length=100, required= True)

    def clean(self):
        cleaned_data = super(Register, self).clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password != password2:
            raise forms.ValidationError(_('Las contraseñas no coinciden'))
        return cleaned_data

class IncidenceForm(forms.Form):
    id_house = forms.IntegerField(label=_('Vivienda'), widget=forms.Select(choices=get_list_houses()), required= True)
    date_start = forms.DateField(required = True, label=_('Fecha de inicio'),
        widget=forms.DateInput(format='%d/%m/%Y',attrs=dict(type='date')))
    date_end = forms.DateField(required = True, label=_('Fecha de fin'),
        widget=forms.DateInput(format='%d/%m/%Y',attrs=dict(type='date')))
    description = forms.CharField(label=_('Descripción'), widget=forms.Textarea(attrs={'rows': 2, 'cols': 40}))
    def __init__(self, *args, **kwargs):
        super(IncidenceForm, self).__init__(*args, **kwargs)
        self.fields['id_house'] = forms.IntegerField(label=_('Vivienda'), widget=forms.Select(choices=get_list_houses()), required= True)

class DateChartFilter(forms.Form):
    date = forms.DateField(required = True, label='', input_formats = ['%d/%m/%Y'],
        widget=forms.DateInput(format='%d/%m/%Y',attrs=dict(type='date')))
    id_house = forms.IntegerField(label='', widget=forms.Select(choices=get_list_houses()), required= True)
    def __init__(self, *args, **kwargs):
        super(DateChartFilter, self).__init__(*args, **kwargs)
        self.fields['id_house'] = forms.IntegerField(label='', widget=forms.Select(choices=get_list_houses()), required= True)