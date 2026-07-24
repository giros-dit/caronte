from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os

from utils import logger

try:
    from app import config
except:
    logger.error("Missing server configuration file.")

def sendMail(to, subject, message):
    
    if (message is None):
        logger.error("Message is empty.")
        raise Exception("Message is empty.")
    
    msg = MIMEMultipart()

    msg['From'] =  f'{config["MAIL_FROM"]}'
    msg['To'] = to
    msg['Subject'] = subject
    
    msg.attach(MIMEText(message, 'html'))
    server = smtplib.SMTP(host=config["MAIL_SERVER"], port=config["MAIL_PORT"], timeout=10)

    server.starttls() if config['MAIL_USE_TLS'] else None

    if config['MAIL_USER'] and config['MAIL_PASS']:
        try:
            server.login(config['MAIL_USER'], config['MAIL_PASS'])
            logger.debug("Logged in to mail server successfully.")
        except:
            logger.error("Error logging in to mail server.")
            raise Exception("Error logging in to mail server.")
    
    try:
        server.sendmail(msg['From'], msg['To'], msg.as_string())
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise Exception("Error sending email.")

    server.quit()

    return

def buildMessage(template, fields = {}):
    try:
        with open(f'{os.path.dirname(__file__)}/templates/{template}.html') as f:
            content = f.read()
            for field in fields.keys():
                content = content.replace(field, fields[field])

            return content
    except:
        logger.error("Failed to generate message.")
        raise Exception("Failed to generate message.")