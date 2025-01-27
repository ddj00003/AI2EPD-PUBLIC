from django import forms
import datetime as dt
from crispy_forms.helper import FormHelper
from django.utils.translation import gettext_lazy as _

HOUR_CHOICES = [(dt.time(hour=x), '{:02d}:00'.format(x)) for x in range(0, 24)]

ACTIVITIES_TYPES= [
    ('exercise', _('Caminar')),
    ('shower', _('Ducha')),
    ('brush_teeth', _('Cepillado')),
    ('eat', _('Comer')),
    ('take_medicine', _('Medicación')),
    ('sleep', _('Dormir'))
    ]
 
class DateInput(forms.DateInput):
    input_type = 'date'

'''class DateForm(forms.ModelForm):
    class Meta:
        model = Date
        fields = fields = '__all__'
        widgets = {
                'expiration_date': DateInput(),
            }
'''
class DateForm(forms.Form):
    date = forms.DateField(required = False, label='', input_formats = ['%d/%m/%Y'],
        widget=forms.DateInput(format='%d/%m/%Y',attrs=dict(type='date')))
    month = forms.DateField(required = False, label='', input_formats = ['%m'],
        widget=forms.DateInput(format='%m',attrs=dict(type='month')))
    week = forms.DateField(required = False, label='', input_formats = ['%w'],
        widget=forms.DateInput(format='%w',attrs=dict(type='week')))

class CustomDateForm(forms.Form):
    start_date = forms.DateField(required = True, label='', input_formats = ['%d/%m/%Y'],
        widget=forms.DateInput(format='%d/%m/%Y',attrs=dict(type='date')))
    end_date = forms.DateField(required = True, label='', input_formats = ['%d/%m/%Y'],
        widget=forms.DateInput(format='%d/%m/%Y',attrs=dict(type='date')))
    
class DownloadSummary(forms.Form):
    start_date = forms.DateField(required = True, label=_('Fecha de inicio'),
        widget=forms.DateInput(format='%d/%m/%Y',attrs=dict(type='date')))
    end_date = forms.DateField(required = True, label=_('Fecha de fin'),
        widget=forms.DateInput(format='%d/%m/%Y',attrs=dict(type='date')))
    activity = forms.CharField(label=_('Actividad'), widget=forms.Select(choices=ACTIVITIES_TYPES), required= True)

class TherapeuticContract(forms.Form):
    shower = forms.CharField(label=_('Ducha'), widget=forms.Textarea(attrs={'rows': 2, 'cols': 40}))
    walk = forms.CharField(label=_('Caminar'), widget=forms.Textarea(attrs={'rows': 2, 'cols': 40}))
    brush_teeth = forms.CharField(label=_('Cepillarse los dientes'), widget=forms.Textarea(attrs={'rows': 2, 'cols': 40}))
    eat = forms.CharField(label=_('Comer'), widget=forms.Textarea(attrs={'rows': 2, 'cols': 40}))
    medication = forms.CharField(label=_('Medicación'),widget=forms.Textarea(attrs={'rows': 2, 'cols': 40}))
    sleep = forms.CharField(label=_('Dormir'), widget=forms.Textarea(attrs={'rows': 2, 'cols': 40}))

class TherapeuticContractV2(forms.Form):
    time_fields = [
        ('shower', 'Shower'),
        ('activity_morning', 'Morning Activity'),
        ('activity_afternoon', 'Afternoon Activity'),
        ('sleep', 'Sleep'),
        ('brush_teeth_1', 'Brush Teeth 1'),
        ('brush_teeth_2', 'Brush Teeth 2'),
        ('brush_teeth_3', 'Brush Teeth 3'),
        ('eat_1', 'Eat 1'),
        ('eat_2', 'Eat 2'),
        ('eat_3', 'Eat 3'),
        ('eat_4', 'Eat 4'),
        ('eat_5', 'Eat 5'),
        ('eat_6', 'Eat 6'),
        ('medication_1', 'Medication 1'),
        ('medication_2', 'Medication 2'),
        ('medication_3', 'Medication 3'),
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        
        for field_name, label in self.time_fields:
            self.fields[f"{field_name}_s"] = forms.TimeField(
                input_formats=['%H:%M'],
                required=False,
                label='',
            )
            self.fields[f"{field_name}_e"] = forms.TimeField(
                input_formats=['%H:%M'],
                required=False,
                label='',
            )


def therapeutic_validation(data):
    required_fields = {
        'shower': ('shower_s', 'shower_e'),
        'activity_morning': ('activity_morning_s', 'activity_morning_e'),
        'activity_afternoon': ('activity_afternoon_s', 'activity_afternoon_e'),
        'sleep': ('sleep_s', 'sleep_e'),
        'brush_teeth_1': ('brush_teeth_1_s', 'brush_teeth_1_e'),
        'brush_teeth_2': ('brush_teeth_2_s', 'brush_teeth_2_e'),
        'brush_teeth_3': ('brush_teeth_3_s', 'brush_teeth_3_e'),
        'eat_1': ('eat_1_s', 'eat_1_e'),
        'eat_2': ('eat_2_s', 'eat_2_e'),
        'eat_3': ('eat_3_s', 'eat_3_e'),
        'eat_4': ('eat_4_s', 'eat_4_e'),
        'eat_5': ('eat_5_s', 'eat_5_e'),
        'eat_6': ('eat_6_s', 'eat_6_e'),
        'medication_1': ('medication_1_s', 'medication_1_e'),
        'medication_2': ('medication_2_s', 'medication_2_e'),
        'medication_3': ('medication_3_s', 'medication_3_e')
    }
    
    for field, (start, end) in required_fields.items():
        if (data[start] is None and data[end] is not None) or (data[start] is not None and data[end] is None):
            return False
    
    return True
