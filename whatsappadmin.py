#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-

import sys, subprocess

import os, shutil
from zap.lib.graphs_manager import GraphManager
from zap.plugins.basic_conversation.db_connector import BasicConversationDb
from zap.settings import *
from configobj import ConfigObj


def show_graph(cfg):
    config = ConfigObj(cfg)
    username = config['db_name'].split('_')[1]
    g = GraphManager(username)
    graph = g.load_graph()
    g.show_graph(graph)


def create_user(cfg):
    config = ConfigObj(cfg)
    username = config['db_name'].split('_')[1]
    firstname = raw_input('First Name:')
    lastname = raw_input('Last Name:')
    email = raw_input('email:')
    robotcellnumber = config['phone']
    password = raw_input('password:')

    g = GraphManager(username)
    g.create_root(robotcellnumber)
    g.save_graph()

    subprocess.call(['mysql', '-uroot', '-p****', '-e', 'create database zap_{} DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;'.format(username)])
    subprocess.call(['mysql -uroot -p**** zap_{} < /home/zap/zap/database.sql'.format(username)], shell=True)

    db = BasicConversationDb(cfg)
    db.set_new_user(username, firstname, lastname, email, password)
    db.close()

    session_config(cfg)
    print('SUCCESS: User {} created.'.format(username))


def add_nodes(cfg):
    config = ConfigObj(cfg)
    username = config['db_name'].split('_')[1]
    g = GraphManager(username)
    g.load_graph()
    while True:
        parent = raw_input('Parent node: (empty to exit)')
        if parent == '':
            break
        node_name = raw_input('New node name:')
        g.add_node(parent, node_name)
    g.save_graph()
    print('Exited.')


def set_nodes_messages(cfg):
    db = BasicConversationDb(cfg)
    while True:
        node = raw_input('Node name: (empty to exit)')
        if node == '':
            break
        message = raw_input('Message:')
        db.set_node_message(node, message)
    db.close()
    print('Exited.')


def del_node(cfg):
    node_name = raw_input('Node name:')
    config = ConfigObj(cfg)
    username = config['db_name'].split('_')[1]
    g = GraphManager(username)
    g.load_graph()
    g.remove_node(node_name)
    g.save_graph()
    db = BasicConversationDb(cfg)
    db.del_node_message(node_name)
    db.close()


def add_nodes_aliases(cfg):
    db = BasicConversationDb(cfg)
    while True:
        node = raw_input('Node name: (empty to exit)')
        if node == '':
            break
        message = raw_input('Alias:')
        db.add_node_alias(node, message)
    db.close()
    print('Exited.')


def set_main_messages(cfg):
    print('* presentation_message')
    print('* last_leaf_message')
    print('* alias_found_message')
    print('* multiple_keywords_matched_message')
    print('* multiple_aliases_found_message')
    print('* default_unknown_input_message')
    print('* back_to_root_keyword')
    print('* goodbye_message')
    db = BasicConversationDb(cfg)
    while True:
        field = raw_input('Field name:(empty to exit)')
        if field == '':
            break
        message = raw_input('Message or word:')
        db.set_main_messages(field, message)
    db.close()
    print('Exited.')


def show_main_messages(cfg):
    field = raw_input('Type field name or ENTER to show all:')
    if not field:
        field = 'NULL'
    db = BasicConversationDb(cfg)
    result = db.show_main_messages(field)
    db.close()
    print(result)


def del_all_main_messages(cfg):
    db = BasicConversationDb(cfg)
    db.del_all_main_messages()
    db.close()
    print('SUCCESS: All main messages were deleted.')


def session_config(cfg):
    session_timeout_seconds = raw_input('Session timeout(in seconds):')
    record_chat = raw_input('Record chat?: (1 / 0)')
    record_chat_days = raw_input('How many days to record chat?:')
    days_visitor_is_known = raw_input('How many days robot will remember each visitor?:')

    db = BasicConversationDb(cfg)
    db.set_session_config(session_timeout_seconds, record_chat, record_chat_days, days_visitor_is_known)
    db.close()


def show_sessions(cfg):
    visitor_cellnumber = raw_input('Type visitor_cellnumber or ENTER to show all:')
    if not visitor_cellnumber:
        visitor_cellnumber = 'NULL'
    db = BasicConversationDb(cfg)
    result = db.get_sessions(visitor_cellnumber)
    db.close()
    print(result)


def show_node_messages(cfg):
    node = raw_input('Type node name or ENTER to show all:')
    if not node:
        node = 'NULL'
    db = BasicConversationDb(cfg)
    result = db.get_node_messages(node)
    db.close()
    print(result)


def clear_sessions(cfg):
    visitor_cellnumber = raw_input('Type visitor_cellnumber or ENTER to clear all:')
    if not visitor_cellnumber:
        visitor_cellnumber = 'NULL'
    db = BasicConversationDb(cfg)
    db.clear_sessions(visitor_cellnumber)
    db.close()
    print('SUCCESS: Sessions cleared.')


def del_node_alias(cfg):
    node_name = raw_input('Type node name:')
    db = BasicConversationDb(cfg)
    db.del_node_alias(node_name)
    db.close()
    print('SUCCESS: Alias(es) cleared.')


def remove_user(cfg):
    config = ConfigObj(cfg)
    username = config['db_name'].split('_')[1]
    robot_cellnumber = config['phone']
    prompt = raw_input('Are you SURE you want to remove user: {} with associated robot number {} ? (YES/NO):'.format(username, robot_cellnumber))
    if str(prompt) == 'YES':
        if os.path.isdir(os.path.join(ROOT_DIR, username)):
            shutil.rmtree(os.path.join(ROOT_DIR, username))
            db = BasicConversationDb(cfg)
            db.drop_database_user()
            db.close()
            print('SUCCESS: User {} with associated robot number {} was removed.'.format(username, robot_cellnumber))
        else:
            print('ERROR: Path {} not found.'.format(os.path.join(ROOT_DIR, username)))
    else:
        print('Operation canceled.')


# def conversation(cfg, visitor_cellnumber, input_msg):
#     c = BasicConversationFlow(visitor_cellnumber, cfg)
#     input_msg_list = []
#     for i in input_msg:
#         input_msg_list.append(i)
#     c.navigation(input_msg_list)


def syntax():
    print('Syntax: {} create_user conf_file'.format(sys.argv[0]))
    print('Syntax: {} REMOVE_USER conf_file'.format(sys.argv[0]))
    print('Syntax: {} show_graph conf_file'.format(sys.argv[0]))
    print('Syntax: {} add_nodes conf_file'.format(sys.argv[0]))
    print('Syntax: {} set_nodes_messages conf_file'.format(sys.argv[0]))
    print('Syntax: {} set_main_messages conf_file'.format(sys.argv[0]))
    print('Syntax: {} del_all_main_messages conf_file'.format(sys.argv[0]))
    print('Syntax: {} add_nodes_aliases conf_file'.format(sys.argv[0]))
    print('Syntax: {} session_config conf_file'.format(sys.argv[0]))
    print('Syntax: {} del_node_alias conf_file'.format(sys.argv[0]))
    print('Syntax: {} del_node conf_file'.format(sys.argv[0]))
    print('Syntax: {} show_sessions conf_file'.format(sys.argv[0]))
    print('Syntax: {} show_node_messages conf_file'.format(sys.argv[0]))
    print('Syntax: {} show_main_messages conf_file'.format(sys.argv[0]))
    print('Syntax: {} clear_sessions conf_file'.format(sys.argv[0]))
    # print('Syntax: {} conversation conf_file visitor_cellnumber message'.format(sys.argv[0]))

if len(sys.argv) == 3:
    if os.path.isfile(sys.argv[2]):
        opt = sys.argv[1]
        cfg = sys.argv[2]
        if opt == 'create_user':
            create_user(cfg)
        elif opt == 'REMOVE_USER':
            remove_user(cfg)
        elif opt == 'show_graph':
            show_graph(cfg)
        elif opt == 'add_nodes':
            add_nodes(cfg)
        elif opt == 'set_nodes_messages':
            set_nodes_messages(cfg)
        elif opt == 'set_main_messages':
            set_main_messages(cfg)
        elif opt == 'del_all_main_messages':
            del_all_main_messages(cfg)
        elif opt == 'add_nodes_aliases':
            add_nodes_aliases(cfg)
        elif opt == 'session_config':
            session_config(cfg)
        elif opt == 'del_node_alias':
            del_node_alias(cfg)
        elif opt == 'del_node':
            del_node(cfg)
        elif opt == 'show_sessions':
            show_sessions(cfg)
        elif opt == 'show_node_messages':
            show_node_messages(cfg)
        elif opt == 'show_main_messages':
            show_main_messages(cfg)
        elif opt == 'clear_sessions':
            clear_sessions(cfg)
    else:
        print('{} not found.'.format(sys.argv[2]))
else:
    syntax()