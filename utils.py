import requests
import json
from datetime import datetime, timedelta
from statistics import mean
import os

def zabbix_api_request(url, auth_token, method, params):
    """Función para hacer solicitudes a la API de Zabbix"""
    headers = {"Content-Type": "application/json-rpc"}
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "auth": auth_token,
        "id": 1
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response.json()

def get_date_range(start_date=None, end_date=None):
    """
    Convierte fechas en formato string a timestamps.
    Si no se proporcionan fechas, usa el mes anterior por defecto.
    El rango va desde el inicio del primer día hasta el inicio del día siguiente al último día especificado.
    """
    if not start_date or not end_date:
        today = datetime.now()
        first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_day_last_month = today.replace(day=1) - timedelta(days=1)
        start = first_day_last_month
        end = last_day_last_month
    else:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = end.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    return int(start.timestamp()), int(end.timestamp())

def calculate_stats(trend_data):
    """Calcula las estadísticas de los datos de tendencia"""
    if not trend_data:
        return None, None, None

    avg_values = [float(item["value_avg"]) for item in trend_data]
    min_values = [float(item["value_min"]) for item in trend_data]
    max_values = [float(item["value_max"]) for item in trend_data]
    
    return mean(avg_values), min(min_values), max(max_values)

def bytes_to_human_readable(size_in_bytes):
    """Convierte bytes a un formato legible por humanos"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} PB"

def load_config(json_file):
    """Carga la configuración desde un archivo JSON."""
    if not os.path.isfile(json_file):
        raise FileNotFoundError(f"El archivo {json_file} no se encuentra.")
    with open(json_file, 'r') as file:
        return json.load(file)