# Generador de Reportes de Zabbix

Este proyecto genera reportes CSV con información detallada sobre el uso de recursos (CPU, memoria, sistema de archivos) en servidores monitoreados por Zabbix. El reporte incluye estadísticas como el porcentaje de uso y el espacio utilizado, y puede enviarse por correo electrónico automáticamente.

## Requisitos

1. Python 3.x
2. Zabbix con API habilitada
3. Dependencias Python:
   - requests
   - smtplib
   - email

## Instalación

1. Clona el repositorio:
    ```bash
    git clone https://github.com/tu_usuario/zabbix-report-generator.git
    cd zabbix-report-generator
    ```

2. Instala las dependencias necesarias:
    ```bash
    pip install -r requirements.txt
    ```

3. Configura tu archivo `config.json` con los detalles de tu servidor Zabbix, credenciales de correo y parámetros de los ítems a monitorear.

## Uso

1. Modifica el archivo `config.json` para incluir:
   - La URL de tu servidor Zabbix y el token de autenticación.
   - Las claves de los ítems a monitorear (`filesystem`, `memory`, `cpu`).
   - Los tags de los hosts que deseas incluir en el reporte.
   - Configura las opciones de correo electrónico para el envío automático de reportes.

2. Genera un reporte ejecutando el siguiente comando:
    ```bash
    python main.py config.json --start_date YYYY-MM-DD --end_date YYYY-MM-DD --report_name reporte_personalizado
    ```

   - **start_date** y **end_date** son opcionales, si no se proporcionan, el reporte tomará el mes anterior por defecto.
   - **report_name** es opcional, si no se proporciona, se utilizará el nombre por defecto en el archivo de configuración.

## Ejemplo de Configuración

```json
{
    "ZABBIX_URL": "http://tu_servidor_zabbix/api_jsonrpc.php",
    "AUTH_TOKEN": "tu_token_de_autenticacion_zabbix",
    "ITEM_KEYS": {
        "filesystem": {
            "percent": "vfs.fs.size[*,pused]",
            "used": "vfs.fs.size[*,used]"
        },
        "memory": {
            "percent": "vm.memory.util",
            "used": "vm.memory.size[used]"
        },
        "cpu": {
            "percent": "system.cpu.util"
        }
    },
    "HOST_TAGS": [
        {"tag": "cliente", "value": "monitoreo", "operator": 1},
        {"tag": "os", "value": "linux", "operator": 1}
    ],
    "CSV_FIELDS": [
        "Host ID", "Nombre", "Dirección IP", "Tipo", "Nombre Item", 
        "Porcentaje Utilizado", "Espacio Usado", 
        "Promedio Porcentaje", "Mínimo Porcentaje", "Máximo Porcentaje", "Percentil 95 Porcentaje",
        "Promedio Usado", "Mínimo Usado", "Máximo Usado", "Percentil 95 Usado"
    ],
    "default_report_name": "zabbix_report",
    "email": {
        "sender": "tu_correo@tudominio.com",
        "recipients": ["destinatario1@ejemplo.com", "destinatario2@ejemplo.com"],
        "cc": ["destinatario1@ejemplo.com", "destinatario2@ejemplo.com"],
        "subject": "Reporte de Zabbix - {start_date} a {end_date}",
        "body": "Estimado/a,\n\nAdjunto encontrarás el reporte de Zabbix generado para el período del {start_date} al {end_date}.\n\nEste reporte incluye información sobre {item_types} para los hosts monitoreados.\n\nSi tienes alguna pregunta o necesitas información adicional, no dudes en contactarnos.\n\nSaludos cordiales,\nEquipo de Monitoreo",
        "smtp_server": "smtp.tudominio.com",
        "smtp_port": 587,
        "use_tls": true,
        "use_authentication": true,
        "username": "tu_usuario@tudominio.com",
        "password": "tu_contraseña_segura"
    }
}
