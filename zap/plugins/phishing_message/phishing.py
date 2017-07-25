# -*- coding: utf-8 -*-
import pymysql
from configobj import ConfigObj


class PhishingMessage:

    def __init__(self, visitor_cellnumber, cfg):
        config = ConfigObj(cfg)
        host_db = config['host_db']
        self.user_db = config['user_db']
        self.passdb = config['passdb']
        self.db_name = config['db_name']
        self.db = pymysql.connect(host_db, self.user_db, self.passdb, self.db_name, autocommit=True)
        self.cursor = self.db.cursor()
        self.visitor_cellnumber = visitor_cellnumber

    def close(self):
        self.cursor.close()
        self.db.close()

    def send_phishing_message_to_spool(self, unicode_message):
        self.cursor.execute("select id from plugin_phishing_message")
        queryset = self.cursor.fetchone()
        if queryset is None:
            self.cursor.execute("insert into plugin_phishing_message(created_by, message) values(%s, %s)", (self.visitor_cellnumber, unicode_message))
            return True
        else:
            return False

    def get_phishing_message_status(self):
        self.cursor.execute("select id from plugin_phishing_message")
        queryset = self.cursor.fetchone()
        if queryset is None:
            return True
        else:
            return False

    def get_phishing_message_content(self):
        if not self.get_phishing_message_status():
            self.cursor.execute("select message from plugin_phishing_message")
            return self.cursor.fetchone()
        else:
            return None

    def get_phishing_message_created_by(self):
        if not self.get_phishing_message_status():
            self.cursor.execute("select created_by from plugin_phishing_message")
            return self.cursor.fetchone()
        else:
            return None

    def get_phishing_message_created_at(self):
        if not self.get_phishing_message_status():
            self.cursor.execute("select created_at from plugin_phishing_message")
            return self.cursor.fetchone()
        else:
            return None

    def get_current_phishing_recipients_count(self):
        self.cursor.execute("select id from plugin_phishing where answered is NULL")
        return len(self.cursor.fetchall())

    def mark_as_answered(self):
        self.cursor.execute("select id from plugin_phishing where cellnumber = %s and answered != 1", self.visitor_cellnumber)
        queryset = self.cursor.fetchone()
        if queryset is not None:
            self.cursor.execute("update plugin_phishing set answered = 1 where cellnumber = %s", self.visitor_cellnumber)

    def get_unanswered_recipients_list(self):
        self.cursor.execute("select cellnumber from plugin_phishing where answered != 1 or answered is NULL")
        return self.cursor.fetchall()

    def clear_phishing_message_spool(self):
        self.cursor.execute("delete from plugin_phishing_message")