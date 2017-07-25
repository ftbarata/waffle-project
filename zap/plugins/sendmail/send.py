# -*- coding: utf-8 -*-
# https://pypi.python.org/pypi/outbox

from zap.settings import *
from outbox import Outbox, Email, Attachment
import re, pymysql
from configobj import ConfigObj


class SendMail:

    def __init__(self, cfg):
        config = ConfigObj(cfg)
        host_db = config['host_db']
        self.user_db = config['user_db']
        self.passdb = config['passdb']
        self.db_name = config['db_name']
        self.db = pymysql.connect(host_db, self.user_db, self.passdb, self.db_name, autocommit=True)
        self.cursor = self.db.cursor()

    def close(self):
        self.cursor.close()
        self.db.close()

    def get_mail_sent_ok_message(self):
        self.cursor.execute("select mail_sent_ok from plugin_sendmail_runtime_messages")
        if self.cursor.fetchone()[0] is None:
            return 'E-mail enviado com sucesso. Verifique sua caixa de entrada.'
        else:
            return self.cursor.fetchone()[0]

    def get_mail_sent_fail_message(self):
        self.cursor.execute("select mail_sent_fail from plugin_sendmail_runtime_messages")
        if self.cursor.fetchone()[0] is None:
            return 'Houve um problema ao enviar o e-mail. Peço informar ao meu administrador.'
        else:
            return self.cursor.fetchone()[0]

    def get_invalid_mails_filtered_by_regex(self):
        self.cursor.execute("select invalid_mails_filtered_by_regex from plugin_sendmail_runtime_messages")
        if self.cursor.fetchone()[0] is None:
            return 'Os seguintes e-mails endereços de e-mail a seguir foram descartados porque são inválidos:'
        else:
            return self.cursor.fetchone()[0]

    def send(self, recipient_list, subject='Sem assunto',attachment_list='False'):

        emailRegex = re.compile(r'''([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+(\.[a-zA-Z]{2,4}))''', re.VERBOSE)
        valid_recipients = []
        invalid_recipients = []

        for i in recipient_list:
            email = emailRegex.findall(i)
            if email:
                valid_recipients.append(email)
            else:
                invalid_recipients.append(email)
        try:
            with Outbox(username=smtp_user, password=smtp_pass,
                        server=smtp_server, port=smtp_port, mode='SSL') as outbox:

                if attachment_list == 'False':
                    attachments = []
                    for i in attachment_list:
                        attachments.append(Attachment(str(i), fileobj=open(i, 'rb')))
                    outbox.send(Email(subject=subject, html_body='<b>SOME REALLY NICE SENTIMENT</b>', recipients=valid_recipients), attachments=attachments)
                    response = self.get_mail_sent_ok_message()
                    if len(invalid_recipients) > 0:
                        response = response + '\n' + self.get_invalid_mails_filtered_by_regex()
                        for invalid in invalid_recipients:
                            response = response + '\n' + invalid
                    return response
                else:
                    outbox.send(Email(subject=subject, html_body='<b>SOME REALLY NICE SENTIMENT</b>', recipients=valid_recipients))
                    response = self.get_mail_sent_ok_message()
                    if len(invalid_recipients) > 0:
                        response = response + '\n' + self.get_invalid_mails_filtered_by_regex()
                        for invalid in invalid_recipients:
                            response = response + '\n' + invalid
                    return response
        finally:
            pass
