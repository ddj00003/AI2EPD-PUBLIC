from datetime import datetime

def time_window_helper(data) -> dict | None:
    try:
        return {
            "size_window": int(data["size_window"]),
            "rssi": round(float(data["rssi"]),2)
        }
    except:
        return None

def house_data_anchor_helper(data) -> dict | None:
    try:
        return {
            "timestamp": datetime.fromtimestamp(data["timestamp"]),
            "rssi": int(data["rssi"]),
            "id_anchor": str(data["id_anchor"]),
            "id_beacon": int(data["id_beacon"]),
            "time_window": time_window_helper(data["time_window"])
        }
    except:
        return None

def house_data_sensor_helper(data, type) -> dict | None:
    try:
        return {
            "timestamp": datetime.fromtimestamp(data["timestamp"]),
            "id_sensor": str(data["id_sensor"]),
            "id_house": int(data["id_house"]),
            "state": str(data["state"]),
            "type": str(type),
        }
    except:
        return None

def house_data_sensor_temp_humidity_helper(data) -> dict | None:
    try:
        return {
            "timestamp": datetime.fromtimestamp(data["timestamp"]),
            "id_sensor": str(data["id_sensor"]),
            "id_house": int(data["id_house"]),
            "humidity": int(data["humidity"]),
            "temperature": int(data["temperature"]),
            "pressure": int(data["pressure"]),
            "type": "temp&hm&presion",
        }
    except:
        return None

def house_data_sensor_energy_helper(data) -> dict | None:
    try:
        return {
            "timestamp": datetime.fromtimestamp(data["timestamp"]),
            "id_sensor": str(data["id_sensor"]),
            "id_house": int(data["id_house"]),
            "current_power": float(data["current_power"]),
            "total_consumption": float(data["total_consumption"]),
            "current_consumption": float(data["current_consumption"]),
            "type": "energy_consumption",
        }
    except:
        return None
    
def house_data_sensor_energy_v2_helper(data) -> dict | None:
    try:
        return {
            "timestamp": datetime.fromtimestamp(data["timestamp"]),
            "id_sensor": str(data["id_sensor"]),
            "id_house": int(data["id_house"]),
            "current_a": float(data["current_a"]),
            "current_w": float(data["current_w"]),
            "today_consumption": float(data["today_consumption"]),
            "total_consumption": float(data["total_consumption"]),
            "total_voltage": float(data["total_voltage"]),
            "type": "energy_consumption_v2",
        }
    except:
        return None

def house_data_wristband_helper(data) -> dict | None:
    try:
        return {
            "timestamp": datetime.fromtimestamp(data["timestamp"]),
            "id_wristband": str(data["id_beacon"]),
            "battery": int(data["battery"]),
            "last_steps": str(data["steps"])
        }
    except:
        return None

def user_helper(user) -> dict | None:
    try:
        return {
            "username": str(user["username"]),
            "hashed_password": str(user["hashed_password"]),
            "disabled": str(user["disabled"]),
        }
    except:
        return None

def location_helper(data) -> dict | None:
    try:
        return {
            "date": datetime.fromtimestamp(data["timestamp"]),
            "location": str(data["location"])
        }
    except:
        return None

def hg_helper(data) -> dict | None:
    try:
       data['date'] = datetime.fromtimestamp(data['timestamp'])
       return data
    except:
        return None
