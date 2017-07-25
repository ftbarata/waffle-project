# -*- coding: utf-8 -*-
import sys
sys.path.append('/home/zap/zap/plugins')
from configobj import ConfigObj
from basic_conversation.db_connector import BasicConversationDb


class ExitPlugin:

    def __init__(self, visitor_cellnumber, cfg):
        self.cfg = cfg
        config = ConfigObj(cfg)
        self.robot_cellnumber = config['phone']
        self.visitor_cellnumber = visitor_cellnumber
        self.calldb = BasicConversationDb(cfg)
        self.record_chat = self.calldb.get_record_chat_flag()[0]
        self.yowsupmessage = ''

    def exit(self):
        self.set_graph_position('root')
        self.answer()

    def answer(self):
        node_message = self.calldb.get_node_message_cursor('root')
        if node_message is None:
            self.send_message('Não foi cadastrada uma mensagem para este nó. Informe ao meu administrador.', exit_ok='true')
        else:
            self.send_message(node_message[0])

    def set_graph_position(self, node_name):
        self.calldb.set_graph_position_session(node_name, self.visitor_cellnumber)

    def send_message(self, message, exit_ok='false'):
        if message is None:
            message = 'Não foi cadastrada uma mensagem para esta opção. Informe ao meu administrador[2].'
        self.yowsupmessage = message
        if self.record_chat == 1:
            self.calldb.log_robot_message(self.visitor_cellnumber, self.robot_cellnumber, message)
        if str(exit_ok).lower() == 'true':
            pass
        self.calldb.close()
