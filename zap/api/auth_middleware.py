#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
import pymysql

api_host_db = 'localhost'
api_user_db = 'root'
api_passdb = '****'
api_db_name = 'zap_api'


class AuthMiddleWare:

    def __init__(self, api_username='', token=''):
        if api_username is None or token is None:
            self.args_ok = False
        else:
            self.args_ok = True
            self.username = api_username
            self.token = token
            self.db = pymysql.connect(api_host_db, api_user_db, api_passdb, api_db_name, autocommit=True)
            self.cursor = self.db.cursor()

    def close(self):
        self.cursor.close()
        self.db.close()

    def validate(self):
        if not self.args_ok:
            return 'missing_params'
        else:
            self.cursor.execute("select id from api_token where username = %s", self.username)
            id = self.cursor.fetchone()
            if id is None:
                return 'username_not_found'
            else:
                self.cursor.execute("select enabled from api_token where id = %s", id[0])
                enabled = self.cursor.fetchone()[0]
                if enabled == 0:
                    return 'username_is_disabled'
                else:
                    self.cursor.execute("select token from api_token where id = %s", id)
                    token = self.cursor.fetchone()[0]
                    if str(token).lower() == str(self.token).lower():
                        return 'token_match'
                    else:
                        return 'token_mismatch'

    def get_mongodb_name(self):
        self.cursor.execute("select mongodb_name from api_token where username = %s", self.username)
        return self.cursor.fetchone()[0]
