import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_email(config, report_file):
    msg = MIMEMultipart()
    msg['From'] = config['email']['sender']
    msg['To'] = ', '.join(config['email']['recipients'])
    msg['Subject'] = config['email']['subject']

    body = config['email']['body']
    msg.attach(MIMEText(body, 'plain'))

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
        
        server.send_message(msg)
        server.quit()
        print("Correo enviado exitosamente")
    except Exception as e:
        print(f"Error al enviar el correo: {str(e)}")