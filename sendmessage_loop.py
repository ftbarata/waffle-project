#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
import sys
from datetime import *
from zap.plugins.phishing_message.phishing import PhishingMessage
from configobj import ConfigObj
from run2 import Client


def send_phishing_messages(phone, cfg):
    p = PhishingMessage(phone, cfg)
    message = p.get_phishing_message_content()
    if message is not None:
        recipients_list = p.get_unanswered_recipients_list()
        if len(recipients_list) > 0:
            p.close()
            for i in recipients_list:
                s = Client()
                print(i[0])
                s.send_message(i[0], message[0])
                currdate = date.today()
                a = datetime.now()
                currtime = a.strftime('%H:%M:%S')
                print('{} {} Para: {}'.format(currdate, currtime, i[0]))
                print('Mensagem: {}'.format(message[0]))
        else:
            p.clear_phishing_message_spool()
            p.close()
    else:
        currdate = date.today()
        a = datetime.now()
        currtime = a.strftime('%H:%M:%S')
        print('{} {} Nothing to send.'.format(currdate, currtime))


if len(sys.argv) == 2:
    cfg = sys.argv[1]
    config = ConfigObj(cfg)
    phone = config['phone']
    # IN SECONDS
    phishing_interval = 3600
    send_phishing_messages(phone, cfg)

else:
    print('Syntax: {} <config_file>'.format(sys.argv[0]))

