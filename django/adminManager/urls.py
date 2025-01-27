from django.urls import path
from . import views


app_name = 'adminManager'
urlpatterns = [
    path('', views.main, name='home'),
    path('houses', views.houses, name='houses'),
    path('deleteHouse/<int:id>', views.delete_house, name='delete_house'),
    path('editHouse/<int:id>', views.edit_house, name='edit_house'),
    path('anchors', views.anchors , name='anchors'),
    path('deleteAnchor/<int:id>', views.delete_anchor, name='delete_anchor'),
    path('editAnchor/<int:id>', views.edit_anchor, name='edit_anchor'),
    path('wristbands', views.wristbans, name='wristbands'),
    path('deleteWristband/<int:id>', views.delete_wristband, name='delete_wristband'),
    path('editWristband/<int:id>', views.edit_wristband, name='edit_wristband'),
    path('sensors', views.sensors, name='sensors'),
    path('deleteSensor/<int:id>', views.delete_sensor, name='delete_sensor'),
    path('editSensor/<int:id>', views.edit_sensor, name='edit_sensor'),
    path('getDataHouse', views.data_id_post, name='get_data_house'),
    path('data/<int:id>', views.data_id , name='data_id'),
    path('data', views.data_id , name='data_id'),
    path('getLocationHouse', views.location_id_post, name='get_location_house'),
    path('location/<int:id>', views.location_id , name='location_id'),
    path('location', views.location_id , name='location_id'),
    #path('register', views.register, name='register')
    path('dataChart', views.data_charts, name='data_chart'),
    path('downloadData', views.download_data, name='download_data'),
    path('incidences', views.incidences, name='incidences'),
    path('deleteIncidence/<int:id>', views.delete_incidence, name='delete_incidence')
]