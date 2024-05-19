import pysmile
# pysmile_license is your license key
import pysmile_license
import ngsa_api as ng
from datetime import datetime
import database
import logging



# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Степени уверенности для Percieved Severity МИ

WARNING_CONFIDENCE = 0.3
MINOR_CONFIDENCE = 0.5
MAJOR_CONFIDENCE = 0.7

# Идентификатор БС
MO_IDENTIFIER = "BTS_23_129"
def BayesianNetwork(MO_IDENTIFIER):

    # Подключение к БД
    db = database.Database()
    db.connect()

    #Зачистить старые риски
    database.RiskAccident.delete_old_risks(MO_IDENTIFIER)

    #Загрузка предварительно созданной байесовской сети из файла
    net = pysmile.Network()
    net.read_file("Network.xdsl");


    accidents = ng.Accident.from_api(MO_IDENTIFIER)

    for accident in accidents:
        net.set_evidence(accident.displayed_text, "State1")


    #Считываем данный о BTS
    base_station = ng.BaseStation.bs_readings()


    # Загружаем температуру
    temperature = base_station.temperature

    temperature_intervals = {
        (-float('inf'), -10): 'lessm10',
        (-10, 0): 'fm10t0',
        (0, 10): 'f0t10',
        (10, 20): 'f10t20',
        (20, 30): 'f20t30',
        (30, 50): 'f30t50',
        (50, float('inf')): 'more50'
    }

    for interval, value in temperature_intervals.items():
        if interval[0] < temperature < interval[1]:
            net.set_evidence('ambient_temperature', value)
            break

    #Загружаем заряд аккумулятора

    battery_charge = base_station.battery_charge
    battery_intervals = {
        (0, 25): 'less25',
        (25, 50): 'f25t50',
        (50, 75): 'f50t75',
        (75, 100): 'f75t100'
    }

    for interval, value in battery_intervals.items():
        if interval[0] < battery_charge <= interval[1]:
            net.set_evidence('WIB_battery', value)
            break


    net.update_beliefs()

    identifiers = net.get_all_node_ids()
    identifiers = [id for id in identifiers if id not in [accident.displayed_text for accident in accidents]]

    for id in identifiers:
        true_belief = net.get_node_value(id)[1]
        severity = "Major" if true_belief > 0.7 else "Minor" if true_belief > 0.5 else "Warning" if true_belief > 0.3 else None
        if severity is not None:
            accident = ng.Accident(MO_IDENTIFIER, severity, id)
            if accident not in accidents:
                logging.info('Событие на %s, Важность: %s, Аварийное сообщение: %s, Степень уверенности: %s',accident.mo_identifier, accident.perceived_severity, accident.displayed_text, true_belief)
                database.RiskAccident.save_to_database()
                if ng.Accident.to_api(accident):
                    logging.info('--Отправлено в API NGSA--')




BayesianNetwork(MO_IDENTIFIER)