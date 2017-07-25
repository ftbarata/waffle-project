# -*- coding: utf-8 -*-
import pymysql
from configobj import ConfigObj


class Auth:

    def __init__(self, visitor_cellnumber, cfg):
        config = ConfigObj(cfg)
        host_db = config['host_db']
        self.user_db = config['user_db']
        self.passdb = config['passdb']
        self.db_name = config['db_name']
        self.db = pymysql.connect(host_db, self.user_db, self.passdb, self.db_name, autocommit=True, charset='utf8')
        self.cursor = self.db.cursor()
        self.visitor_cellnumber = visitor_cellnumber

    def get_permission_level(self):
        self.cursor.execute("select perm_id from plugin_auth where administrator_cellnumber = %s", self.visitor_cellnumber)
        queryset = self.cursor.fetchone()
        if queryset is None:
            return False
        else:
            return queryset[0]

    def close(self):
        self.cursor.close()
        self.db.close()

    def get_authorization(self, access_level='1'):
        current_db_perm_level = self.get_permission_level()
        if str(current_db_perm_level) == str(access_level):
            return True
        else:
            return False

    def get_access_denied_message(self):
        self.cursor.execute("select access_denied from plugin_auth_messages")
        queryset = self.cursor.fetchone()
        if queryset is None:
            return 'Acesso negado. Você não tem permissão para acessar esta área administrativa.'
        else:
            return queryset[0]

    def get_access_granted_message(self):
        self.cursor.execute("select access_granted from plugin_auth_messages")
        queryset = self.cursor.fetchone()
        if queryset is None:
            return 'O acesso à esta área restrita foi concedido. Seu número foi encontrado na base de dados de administradores, bem vindo(a).'
        else:
            return queryset[0]

    def add_administrator_cellnumber(self, admin_cellnumber, perm_id='1'):
        self.cursor.execute("select id from plugin_auth where administrator_cellnumber = %s", admin_cellnumber)
        queryset = self.cursor.fetchone()
        if queryset is None:
            self.cursor.execute("insert into plugin_auth(administrator_cellnumber, perm_id, being_added_by) values(%s, %s, %s)", (admin_cellnumber, perm_id, self.visitor_cellnumber))
            return True
        else:
            return False

    def update_administrator_name(self, name):
        self.cursor.execute("select being_added_by from plugin_auth where being_added_by = %s", self.visitor_cellnumber)
        being_added_by = self.cursor.fetchone()[0]
        self.cursor.execute("update plugin_auth set name = %s where being_added_by = %s", (name, being_added_by))
        self.cursor.execute("update plugin_auth set being_added_by = NULL where being_added_by = %s", being_added_by)

    def get_administrator_name(self, admin_cellnumber):
        self.cursor.execute("select name from plugin_auth where administrator_cellnumber = %s", admin_cellnumber)
        return self.cursor.fetchone()

    def get_administrators_list(self):
        self.cursor.execute("select administrator_cellnumber from plugin_auth")
        queryset = self.cursor.fetchall()
        if len(queryset) == 0:
            return None
        else:
            tempdict = {}
            for i in queryset:
                self.cursor.execute("select name from plugin_auth where administrator_cellnumber = %s", i)
                name = self.cursor.fetchone()[0]
                if name is None:
                    name = 'Nome não cadastrado'
                tempdict[i] = name
        return tempdict

    def remove_administrator(self, admin_cellnumber):
        self.cursor.execute("select id from plugin_auth where administrator_cellnumber = %s", admin_cellnumber)
        queryset = self.cursor.fetchone()
        if queryset is not None:
            self.cursor.execute("delete from plugin_auth where administrator_cellnumber = %s", admin_cellnumber)
            return True
        else:
            return False
