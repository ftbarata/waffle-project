# -*- coding: utf-8 -*-
import pymysql, subprocess
# import sys
# sys.path.append('/home/zap')
from configobj import ConfigObj


class BasicConversationDb:

    def __init__(self, cfg):
        config = ConfigObj(cfg)
        host_db = config['host_db']
        self.user_db = config['user_db']
        self.passdb = config['passdb']
        self.db_name = config['db_name']
        self.robot_cellnumber = config['phone']
        self.db = pymysql.connect(host_db, self.user_db, self.passdb, self.db_name, autocommit = True)
        self.cursor = self.db.cursor()

    def close(self):
        self.cursor.close()
        self.db.close()

    def get_presentation_message(self):
        self.cursor.execute("select presentation_message from basic_conversation_plugin_main")
        return self.cursor.fetchone()

    def get_node_message_cursor(self, position):
        self.cursor.execute("select graph_node_message from basic_conversation_plugin_nodes_messages where graph_node_name = %s", position)
        return self.cursor.fetchone()

    def get_node_messages(self, node_name):
        if node_name == 'NULL':
            subprocess.call(['mysql', '-u{}'.format(self.user_db), '-p{}'.format(self.passdb), '{}'.format(self.db_name), '-e','select graph_node_name as Node, graph_node_message as Message from basic_conversation_plugin_nodes_messages \G;'])
        else:
            subprocess.call(['mysql', '-u{}'.format(self.user_db), '-p{}'.format(self.passdb), '{}'.format(self.db_name), '-e','select graph_node_name as Node, graph_node_message as Message from basic_conversation_plugin_nodes_messages where graph_node_name = \'{}\' ;'.format(node_name)])

    def check_if_visitor_is_known(self, visitor_cellnumber):
        self.cursor.execute("select id from session where visitor_cellnumber = %s", visitor_cellnumber)
        return self.cursor.fetchone()

    def set_new_user(self, username, firstname, lastname, email, password):
        self.cursor.execute("insert into user_info(username, firstname, lastname, email, robot_cellnumber, password, active)"
                            "values(%s, %s, %s, %s, %s, %s, %s)",
                            (username, firstname, lastname, email, self.robot_cellnumber, password, '1'))

    def set_node_message(self, node, message):
        test = self.cursor.execute("select id from basic_conversation_plugin_nodes_messages where graph_node_name = %s", node)
        if test == 0:
            self.cursor.execute("insert into basic_conversation_plugin_nodes_messages(graph_node_name, graph_node_message) values(%s, %s)", (node, message))
        else:
            self.cursor.execute("update basic_conversation_plugin_nodes_messages set graph_node_message = %s where graph_node_name = %s", (message, node))

    def del_node_message(self, node):
        self.cursor.execute("delete from basic_conversation_plugin_nodes_messages where graph_node_name = %s", node)

    def del_all_nodes_messages(self):
        self.cursor.execute("delete from basic_conversation_plugin_nodes_messages")

    def set_session_config(self, session_timeout, record_chat, record_chat_days, days_visitor_is_known):
        self.cursor.execute("select id from session_config")
        test = self.cursor.fetchone()
        if str(test) == 'None' or test == 0:
            self.cursor.execute("insert into session_config(session_timeout_seconds, record_chat,"
                                " record_chat_days, days_visitor_is_known) "
                                "values(%s, %s, %s, %s)",(session_timeout, record_chat, record_chat_days, days_visitor_is_known))
        else:
            self.cursor.execute("update session_config set session_timeout_seconds = %s", session_timeout)
            self.cursor.execute("update session_config set record_chat = %s", record_chat)
            self.cursor.execute("update session_config set record_chat_days = %s", record_chat_days)
            self.cursor.execute("update session_config set days_visitor_is_known = %s", days_visitor_is_known)

    def set_main_messages(self, field, message):
        self.cursor.execute("select id from basic_conversation_plugin_main")
        if str(self.cursor.fetchone()) == 'None':
            if field == 'presentation_message':
                self.cursor.execute("insert into basic_conversation_plugin_main(presentation_message) values(%s)", message)
            elif field == 'goodbye_message':
                self.cursor.execute("insert into basic_conversation_plugin_main(goodbye_message) values(%s)", message)
            elif field == 'last_leaf_message':
                self.cursor.execute("insert into basic_conversation_plugin_main(last_leaf_message) values(%s)", message)
            elif field == 'alias_found_message':
                self.cursor.execute("insert into basic_conversation_plugin_main(alias_found_message) values(%s)", message)
            elif field == 'multiple_keywords_matched_message':
                self.cursor.execute("insert into basic_conversation_plugin_main(multiple_keywords_matched_message) values(%s)", message)
            elif field == 'multiple_aliases_found_message':
                self.cursor.execute("insert into basic_conversation_plugin_main(multiple_aliases_found_message) values(%s)",  message)
            elif field == 'default_unknown_input_message':
                self.cursor.execute("insert into basic_conversation_plugin_main(default_unknown_input_message) values(%s)",  message)
            elif field == 'back_to_root_keyword':
                self.cursor.execute("insert into basic_conversation_plugin_main(back_to_root_keyword) values(%s)",  message)
            else:
                print('Incorrect field.')
        else:
            if field == 'presentation_message':
                self.cursor.execute("update basic_conversation_plugin_main set presentation_message = %s", message)
            elif field == 'goodbye_message':
                self.cursor.execute("update basic_conversation_plugin_main set goodbye_message = %s", message)
            elif field == 'last_leaf_message':
                self.cursor.execute("update basic_conversation_plugin_main set last_leaf_message = %s", message)
            elif field == 'alias_found_message':
                self.cursor.execute("update basic_conversation_plugin_main set alias_found_message = %s", message)
            elif field == 'multiple_keywords_matched_message':
                self.cursor.execute("update basic_conversation_plugin_main set multiple_keywords_matched_message = %s", message)
            elif field == 'multiple_aliases_found_message':
                self.cursor.execute("update basic_conversation_plugin_main set multiple_aliases_found_message = %s", message)
            elif field == 'default_unknown_input_message':
                self.cursor.execute("update basic_conversation_plugin_main set default_unknown_input_message = %s", message)
            elif field == 'back_to_root_keyword':
                self.cursor.execute("update basic_conversation_plugin_main set back_to_root_keyword = %s", message)
            else:
                print('Incorrect field.')

    def del_all_main_messages(self):
            self.cursor.execute("delete from basic_conversation_plugin_main")

    def set_graph_position_session(self, node_name, visitor_cellnumber):
        test = self.get_graph_position_session(visitor_cellnumber)
        if test is None:
            self.cursor.execute("insert into session(visitor_cellnumber, graph_position) "
                                "values(%s, %s)", (visitor_cellnumber, node_name))
        else:
            self.cursor.execute("update session set graph_position = %s where visitor_cellnumber = %s", (node_name, visitor_cellnumber))

    def get_graph_position_session(self, visitor_cellnumber):
        self.cursor.execute("select graph_position from session where visitor_cellnumber = %s ", visitor_cellnumber)
        return self.cursor.fetchone()

    def get_username(self):
        self.cursor.execute("select username from user_info")
        return self.cursor.fetchone()

    def get_last_leaf_message(self):
        self.cursor.execute("select last_leaf_message from basic_conversation_plugin_main")
        return self.cursor.fetchone()

    def get_record_chat_flag(self):
        self.cursor.execute("select record_chat from session_config")
        return self.cursor.fetchone()

    def get_alias_found_message(self):
        self.cursor.execute("select alias_found_message from basic_conversation_plugin_main")
        return self.cursor.fetchone()

    def drop_database_user(self):
        subprocess.call(['mysql', '-u{}'.format(self.user_db), '-p{}'.format(self.passdb), '-e','drop database {};'.format(self.db_name)])

    def show_main_messages(self, field):
        if field == 'NULL':
            subprocess.call(['mysql', '-u{}'.format(self.user_db), '-p{}'.format(self.passdb), '{}'.format(self.db_name), '-e','select * from basic_conversation_plugin_main \G;'])
        else:
            subprocess.call(['mysql', '-u{}'.format(self.user_db), '-p{}'.format(self.passdb), '{}'.format(self.db_name), '-e','select {} from basic_conversation_plugin_main \G;'.format(field)])

    def get_sessions(self, visitor_cellnumber):
        if visitor_cellnumber == 'NULL':
            subprocess.call(['mysql', '-u{}'.format(self.user_db), '-p{}'.format(self.passdb), '{}'.format(self.db_name), '-e', 'select visitor_cellnumber as Visitante, first_ever_hello as \'Primeira mensagem de todas\', last_started_session as \'Ultima sessao iniciada\', last_message as \'Ultima mensagem\', graph_position as \'Posicao atual\' from session;'])
        else:
            subprocess.call(['mysql', '-u{}'.format(self.user_db), '-p{}'.format(self.passdb), '{}'.format(self.db_name), '-e', 'select visitor_cellnumber as Visitante, first_ever_hello as \'Primeira mensagem de todas\', last_started_session as \'Ultima sessao iniciada\', last_message as \'Ultima mensagem\', graph_position as \'Posicao atual\' from session  where visitor_cellnumber = {};'.format(visitor_cellnumber)])

    def clear_sessions(self, visitor_cellnumber):
        if visitor_cellnumber == 'NULL':
            self.cursor.execute("delete from session")
        else:
            self.cursor.execute("delete from session where visitor_cellnumber", visitor_cellnumber)

    def get_multiple_keywords_matched_found_message(self):
        self.cursor.execute("select multiple_keywords_matched_message from basic_conversation_plugin_main")
        return self.cursor.fetchone()

    def get_multiple_aliases_matched_found_message(self):
        self.cursor.execute("select multiple_aliases_found_message from basic_conversation_plugin_main")
        return self.cursor.fetchone()

    def get_default_unknown_input_message(self):
        self.cursor.execute("select default_unknown_input_message from basic_conversation_plugin_main")
        return self.cursor.fetchone()

    def get_back_to_root_keyword(self):
        self.cursor.execute("select back_to_root_keyword from basic_conversation_plugin_main")
        return self.cursor.fetchone()

    def get_node_aliases(self, node_name):
        self.cursor.execute("select graph_node_alias from basic_conversation_plugin_nodes_aliases inner join "
                            "basic_conversation_plugin_nodes_messages on basic_conversation_plugin_nodes_aliases.bcpnm_id "
                            "= basic_conversation_plugin_nodes_messages.id "
                            "where basic_conversation_plugin_nodes_messages.graph_node_name = %s ", node_name)
        return self.cursor.fetchall()

    def add_node_alias(self, node_name, alias):
        self.cursor.execute("select id from basic_conversation_plugin_nodes_messages where graph_node_name = %s", node_name)
        bcpnm_id = self.cursor.fetchone()[0]
        self.cursor.execute("insert into basic_conversation_plugin_nodes_aliases(bcpnm_id,graph_node_alias) values(%s,%s)", (bcpnm_id, alias))

    def del_node_alias(self, node_name):
        self.cursor.execute("select id from basic_conversation_plugin_nodes_messages where graph_node_name = %s", node_name)
        bcpnm_id = self.cursor.fetchone()[0]
        self.cursor.execute("delete from basic_conversation_plugin_nodes_aliases where bcpnm_id = %s", bcpnm_id)

    def log_visitor_message(self, visitor_cellnumber, robot_cellnumber, input_msg_list):
        input_msg_list_converted = ' '.join(input_msg_list)
        self.cursor.execute("insert into message_log(visitor_cellnumber, visitor_msg, robot_cellnumber) values(%s, %s, %s)", (visitor_cellnumber, input_msg_list_converted, robot_cellnumber))

    def log_robot_message(self, visitor_cellnumber, robot_cellnumber, robot_msg_list):
        input_msg_list_converted = ''.join(robot_msg_list)
        self.cursor.execute("insert into message_log(visitor_cellnumber, robot_cellnumber, robot_msg) values(%s, %s, %s)", (visitor_cellnumber, robot_cellnumber, input_msg_list_converted))

    def get_plugin_codename(self, node):
        self.cursor.execute("select codename from plugin p inner join node_plugin_control n on p.id = n.plugin_id where node_name = %s", node)
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def get_if_node_is_plugin(self, node):
        self.cursor.execute("select node_is_plugin from node_plugin_control where node_name = %s", node)
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]
