import requests
import json

class Accident:
    def __init__(self, mo_identifier, perceived_severity,  displayed_text):
        self.mo_identifier = mo_identifier
        self.perceived_severity = perceived_severity
        self.displayed_text = displayed_text

    @classmethod
    def from_api(cls, mo_identifier):
        api_url = f"https://127.0.0.1/ngsa_api?mo_identifier={mo_identifier}"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            accidents = []
            for accident_data in data.get('accidents', []):
                accidents.append(cls(
                    accident_data.get('mo_identifier', None),
                    accident_data.get('perceived_severity', None),
                    accident_data.get('displayed_text', None)
                ))
            return accidents
        else:
            return None

    @classmethod
    def api_create(cls, accident):
        api_url = "https://127.0.0.1/ngsa_api/create"
        payload = {
            'mo_identifier': accident.mo_identifier,
            'perceived_severity': accident.perceived_severity,
            'displayed_text': accident.displayed_text
        }
        response = requests.post(api_url, data=json.dumps(payload))
        return response.status_code

    @classmethod
    def api_delete(cls, id):
        api_url = "https://example.com/ngsa_api/delete"
        payload = {
            'id': id
        }
        response = requests.post(api_url, data=json.dumps(payload))
        return response.status_code

class BaseStation:
    def __init__(self, temperature, battery_charge):
        self.temperature = temperature
        self.battery_charge = battery_charge
        #self.signal_strength = signal_strength
        #self.traffic_load = traffic_load
        #self.error_rate = error_rate
        #self.backhaul_utilization = backhaul_utilization
        #self.connected_users = connected_users
        #self.hardware_faults = hardware_faults

    @classmethod
    def bs_readings(cls):
        api_url = "https://example.com/ngsa_api/bs_readings"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            temperature = data.get('temperature', None)
            battery_charge = data.get('battery_charge', None)
            return cls(temperature = temperature, battery_charge = battery_charge)
        else:
            return None