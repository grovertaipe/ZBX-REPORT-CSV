import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta

def get_client_tag_value(config):
    """Obtiene el valor del tag 'cliente' de la configuración."""
    for tag in config.get('HOST_TAGS', []):
        if tag.get('tag') == 'cliente':
            return tag.get('value', '')
    return 'default'

def format_email_content(config, start_date=None, end_date=None):
    """Formatea el contenido del correo reemplazando las variables."""
    if start_date is None or end_date is None:
        # Si no se proporcionan fechas, usar el mes anterior
        today = datetime.now()
        start_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1).strftime("%Y-%m-%d")
        end_date = (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m-%d")

    # Obtener los tipos de items desde la configuración
    item_types = ", ".join(config['ITEM_KEYS'].keys())
    
    # Obtener el valor del tag cliente
    client_name = get_client_tag_value(config)

    # Formatear el asunto y cuerpo del correo
    subject = config['email']['subject'].format(
        start_date=start_date,
        end_date=end_date,
        client=client_name.upper()
    )
    
    body = config['email']['body'].format(
        start_date=start_date,
        end_date=end_date,
        item_types=item_types
    )
    
    return subject, body

def send_email(config, report_file, start_date=None, end_date=None):
    """Envía el correo electrónico con el reporte adjunto."""
    msg = MIMEMultipart()
    msg['From'] = config['email']['sender']
    msg['To'] = ', '.join(config['email']['recipients'])
    
    # Formatear el contenido del correo
    subject, body = format_email_content(config, start_date, end_date)
    msg['Subject'] = subject

    # Agregar el cuerpo del mensaje
    msg.attach(MIMEText(body, 'plain'))

    # Agregar el archivo adjunto
    with open(report_file, 'rb') as file:
        part = MIMEApplication(file.read(), Name=report_file)
    part['Content-Disposition'] = f'attachment; filename="{report_file}"'
    msg.attach(part)

    # Agregar CC si existe en la configuración
    if 'cc' in config['email'] and config['email']['cc']:
        msg['Cc'] = ', '.join(config['email']['cc'])
        all_recipients = config['email']['recipients'] + config['email']['cc']
    else:
        all_recipients = config['email']['recipients']

    try:
        server = smtplib.SMTP(config['email']['smtp_server'], config['email']['smtp_port'])
        
        if config['email'].get('use_tls', False):
            server.starttls()
        
        if config['email'].get('use_authentication', False):
            server.login(config['email']['username'], config['email']['password'])
        
        server.send_message(msg)
        server.quit()
        print("Correo enviado exitosamente")
    except Exception as e:
        print(f"Error al enviar el correo: {str(e)}")