# -*- coding: utf-8 -*-
import pymysql
from configobj import ConfigObj

from zap.common.exit_plugin import ExitPlugin
from zap.common.filter_input import FilterInput


class QuestionsRegister:

    def __init__(self, visitor_cellnumber, cfg):
        self.cfg = cfg
        config = ConfigObj(self.cfg)
        host_db = config['host_db']
        self.user_db = config['user_db']
        self.passdb = config['passdb']
        self.db_name = config['db_name']
        self.db = pymysql.connect(host_db, self.user_db, self.passdb, self.db_name, autocommit=True)
        self.cursor = self.db.cursor()
        self.visitor_cellnumber = visitor_cellnumber

    def command_interface(self, input_msg_list):
        start_keyword = self.get_start_keyword()
        if start_keyword is None:
            start_keyword = 'Responder'

        quiz_choice_question = self.get_group_choice_question()
        if quiz_choice_question is None:
            quiz_choice_question = 'Selecione o questionário:'

        category_choice_question = self.get_group_choice_question()
        if category_choice_question is None:
            category_choice_question = 'Selecione a categoria do questionário:'

        subcategory_choice_question = self.get_group_choice_question()
        if subcategory_choice_question is None:
            subcategory_choice_question = 'Selecione a subcategoria do questionário:'

        exit_keyword = self.get_exit_keyword()
        if exit_keyword is None:
            exit_keyword = "Sair"

        unknown_input = self.get_unknown_input()
        if unknown_input is None:
            unknown_input = "Desculpe, não entendi sua mensagem."

        empty_question_groups = self.get_empty_question_groups()
        if empty_question_groups is None:
            empty_question_groups = 'Não há questões cadastradas.'

        for word in input_msg_list:
            if str(word).lower() == str(exit_keyword).lower():
                self.exit()

        state = self.get_visitor_state()
        if state is None:
            self.update_state('visitor_on_root')
            state = 'visitor_on_root'

        if state == 'visitor_on_root':
            for word in input_msg_list:
                if str(word).lower() == str(start_keyword).lower():
                    temp_dict = {}
                    categories_list = self.get_category_list()
                    for i in range(1, len(categories_list) +1):
                        temp_dict[i] = categories_list[i - 1]
                    menu = '\n'
                    for j in temp_dict.keys():
                        menu = menu + str(j) + ':' + ' ' + str(temp_dict[j]) + '\n'
                    self.update_state('visitor_on_category_choice')
                    return category_choice_question + '\n' + menu
                else:
                        return unknown_input

        elif state == 'visitor_on_category_choice':
            temp_dict = {}
            categories_list = self.get_category_list()
            for i in range(1, len(categories_list) + 1):
                temp_dict[i] = categories_list[i - 1]
            for word in input_msg_list:
                for key in temp_dict.keys():
                    if str(word).lower() == key:
                        category_name = temp_dict[key]
                        subcategories = self.get_subcategories_list_by_category(category_name)
                        if len(subcategories) > 0:
                            temp_dict2 = {}
                            for j in range(1, len(subcategories) + 1):
                                temp_dict2[j] = subcategories[j - 1]
                            subcategory_menu = '\n'
                            for k in temp_dict2.keys():
                                subcategory_menu = subcategory_menu + str(k) + ':' + ' ' + str(temp_dict2[k]) + '\n'
                            self.update_state('visitor_on_subcategory_choice')
                            return subcategory_choice_question + '\n' + subcategory_menu
                        else:
                            quiz_titles = self.get_titles_by_category(category_name)
                            if len(quiz_titles) > 0:
                                temp_dict = {}
                                for i in range(1, len(quiz_titles) + 1):
                                    temp_dict[i] = quiz_titles[i - 1]
                                quiz_menu = '\n'
                                for i in temp_dict.keys():
                                    quiz_menu = quiz_menu + str(i) + ':' + ' ' + str(temp_dict[i]) + '\n'
                                self.update_state('visitor_on_quiz_choice')
                                return quiz_choice_question + '\n' + quiz_menu

        elif state == 'visitor_on_subcategory_choice':
            pass
        elif state == 'visitor_on_quiz_choice':
            pass
        elif state == 'visitor_on_play:':
            pass
        elif state == 'visitor_finished':
            pass

    def get_admin_state(self):
        self.cursor.execute("select codename from plugin_quiz_states p inner join plugin_quiz_admin_state q where p.id = q.quiz_state_id where administrator_cellnumber = %s", self.visitor_cellnumber)
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def get_visitor_state(self):
        self.cursor.execute("select codename from plugin_quiz_states p inner join plugin_quiz_visitor_state q where p.id = q.quiz_state_id where visitor_cellnumber = %s", self.visitor_cellnumber)
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def get_presentation_message(self):
        self.cursor.execute("select presentation_message from plugin_quiz_runtime_messages")
        queryset = self.cursor.fetchone()
        if queryset is None:
            return 'O subsistema de Quiz foi ativado. O que deseja fazer? *cadastrar* questões ou *responder* ?'
        else:
            return queryset[0]

    @staticmethod
    def input_parser(input_msg_list, value):
        filter = FilterInput(input_msg_list)
        filtered_msg_list = filter.filter()
        for word in filtered_msg_list:
            if str(word).lower() == str(value).lower():
                return True

    def close(self):
        self.cursor.close()
        self.db.close()

    def update_state(self, state):
        self.cursor.execute("select id from plugin_quiz_visitor_state where visitor_cellnumber = %s", self.visitor_cellnumber)
        test = self.cursor.fetchone()[0]
        if test is None:
            self.cursor.execute("insert into plugin_quiz_visitor_state(visitor_cellnumber, state) values(%s, %s)", (self.visitor_cellnumber, state))
        else:
            self.cursor.execute("update plugin_quiz_visitor_state set state = %s where visitor_cellnumber = %s", (state, self.visitor_cellnumber))

    def get_start_keyword(self):
        self.cursor.execute("select menu_start_quiz_keyword from plugin_quiz_runtime_messages")
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def get_group_choice_question(self):
        self.cursor.execute("select group_choice_question from plugin_quiz_runtime_messages")
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def get_category_choice_question(self):
        self.cursor.execute("select category_choice_question from plugin_quiz_runtime_messages")
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def get_subcategory_choice_question(self):
        self.cursor.execute("select subcategory_choice_question from plugin_quiz_runtime_messages")
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def get_question_group_title_by_category(self, category):
        self.cursor.execute("select title from plugin_quiz_questions_group where category = %s", category)
        return self.cursor.fetchall()

    def get_exit_keyword(self):
        self.cursor.execute("select exit_keyword from plugin_quiz_runtime_messages")
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def get_unknown_input(self):
        self.cursor.execute("select unknown_input from plugin_quiz_runtime_messages")
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def get_empty_question_groups(self):
        self.cursor.execute("select empty_question_groups from plugin_quiz_runtime_messages")
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def get_category_list(self):
        self.cursor.execute("select distinct category from plugin_quiz_questions_group")
        return self.cursor.fetchall()

    def get_subcategories_list_by_category(self, category):
        self.cursor.execute("select subcategory from plugin_quiz_questions_group where category = %s", category)
        return self.cursor.fetchall()

    def get_titles_by_category(self, category):
        self.cursor.execute("select title from plugin_quiz_questions_group where category = %s", category)
        return self.cursor.fetchall()

    def answer_quiz(self, question_group):
        pass

    def exit(self):
        e = ExitPlugin(self.visitor_cellnumber, self.cfg)
        e.exit()

    def save_temp_dict(self, dict):
        self.cursor.execute("update plugin_quiz_visitor_state set temp_dict = %s where visitor_cellnumber = %s", (str(dict), self.visitor_cellnumber))

    def get_temp_dict(self):
        self.cursor.execute("select temp_dict from plugin_quiz_visitor_state where visitor_cellnumber = %s", self.visitor_cellnumber)
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]
