import easyimap
from flask_mail import Message
from app import mail, app
from app.helpers import tweety_new, find_user_by_mail
from threading import Thread
import schedule
import time


host = "mail.quasarpm.com"
user = "tweety@quasarpm.com"
password = "300777Tweety"
mailbox = "inbox"


def tweety_mail():
    try:
        imapper = easyimap.connect(host, user, password, mailbox)
        unseen = imapper.unseen()
        if unseen is not None:
            for newmail in unseen:
                try:
                    basecode = newmail.title.split(' ')[0]
                    tr_subject = newmail.title.split(' ')[1]
                except:
                    basecode = 'undefined'
                    tr_subject = 'undefined'
                send_mail(
                    recipients=newmail.from_addr,
                    title = newmail.title,
                    body = tweety_new(find_user_by_mail(newmail.from_addr),
                                    basecode, tr_subject))
        imapper.quit()
    except:
        print('Tweety Mail Fail')
    
            

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_mail(recipients,title,body):
    msg = Message(subject=title,
                    recipients=[recipients],
                    sender='tweety@quasarpm.com')

    msg.body = body
    Thread(target=send_async_email, args=(app, msg)).start()

    

def async_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)
        


def mail_scheduler():
    
    schedule.every(15).seconds.do(tweety_mail)
    print('event scheduled')
    
    #schedule.logger.disabled = True
    #schedule.logger.error = True
    Thread(target=async_scheduler).start()
    

