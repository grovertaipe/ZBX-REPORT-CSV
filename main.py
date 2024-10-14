import csv
import argparse
from datetime import datetime
from utils import get_date_range, calculate_stats, bytes_to_human_readable, load_config
from zabbix_operations import ZabbixOperations
from email_sender import send_email

def process_items(zabbix, host_id, item_type, time_from, time_till, item_keys):
    percent_key = item_keys[item_type]['percent']
    used_key = item_keys[item_type].get('used')

    percent_items = zabbix.get_items_for_host(host_id, [percent_key])
    used_items = zabbix.get_items_for_host(host_id, [used_key]) if used_key else []

    results = []

    for percent_item in percent_items:
        result = {
            'Tipo': item_type,
            'Nombre Item': percent_item['name'],
            'Porcentaje Utilizado': f"{float(percent_item['lastvalue']):.2f}%"
        }

        trend_data = zabbix.get_trend_data(percent_item['itemid'], time_from, time_till)
        avg, min_val, max_val = calculate_stats(trend_data)
        result.update({
            'Promedio Porcentaje': f"{avg:.2f}%" if avg is not None else "N/A",
            'Mínimo Porcentaje': f"{min_val:.2f}%" if min_val is not None else "N/A",
            'Máximo Porcentaje': f"{max_val:.2f}%" if max_val is not None else "N/A"
        })

        if used_items:
            if item_type == 'memory':
                used_item = used_items[0]
            else:
                used_item = next((item for item in used_items if item['name'].split()[0] == percent_item['name'].split()[0]), None)

            if used_item:
                last_value = bytes_to_human_readable(float(used_item['lastvalue']))
                result['Espacio Usado'] = last_value

                trend_data = zabbix.get_trend_data(used_item['itemid'], time_from, time_till)
                avg, min_val, max_val = calculate_stats(trend_data)
                result.update({
                    'Promedio Usado': bytes_to_human_readable(avg) if avg is not None else "N/A",
                    'Mínimo Usado': bytes_to_human_readable(min_val) if min_val is not None else "N/A",
                    'Máximo Usado': bytes_to_human_readable(max_val) if max_val is not None else "N/A"
                })
            else:
                result.update({
                    'Espacio Usado': 'N/A',
                    'Promedio Usado': 'N/A',
                    'Mínimo Usado': 'N/A',
                    'Máximo Usado': 'N/A'
                })
        else:
            result.update({
                'Espacio Usado': 'N/A',
                'Promedio Usado': 'N/A',
                'Mínimo Usado': 'N/A',
                'Máximo Usado': 'N/A'
            })

        results.append(result)

    return results

def generate_report(config_file, start_date, end_date, report_name=None):
    config = load_config(config_file)
    zabbix = ZabbixOperations(config['ZABBIX_URL'], config['AUTH_TOKEN'])
    time_from, time_till = get_date_range(start_date, end_date)

    if report_name is None:
        report_name = config.get('default_report_name', 'zabbix_report')

    current_date = datetime.now().strftime("%Y-%m-%d")
    output_file = f"{report_name}_{current_date}.csv"

    hosts = zabbix.get_hosts(config['HOST_TAGS'])

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=config['CSV_FIELDS'])
        writer.writeheader()

        for host in hosts:
            host_id = host['hostid']
            host_name = host['host']
            ip_address = host['interfaces'][0]['ip']

            for item_type in config['ITEM_KEYS']:
                items_data = process_items(zabbix, host_id, item_type, time_from, time_till, config['ITEM_KEYS'])

                for item_data in items_data:
                    row = {
                        'Host ID': host_id,
                        'Nombre': host_name,
                        'Dirección IP': ip_address
                    }
                    row.update(item_data)
                    writer.writerow(row)

    print(f"El reporte ha sido generado en {output_file}")
    
    # Obtener los tipos de items del reporte
    item_types = list(config['ITEM_KEYS'].keys())
    # Enviar el reporte por correo electrónico
    send_email(config, output_file, start_date, end_date, item_types)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generar reporte de Zabbix")
    parser.add_argument("config_file", help="Archivo de configuración JSON")
    parser.add_argument("--start_date", help="Fecha de inicio (YYYY-MM-DD), opcional", default=None)
    parser.add_argument("--end_date", help="Fecha de fin (YYYY-MM-DD), opcional", default=None)
    parser.add_argument("--report_name", help="Nombre personalizado para el reporte", default=None)
    args = parser.parse_args()

    # Llamamos a generate_report con el archivo de configuración, fechas opcionales y nombre de reporte personalizado
    generate_report(args.config_file, args.start_date, args.end_date, args.report_name)
