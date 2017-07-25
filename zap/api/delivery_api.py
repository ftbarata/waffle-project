#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
import falcon
from bson.json_util import dumps, loads
from pymongo import MongoClient
from bson.objectid import ObjectId
import rstr
from auth_middleware import AuthMiddleWare
from zap.common.unicode_to_ascii import UnicodeToAscii


class Resource(object):

    def on_get(self, req, resp, operation):
        if req.method == 'GET':
            username = req.get_param('username')
            token = req.get_param('token')
            a = AuthMiddleWare(username, token)
            auth_status = a.validate()
            if auth_status == 'username_not_found':
                resp.body = falcon.HTTPError(falcon.HTTP_403, title='Usuario de api nao existe.').to_json()
            elif auth_status == 'username_is_disabled':
                resp.body = falcon.HTTPError(falcon.HTTP_403, title='Usuario de api inativo.').to_json()
            elif auth_status == 'missing_params':
                resp.body = falcon.HTTPError(falcon.HTTP_403, title='Faltam parametros.').to_json()
            elif auth_status == 'token_mismatch':
                resp.body = falcon.HTTPError(falcon.HTTP_403, title='Token invalido.').to_json()
            elif auth_status == 'token_match':
                if operation == 'get_dataset_bson':
                    collection = req.get_param('collection')
                    if collection is not None:
                        mongodb_name = a.get_mongodb_name()
                        a.close()
                        mongo = MongoConn(mongodb_name, collection)
                        resp.body = mongo.get_dataset_bson()
                        resp.status = falcon.HTTP_200
                    else:
                        resp.body = "Nao foi informado o parametro collection na chamada GET."
                        resp.status = falcon.HTTP_403
                elif operation == 'get_dataset_json':
                    collection = req.get_param('collection')
                    if collection is not None:
                        mongodb_name = a.get_mongodb_name()
                        a.close()
                        mongo = MongoConn(mongodb_name, collection)
                        resp.body = mongo.get_dataset_json()
                        resp.status = falcon.HTTP_200
                    else:
                        resp.body = "Nao foi informado o parametro collection na chamada GET."
                        resp.status = falcon.HTTP_403
                elif operation == 'drop_dataset':
                    collection = req.get_param('collection')
                    if collection is not None:
                        mongodb_name = a.get_mongodb_name()
                        a.close()
                        mongo = MongoConn(mongodb_name, collection)
                        resp.body = mongo.drop_dataset()
                        resp.status = falcon.HTTP_200
                    else:
                        resp.body = "Nao foi informado o parametro collection na chamada GET."
                        resp.status = falcon.HTTP_403
                elif operation == 'update_one_by_oid':
                    oid = req.get_param('oid')
                    key = req.get_param('key')
                    value = req.get_param('value')
                    collection = req.get_param('collection')
                    if oid is None or key is None or value is None or collection is None:
                        resp.body = "Faltam parametros para a funcao update_one_by_oid."
                        resp.status = falcon.HTTP_403
                    else:
                        mongodb_name = a.get_mongodb_name()
                        a.close()
                        mongo = MongoConn(mongodb_name, collection)
                        resp.body = mongo.update_one_by_oid(oid,key,value)
                        resp.status = falcon.HTTP_200
                elif operation == 'delete_one_by_oid':
                    oid = req.get_param('oid')
                    collection = req.get_param('collection')
                    if oid is None or collection is None:
                        resp.body = "Faltam parametros para a funcao delete_one_by_oid."
                        resp.status = falcon.HTTP_403
                    else:
                        mongodb_name = a.get_mongodb_name()
                        a.close()
                        mongo = MongoConn(mongodb_name, collection)
                        resp.body = mongo.delete_one_by_oid(oid)
                        resp.status = falcon.HTTP_200
                elif operation == 'insert_one':
                    key = req.get_param('key')
                    value = req.get_param('value')
                    collection = req.get_param('collection')
                    if key is None or value is None or collection is None:
                        resp.body = "Faltam parametros para a funcao insert_one."
                        resp.status = falcon.HTTP_403
                    else:
                        mongodb_name = a.get_mongodb_name()
                        a.close()
                        mongo = MongoConn(mongodb_name, collection)
                        resp.body = mongo.insert_one_via_get(key,value)
                        resp.status = falcon.HTTP_200
                else:
                    a.close()
                    resp.body = falcon.HTTPError(falcon.HTTP_403, title='Operacao invalida.').to_json()
                    resp.status = falcon.HTTP_200
            else:
                a.close()
                resp.body = falcon.HTTPError(falcon.HTTP_403, title='Erro interno.').to_json()

    def on_post(self, req, resp, operation):
        if req.method == 'POST':
            username = req.get_param('username')
            token = req.get_param('token')
            a = AuthMiddleWare(username, token)
            auth_status = a.validate()
            if auth_status == 'username_not_found':
                a.close()
                resp.body = falcon.HTTPError(falcon.HTTP_403, title='Usuario de api nao existe.').to_json()
                resp.status = falcon.HTTP_403
            elif auth_status == 'username_is_disabled':
                a.close()
                resp.body = falcon.HTTPError(falcon.HTTP_403, title='Usuario de api inativo.').to_json()
                resp.status = falcon.HTTP_403
            elif auth_status == 'missing_params':
                a.close()
                resp.body = falcon.HTTPError(falcon.HTTP_403, title='Faltam parametros.').to_json()
                resp.status = falcon.HTTP_403
            elif auth_status == 'token_mismatch':
                a.close()
                resp.body = falcon.HTTPError(falcon.HTTP_403, title='Token invalido.').to_json()
                resp.status = falcon.HTTP_403
            elif auth_status == 'token_match':
                if operation == 'insert_one':
                    collection = req.get_param('collection')
                    if collection is not None:
                        body = req.stream.read()
                        mongodb_name = a.get_mongodb_name()
                        a.close()
                        mongo = MongoConn(mongodb_name, collection)
                        resp.body = mongo.insert_one_via_post(body)
                    else:
                        resp.body = "Nao foi informado o parametro collection."
                        resp.status = falcon.HTTP_403
                elif operation == 'insert_bulk':
                    collection = req.get_param('collection')
                    if collection is not None:
                        body = req.stream.read()
                        mongodb_name = a.get_mongodb_name()
                        a.close()
                        mongo = MongoConn(mongodb_name, collection)
                        resp.body = mongo.insert_bulk(body)
                    else:
                        resp.body = "Nao foi informado o parametro collection."
                        resp.status = falcon.HTTP_403
                else:
                    a.close()
                    resp.body = falcon.HTTPError(falcon.HTTP_403, title='Operacao invalida.').to_json()
                    resp.status = falcon.HTTP_200
            else:
                a.close()
                resp.body = falcon.HTTPError(falcon.HTTP_403, title='Erro interno.').to_json()


class MongoConn:

    def __init__(self, mongodb_name, collection):
        client = MongoClient()
        self.db = client[mongodb_name]
        self.collection_name = collection

    def get_dataset_bson(self):
        cursor = self.db[self.collection_name].find()
        response = ''
        for i in cursor:
            response += str(dumps(i)) + "\n\n"
        if len(response) == 0:
            response = "Dataset vazio."
        return response

    def get_dataset_json(self):
        cursor = self.db[self.collection_name].find()
        response = ''
        for i in cursor:
            response += str(i) + "\n\n"
        if len(response) == 0:
            response = "Dataset vazio."
        return response

    def insert_one_via_post(self, body):
        insert = self.db[self.collection_name].insert_one(loads(body))
        return str(insert.inserted_id)

    def insert_one_via_get(self, key, value):
        insert = self.db[self.collection_name].insert_one({key:value})
        return str(insert.inserted_id)

    def drop_dataset(self):
        self.db[self.collection_name].drop()
        return "Todos os dados foram apagados."

    def insert_bulk(self, body):
        insert = self.db[self.collection_name].insert_many(loads(body))
        return str(insert.inserted_ids)

    def update_one_by_oid(self, oid, key, value):
        update = self.db[self.collection_name].update_one({"_id": ObjectId(oid)}, {"$set": {key: value}})
        return str(update.modified_count)

    def delete_one_by_oid(self, oid):
        delete = self.db[self.collection_name].delete_one({"_id": ObjectId(oid)})
        return str(delete.deleted_count)

    ### Functions below are NOT for webservice calls #################################################################

    def get_convert_collection_to_dict(self, state):
        cursor = self.db[self.collection_name].find({"state": state}, {"_id": 0})
        for i in cursor:
            if i['state'] == state:
                try:
                    convert_collection_to_dict = i['convert_collection_to_dict']
                    return convert_collection_to_dict
                except KeyError:
                    return '0'

    def get_dict_to_str(self, collection):
        cursor = self.db[collection].find({}, {"_id": 0, "value":0, "short_name": 0})
        resp = "\n"
        for i in cursor:
            resp += i.keys()[0].encode(encoding='utf-8') + ": " + i.values()[0].encode(encoding='utf-8') + "\n\n"
        return resp

    def get_override_collection_to_str(self, state, override_collection):
        cursor = self.db[override_collection].find({}, {"_id": 0})
        resp = "\n"
        for i in cursor:
            option = i['option']
            description = i['description']
            resp += option.encode(encoding='utf-8') + ": " + description.encode(encoding='utf-8') + "\n\n"
        return resp

    def get_collection(self, state):
        cursor = self.db[self.collection_name].find({"state":state}, {"_id": 0})
        for i in cursor:
            if i['state'] == state:
                collection = i['collection']
                return collection

    def get_use_pre_msg(self, state):
        cursor = self.db[self.collection_name].find({"state": state}, {"_id": 0})
        for i in cursor:
            if i['state'] == state:
                try:
                    use_pre_msg = i['use_pre_msg']
                    return use_pre_msg
                except KeyError:
                    return '0'

    def get_pre_msg(self, state):
        cursor = self.db[self.collection_name].find({"state":state}, {"_id": 0})
        for i in cursor:
            if i['state'] == state:
                try:
                    pre_msg = i['pre_msg']
                    return pre_msg
                except KeyError:
                    return ""

    def get_post_msg(self, state):
        cursor = self.db[self.collection_name].find({"state": state}, {"_id": 0})
        for i in cursor:
            if i['state'] == state:
                try:
                    post_msg = i['post_msg']
                    return post_msg
                except KeyError:
                    return ""

    def get_use_post_msg(self, state):
        cursor = self.db[self.collection_name].find({"state": state}, {"_id": 0})
        for i in cursor:
            if i['state'] == state:
                try:
                    use_post_msg = i['use_post_msg']
                    return use_post_msg
                except KeyError:
                    return '0'

    def get_free_text_name_field(self, state):
        cursor = self.db[self.collection_name].find({"state": state}, {"_id": 0, "free_text_name_field": 1, "state": 1})
        for i in cursor:
            if i['state'] == state:
                try:
                    free_text_name_field = i['free_text_name_field']
                    return free_text_name_field
                except KeyError:
                    return ""

    def get_return_message(self, state, save_flag=1):
        a = self.get_use_pre_msg(state)
        b = self.get_use_post_msg(state)
        c = self.get_convert_collection_to_dict(state)
        if str(a) == "1":
            if str(b) == "1" or str(c) == "1":
                pre_msg = self.get_pre_msg(state) + "\n"
            else:
                pre_msg = self.get_pre_msg(state)
        else:
            pre_msg = ""
        if str(b) == "1":
            post_msg = self.get_post_msg(state)
        else:
            post_msg = ""
        if save_flag == "0":
            override_collection = self.get_next_state_override_collection(state)
            dict_resp = self.get_override_collection_to_str(state, override_collection)
        else:
            if str(c) == "1":
                collection = self.get_collection(state)
                dict_resp = self.get_dict_to_str(collection)
            else:
                dict_resp = ""

        return pre_msg.encode(encoding='utf-8') + dict_resp + post_msg.encode(encoding='utf-8')

    def get_next_state(self, state):
        cursor = self.db[self.collection_name].find({"state": state}, {"_id": 0})
        for i in cursor:
            try:
                if i['state'] == state:
                    try:
                        next_state = i['next_state']
                        if len(next_state) == 0:
                            return "root"
                        else:
                            return next_state
                    except KeyError:
                        return state
            except KeyError:
                return "root"

    def get_restart_keyword(self):
        cursor = self.db[self.collection_name].find({}, {"cancel_and_restart_keyword": 1, "_id": 0})
        for i in cursor:
            if len(i) > 0:
                try:
                    restart_keyword = i['cancel_and_restart_keyword']
                    return restart_keyword
                except KeyError:
                    return ""

    def get_save_flag(self, current_state):
        cursor = self.db[self.collection_name].find({"state": current_state}, {"_id": 0})
        for i in cursor:
            try:
                if i['state'] == current_state:
                    try:
                        save = i['save']
                        if len(save) == 0:
                            return "1"
                        else:
                            return save
                    except KeyError:
                        return "null"
            except KeyError:
                return "null_2"

    def get_next_state_override(self, input_msg_list_ascii, collection):
        cursor = self.db[collection].find({}, {"_id": 0})
        for i in cursor:
            option = i['option']
            next_state = i['next_state_override']
            for msg in input_msg_list_ascii:
                if str(msg).encode(encoding='utf-8').lower() == str(option).lower():
                    return next_state
        return "null"

    def get_next_state_override_collection(self, current_state):
        cursor = self.db[self.collection_name].find({"state": current_state}, {"_id": 0})
        for i in cursor:
            try:
                if i['state'] == current_state:
                    try:
                        next_state_override_collection = i['next_state_override_collection']
                        if len(next_state_override_collection) == 0:
                            return "null"
                        else:
                            return next_state_override_collection
                    except KeyError:
                        return "null"
            except KeyError:
                return "null_2"

    def get_codpedido(self, visitor_cellnumber):
        cursor = self.db[self.collection_name].find({"visitor_cellnumber": visitor_cellnumber}, {"codpedido":1, "_id":0})
        for i in cursor:
            if len(i) == 1:
                try:
                    codpedido = i['codpedido']
                    return codpedido
                except KeyError:
                    codpedido = rstr.normal(8).replace(" ", "").upper()
                    self.db[self.collection_name].insert_one({"codpedido": codpedido, "visitor_cellnumber": visitor_cellnumber})
                    return codpedido
        codpedido = rstr.normal(8).replace(" ", "").upper()
        self.db[self.collection_name].insert_one({"codpedido": codpedido, "visitor_cellnumber": visitor_cellnumber})
        return codpedido

    def gen_new_codpedido(self, visitor_cellnumber, codpedido_atual):
        novo_codpedido = rstr.normal(8).replace(" ", "").upper()
        self.db[self.collection_name].find_one_and_update({"visitor_cellnumber": visitor_cellnumber, "codpedido": codpedido_atual}, {"$set": {"codpedido": novo_codpedido}})
        return novo_codpedido

    def get_variable_state(self, visitor_cellnumber):
        cursor = self.db[self.collection_name].find({"visitor_cellnumber": visitor_cellnumber}, {"_id": 0})
        if cursor.count() == 0:
            self.db[self.collection_name].insert_one({"visitor_cellnumber": visitor_cellnumber, "variable_state":"root"})
            return 'root'
        else:
            for i in cursor:
                try:
                    variable_state = i['variable_state']
                    if variable_state == "null" or variable_state is None:
                        return "root"
                    else:
                        return variable_state
                except KeyError:
                    return 'root'

    def update_variable_state(self, visitor_cellnumber, new_state):
        cursor = self.db[self.collection_name].find({"visitor_cellnumber": visitor_cellnumber})
        for i in cursor:
            if len(i) == 3:
                oid = i["_id"]
                if new_state is not None:
                    return self.update_one_by_oid(oid, "variable_state", new_state)
                else:
                    return self.update_one_by_oid(oid, "variable_state", 'root')

    def get_input_type(self, state):
        cursor = self.db[self.collection_name].find({"state": state}, {"_id": 0})
        for i in cursor:
            try:
                if i['state'] == state:
                    try:
                        input_type = i['input_type']
                        return input_type
                    except KeyError:
                        return ""
            except KeyError:
                return ""

    @staticmethod
    def get_short_name(cursor_instance):
        try:
            short_name = cursor_instance['short_name']
            return short_name
        except KeyError:
            return ""

    def get_previous_state(self, state):
        cursor = self.db[self.collection_name].find({"state": state}, {"_id": 0})
        for i in cursor:
            if i['state'] == state:
                try:
                    previous_state = i['previous_state']
                    if previous_state == "":
                        return state
                    else:
                        return previous_state
                except KeyError:
                    return state

    def update_venda_by_codpedido(self, codpedido, key, value):
        cursor = self.db['_venda'].find({"codpedido": codpedido})
        if cursor.count() == 0:
            insert = self.db['_venda'].insert_one({"codpedido": codpedido, key: value})
            return insert.inserted_id
        else:
            update = self.db['_venda'].update_one({"codpedido": codpedido}, {"$set": {key: value}})
            return str(update.modified_count)

    def save_input(self, state, unicode_message, codpedido):
        previous_state = self.get_previous_state(state)
        input_type = self.get_input_type(previous_state)
        if input_type == 'menu_choice':
            ascii = UnicodeToAscii(unicode_message)
            ascii_message = ascii.unicode_to_ascii()
            input_msg_list_ascii = ascii_message.split()
            collection = self.get_collection(previous_state)
            if collection is None:
                collection = self.get_collection(state)
            cursor = self.db[collection].find({}, {"_id": 0})
            for i in cursor:
                for msg in input_msg_list_ascii:
                    conv_msg = str(msg).encode(encoding='utf-8')
                    if conv_msg == str(i.keys()[0]).encode(encoding='utf-8').lower():
                        self.update_venda_by_codpedido(codpedido, conv_msg, self.get_short_name(i))
                        return True

            return "Opção inválida."

        elif input_type == 'free_text':
            previous_state = self.get_previous_state(state)
            free_text_name_field = self.get_free_text_name_field(previous_state)
            self.update_venda_by_codpedido(codpedido, free_text_name_field, str(unicode_message).encode(encoding='utf-8'))
            return True

        else:
            return True

