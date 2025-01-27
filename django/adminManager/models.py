from __future__ import annotations
from datetime import datetime
from . import helpers
from typing import Dict, Any

# Create your models here.

'''class house(models.Model):
    _id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    mac_node = models.CharField(max_length=100)

    def __str__(self):
        return str(self._id)'''

class Anchor():
    id = int | None
    id_house = int | None
    name = str | None
    description : str | None
    mac : str | None
    form : Any

    def __init__(self, id, id_house, name, description, mac):
        self.id = id
        self.id_house = id_house
        self.name = name
        self.description = description
        self.mac = mac

    def __str__(self):
        return str(self.id)
    
    @staticmethod
    def dict_to_anchor(dict : Dict[Any,Any]) -> Anchor | None:
        try:
            id = dict.get("_id")
            id_house = dict.get("id_house")
            name = dict.get("name")
            description = dict.get("description")
            mac = dict.get("mac")

            return Anchor(id, id_house, name, description, mac)
        
        except Exception as e:
            return None
        
    def get_data(self, data : dict) -> Dict[Any,Any] | None:
        return helpers.house_data_anchor_helper(data)
        
class Wristband():
    id : int | None
    id_house : int | None
    name : str | None
    description : str | None
    mac : str | None
    form : Any

    def __init__(self, id, id_house, name, description, mac):
        self.id = id
        self.id_house = id_house
        self.name = name
        self.description = description
        self.mac = mac

    def __str__(self):
        return str(self.id)
    
    @staticmethod
    def dict_to_wristband(dict : Dict[Any,Any]) -> Wristband | None:
        try:
            id = dict.get("_id")
            id_house = dict.get("id_house")
            name = dict.get("name")
            description = dict.get("description")
            mac = dict.get("mac")

            return Wristband(id, id_house, name, description, mac)
        
        except Exception as e:
            return None
        
    def get_data(self, data : Dict[Any,Any]) -> Dict[Any,Any] | None:
        return helpers.house_data_wristband_helper(data)

class Sensor():
    id : int | None
    id_house : int | None
    name : str | None
    description : str | None
    ieee_address : str | None
    type : str | None
    form : Any

    def __init__(self, id, id_house, name, description, ieee_address, type):
        self.id = id
        self.id_house = id_house
        self.name = name
        self.description = description
        self.ieee_address = ieee_address
        self.type = type

    def __str__(self):
        return str(self.id)
    
    @staticmethod
    def dict_to_sensor(dict : Dict[Any,Any]) -> Sensor | None:
        try:
            id = dict.get("_id")
            id_house = dict.get("id_house")
            name = dict.get("name")
            description = dict.get("description")
            ieee_address = dict.get("ieee_address")
            type = dict.get("type")

            return Sensor(id, id_house, name, description, ieee_address, type)
        
        except Exception as e:
            return None
        
    def get_data(self, data : Dict[Any,Any]) -> Dict[Any,Any] | None:

        if self.type in ['motion', 'open/close']:
            return helpers.house_data_sensor_helper(data, self.type)
        elif self.type in ['temp&hm&presion']:
            return helpers.house_data_sensor_temp_humidity_helper(data)
        elif self.type in ['energy_consumption']:
            return helpers.house_data_sensor_energy_helper(data)
        elif self.type in ['energy_consumption_v2']:
            return helpers.house_data_sensor_energy_v2_helper(data)
        else:
            return None        
    
class House():
    id : int | None
    name : str | None
    description : str | None
    mac_node : str | None
    form : Any

    def __init__(self, id, name, description, mac_node):
        self.id = id
        self.name = name
        self.description = description
        self.mac_node = mac_node

    def __str__(self):
        return str(self.id)
    
    @staticmethod
    def dict_to_house(dict : Dict[Any,Any]) -> House | None:
        try:
            id = dict.get("_id")
            name = dict.get("name")
            description = dict.get("description")
            mac_node = dict.get("mac_node")

            return House(id, name, description, mac_node)
        
        except Exception as e:
            return None

class Incidence:
    id : int | None
    id_house : int | None
    description : str | None
    date_start : str | None
    date_end : str | None

    def __init__(self, id, id_house, description, date_start, date_end):
        self.id = id
        self.id_house = id_house
        self.description = description
        self.date_start = date_start
        self.date_end = date_end
    
    def __str__(self):
        return str(self.id)

    @staticmethod
    def dict_to_incidence(dict : Dict[Any,Any]) -> Incidence | None:
        try:
            id = dict.get("_id")
            id_house = dict.get("id_house")
            description = dict.get("description")
            date_start = datetime.fromtimestamp(dict.get("date_start")).strftime('%d/%m/%Y')
            date_end = datetime.fromtimestamp(dict.get("date_end")).strftime('%d/%m/%Y')

            print(date_start)

            return Incidence(id, id_house, description, date_start, date_end)
        
        except Exception as e:
            return None