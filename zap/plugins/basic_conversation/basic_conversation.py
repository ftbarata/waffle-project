# -*- coding: utf-8 -*-
from configobj import ConfigObj

from db_connector import BasicConversationDb
from zap.common.filter_input import FilterInput
from zap.common.unicode_to_ascii import UnicodeToAscii
from zap.lib.graphs_manager import GraphManager
from zap.plugins.delivery.pizza.delivery import Delivery as PizzaDelivery
from zap.settings import *
from ..admin_command_interface.admin_interface import AdminCommandInterface
from ..phishing_message.phishing import PhishingMessage
from ..quiz.quiz_basic import QuestionsRegister
from ..subscription.subscribe_via_chat import SubscribeViaChat


class BasicConversationFlow:

    def __init__(self, visitor_cellnumber, cfg):
        self.cfg = cfg
        config = ConfigObj(cfg)
        self.robot_cellnumber = config['phone']
        self.visitor_cellnumber = visitor_cellnumber
        self.calldb = BasicConversationDb(cfg)
        self.back_to_root_keyword = self.calldb.get_back_to_root_keyword()
        if self.back_to_root_keyword is None:
            self.back_to_root_keyword = ('fdsfdjskfjskjkdjdfk1314501', 'cxvmx94tkgvm')
        self.reverse_alias_key = ''
        self.record_chat = self.calldb.get_record_chat_flag()[0]
        self.yowsupmessage = ''

    def get_yowsupmessage(self):
        return self.yowsupmessage

    def send_message(self, message, exit_ok='false'):
        if message is None:
            message = 'Não foi cadastrada uma mensagem para esta opção. Informe ao meu administrador.'
        self.yowsupmessage = message
        if self.record_chat == 1:
            self.calldb.log_robot_message(self.visitor_cellnumber, self.robot_cellnumber, message)
        if str(exit_ok).lower() == 'true':
            pass
        self.calldb.close()

    def set_graph_position(self, node_name):
        self.calldb.set_graph_position_session(node_name, self.visitor_cellnumber)

    def answer(self):
        current_position = self.calldb.get_graph_position_session(self.visitor_cellnumber)
        node_message = self.calldb.get_node_message_cursor(current_position)
        if node_message is None:
            self.send_message('Não foi cadastrada uma mensagem para este nó. Informe ao meu administrador.', exit_ok='true')
        else:
            msg = node_message[0]
            msg = msg.replace("\\n", "\n")
            self.send_message(msg)

    def back_to_root(self):
        self.set_graph_position(root_node_name)
        current_position = self.calldb.get_graph_position_session(self.visitor_cellnumber)
        node_message = self.calldb.get_node_message_cursor(current_position[0])
        if node_message is None:
            self.send_message('Não foi cadastrada uma mensagem para a raiz. Informe ao meu administrador.', exit_ok='true')
        else:
            self.send_message(node_message[0], exit_ok='True')

    def navigation(self, unicode_message):
        ascii = UnicodeToAscii(unicode_message)
        ascii_message = ascii.unicode_to_ascii()
        input_msg_list_ascii = ascii_message.split()
        visitor_is_known = self.calldb.check_if_visitor_is_known(self.visitor_cellnumber)
        if visitor_is_known is None:
            p = PhishingMessage(self.visitor_cellnumber, self.cfg)
            p.mark_as_answered()
            p.close()
            presentation_message = self.calldb.get_presentation_message()
            if presentation_message is None:
                presentation_message = 'Não foi cadastrada uma mensagem de apresentação. Informe ao meu administrador.'
            else:
                presentation_message = presentation_message[0]
            self.set_graph_position(root_node_name)
            self.send_message(presentation_message)
        else:
            if self.record_chat == 1:
                self.calldb.log_visitor_message(self.visitor_cellnumber, self.robot_cellnumber, input_msg_list_ascii)
            position = self.calldb.get_graph_position_session(self.visitor_cellnumber)
            is_node_plugin = self.calldb.get_if_node_is_plugin(position[0])
            if is_node_plugin == 1:
                plugin_codename = self.calldb.get_plugin_codename(position[0])
                if plugin_codename is None:
                    pass
                elif plugin_codename == 'quiz':
                    plugin = QuestionsRegister(self.visitor_cellnumber, self.cfg)
                    self.send_message(plugin.command_interface(unicode_message))
                    plugin.close()
                elif plugin_codename == 'subscription_via_chat':
                    plugin = SubscribeViaChat(self.visitor_cellnumber, self.cfg)
                    self.send_message(plugin.command_interface(unicode_message))
                    plugin.close()
                elif plugin_codename == 'admin_interface':
                    plugin = AdminCommandInterface(self.visitor_cellnumber, self.cfg)
                    self.send_message(plugin.command_interface(unicode_message))
                    plugin.close()
                elif plugin_codename == 'delivery':
                    plugin = PizzaDelivery(self.visitor_cellnumber, self.cfg)
                    self.send_message(plugin.command_interface(unicode_message))
                    plugin.close()
            else:
                filter_common = FilterInput(input_msg_list_ascii)
                filtered_input_list_ascii = filter_common.filter()
                for word in filtered_input_list_ascii:
                    if str(word[0]).lower() == str(self.back_to_root_keyword[0]).lower():
                        self.back_to_root()
                        break
                else:
                    username = self.calldb.get_username()
                    gm = GraphManager(username[0])
                    gm.load_graph()
                    keywords_options = gm.get_sucessors(position[0])
                    if len(keywords_options) == 0:
                        llf_message = self.calldb.get_last_leaf_message()
                        if llf_message[0] is None:
                            llf_message = 'Não foi cadastrada uma mensagem para final de fluxo. Informe ao meu administrador.'
                        else:
                            llf_message = llf_message[0]
                        self.send_message(llf_message)
                    else:
                        matched_word_list = []
                        for word in filtered_input_list_ascii:
                            if word[0].lower() in keywords_options and word[0].lower() not in matched_word_list:
                                matched_word_list.append(word[0].lower())
                        if len(matched_word_list) == 1:
                            self.calldb.set_graph_position_session(matched_word_list[0], self.visitor_cellnumber)
                            self.answer()
                        elif len(matched_word_list) > 1:
                            self.send_message(self.calldb.get_multiple_keywords_matched_found_message()[0])
                        else:
                            tempdict = {}
                            for i in keywords_options:
                                templist = []
                                for j in self.calldb.get_node_aliases(i):
                                    templist.append(j[0])
                                tempdict[i] = templist
                            matched_alias_count_list = []
                            for word in filtered_input_list_ascii:
                                breaksignal = 0
                                for key in tempdict.keys():
                                    self.reverse_alias_key = key
                                    for alias in tempdict[key]:
                                        if word[0].lower() not in matched_alias_count_list and word[0].lower() == alias:
                                            matched_alias_count_list.append(word[0].lower())
                                            breaksignal = 1
                                            break
                                    if breaksignal == 1:
                                        break
                            if len(matched_alias_count_list) == 1:
                                self.calldb.set_graph_position_session(self.reverse_alias_key, self.visitor_cellnumber)
                                self.answer()
                            elif len(matched_alias_count_list) > 1:
                                self.send_message(self.calldb.get_multiple_aliases_matched_found_message()[0])
                            else:
                                msg = self.calldb.get_default_unknown_input_message()
                                if msg[0] is None:
                                    self.send_message('Não foi cadastrada uma mensagem para entrada desconhecida. Informe ao meu administrador.')
                                else:
                                    self.send_message(msg[0])

