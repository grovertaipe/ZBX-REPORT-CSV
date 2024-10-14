import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime

def send_email(config, report_file, start_date, end_date, item_types):
    msg = MIMEMultipart()
    msg['From'] = config['email']['sender']
    msg['To'] = ', '.join(config['email']['recipients'])
    
    if 'cc' in config['email']:
        msg['Cc'] = ', '.join(config['email']['cc'])
    
    # Formatear las fechas
    start_date_formatted = datetime.strptime(start_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    end_date_formatted = datetime.strptime(end_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    
    # Crear el asunto dinámico
    subject = config['email']['subject'].format(
        start_date=start_date_formatted,
        end_date=end_date_formatted
    )
    msg['Subject'] = subject

    # Crear el cuerpo dinámico
    body = config['email']['body'].format(
        start_date=start_date_formatted,
        end_date=end_date_formatted,
        item_types=", ".join(item_types)
    )
    msg.attach(MIMEText(body, 'plain'))

    # Adjuntar el archivo de reporte
    with open(report_file, 'rb') as file:
        part = MIMEApplication(file.read(), Name=report_file)
    part['Content-Disposition'] = f'attachment; filename="{report_file}"'
    msg.attach(part)

    try:
        server = smtplib.SMTP(config['email']['smtp_server'], config['email']['smtp_port'])
        
        if config['email'].get('use_tls', False):
            server.starttls()
        
        if config['email'].get('use_authentication', False):
            server.login(config['email']['username'], config['email']['password'])
        
        recipients = config['email']['recipients'] + config['email'].get('cc', [])
        server.sendmail(msg['From'], recipients, msg.as_string())
        server.quit()
        
        print("Correo enviado exitosamente")
    except Exception as e:
        print(f"Error al enviar el correo: {str(e)}")
