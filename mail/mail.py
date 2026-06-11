from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os

try:
    import data.serverConfig as config
except:
    print("Missing server configuration file.")

def sendMail(to, subject, message):
    
    if (message is None):
        print("No message defined.")
        return 2
    
    msg = MIMEMultipart()

    msg['From'] =  f'{config.MAIL_FROM}'
    msg['To'] = to
    msg['Subject'] = subject
    
    msg.attach(MIMEText(message, 'html'))
    server = smtplib.SMTP(f'{config.MAIL_SERVER}:{config.MAIL_PORT}')

    server.starttls() if config.MAIL_USE_TLS else None

    if config.MAIL_USER and config.MAIL_PASS:
        try:
            server.login(config.MAIL_USER, config.MAIL_PASS)
        except:
            print("Login failed for SMTP server.")
            return 3
    
    try:
        server.sendmail(msg['From'], msg['To'], msg.as_string())
    except:
        print("Error sending email.")
        return 4

    server.quit()

    return 0

def buildMessage(template, fields = {}):
    try:
        with open(f'{os.path.dirname(__file__)}/templates/{template}.html') as f:
            content = f.read()
            for field in fields.keys():
                content = content.replace(field, fields[field])

            return content
    except:
        print("Failed to generate message.")
        return None