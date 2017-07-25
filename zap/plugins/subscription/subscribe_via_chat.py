# -*- coding: utf-8 -*-
import pymysql, re
from configobj import ConfigObj

from zap.common.exit_plugin import ExitPlugin
from zap.common.filter_input import FilterInput
from zap.common.unicode_to_ascii import UnicodeToAscii


class SubscribeViaChat:

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

    def command_interface(self, unicode_message):
        ascii = UnicodeToAscii(unicode_message)
        ascii_message = ascii.unicode_to_ascii()
        input_msg_list_ascii = ascii_message.split()

        filter = FilterInput(input_msg_list_ascii)
        filtered_input_list_ascii = filter.filter()
        filtered_input_list_ascii_string_version = []
        for i in filtered_input_list_ascii:
            filtered_input_list_ascii_string_version.append(i[0])
        filtered_input_list_ascii_string_version = ' '.join(filtered_input_list_ascii_string_version)

        exit_keyword = 'Sair'
        for word in filtered_input_list_ascii:
            if str(word[0]).lower() == str(exit_keyword).lower():
                self.update_state('visitor_on_root')
                exit = ExitPlugin(self.visitor_cellnumber, self.cfg)
                exit.exit()
                return exit.yowsupmessage

        state = self.get_state()
        if state is None:
            self.update_state('visitor_on_root')
            state = 'visitor_on_root'

        ask_for_name_or_not_message = self.get_ask_for_name_or_not()
        if ask_for_name_or_not_message is None:
            ask_for_name_or_not_message = 'Vou registrá-lo(a) em meu banco de dados agora. Já detectei seu número de celular, gostaria de fornecer seu nome ? ( *Sim* ou *Não* )'

        ask_for_email_or_not_message = self.get_ask_for_name_or_not()
        if ask_for_email_or_not_message is None:
            ask_for_email_or_not_message = 'Gostaria de fornecer seu email ? ( *Sim* ou *Não* )'

        subscription_keyword = self.get_subscription_keyword()
        if subscription_keyword is None:
            subscription_keyword = 'Cadastro'

        unsubscription_keyword = 'Cancelamento'

        unknown_input = self.get_unknown_input()
        if unknown_input is None:
            if state == 'visitor_on_root':
                unknown_input = 'Desculpe, não entendi sua mensagem. Digite *Cancelamento* , *Cadastro* ou *Sair* .'
            else:
                unknown_input = 'Desculpe, não entendi sua mensagem. Responda *Sim* , *Não* ou *Sair* .'

        enter_your_name = self.get_enter_your_name()
        if enter_your_name is None:
            enter_your_name = 'Ok, então por favor me informe seu nome.'

        enter_your_email = self.get_enter_your_email()
        if enter_your_email is None:
            enter_your_email = 'Ok, então por favor me informe seu email.'

        name_saved = self.get_name_saved()
        if name_saved is None:
            name_saved = 'Seu nome foi salvo. Deseja fornecer seu email? ( *Sim* ou *Não* )'

        finished_subscription = self.get_finished_subscription()
        if finished_subscription is None:
            finished_subscription = 'Seu cadastro foi concluído. Obrigado!'

        if state == 'visitor_on_root':
            test = self.test_if_user_is_already_registered()
            for word in filtered_input_list_ascii:
                if str(word[0]).lower() == str(subscription_keyword).lower():
                    if not test:
                        self.update_state('visitor_on_ask_for_name_or_not')
                        return ask_for_name_or_not_message
                    else:
                        name = self.get_subscriber_name()
                        email = self.get_subscriber_email()
                        if name is not None and email is not None:
                            you_are_already_registered = 'Olá %s, você já está cadastrado, e seu e-mail é: %s. Deseja alterar seu cadastro? ( *Sim* ou *Não* )' % (name, email)
                        elif name is not None and email is None:
                            you_are_already_registered = 'Olá %s, você já está cadastrado, mas seu e-mail eu não tenho. Deseja alterar seu cadastro? ( *Sim* ou *Não* )' % (name)
                        elif name is None and email is not None:
                            you_are_already_registered = 'Você já está cadastrado. Não tenho seu nome, apenas seu email: %s Deseja alterar seu cadastro? ( *Sim* ou *Não* )' % (email)
                        else:
                            you_are_already_registered = 'Você já está cadastrado, mas não tenho seu nome nem seu e-mail. Deseja alterar seu cadastro? ( *Sim* ou *Não* )'
                        self.update_state('visitor_on_already_registered')
                        return you_are_already_registered
                elif str(word[0]).lower() == str(unsubscription_keyword).lower():
                    return_code = self.unsubscribe()
                    exit = ExitPlugin(self.visitor_cellnumber, self.cfg)
                    exit.exit()
                    if return_code is not None:
                        return 'Pronto, você foi removido da minha base de dados.' + ' ' + exit.yowsupmessage
                    else:
                        return 'Você já não constava na minha base de dados, fique tranquilo(a) seu cadastro não existe mais.' + ' ' + exit.yowsupmessage

            return unknown_input
        elif state == 'visitor_on_already_registered':
            for word in filtered_input_list_ascii:
                if str(word[0]).lower() == 'sim':
                    self.update_state('visitor_on_ask_for_name_or_not')
                    return ask_for_name_or_not_message
                elif str(word[0]).lower() == 'nao':
                    self.update_state('visitor_on_root')
                    exit = ExitPlugin(self.visitor_cellnumber, self.cfg)
                    exit.exit()
                    return exit.yowsupmessage
                else:
                    return unknown_input
        elif state == 'visitor_on_ask_for_name_or_not':
            for word in filtered_input_list_ascii:
                if str(word[0]).lower() == 'sim':
                    self.update_state('visitor_on_enter_name')
                    return enter_your_name
                elif str(word[0]).lower() == 'nao':
                    self.update_state('visitor_on_ask_for_email_or_not')
                    return ask_for_email_or_not_message
                else:
                    return unknown_input
        elif state == 'visitor_on_enter_name':
            self.subscribe_name(filtered_input_list_ascii_string_version)
            self.update_state('visitor_on_ask_for_email_or_not')
            return name_saved
        elif state == 'visitor_on_ask_for_email_or_not':
            for word in filtered_input_list_ascii:
                if str(word[0]).lower() == 'sim':
                    self.update_state('visitor_on_enter_email')
                    return enter_your_email
                elif str(word[0]).lower() == 'nao':
                    self.subscribe_only_cellphone()
                    self.update_state('visitor_on_finished_subscription')
                    return finished_subscription
                else:
                    return unknown_input
        elif state == 'visitor_on_enter_email':
            emailRegex = re.compile(r'''([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+(\.[a-zA-Z]{2,4}))''', re.VERBOSE)
            email = emailRegex.findall(ascii_message)
            if len(email) == 0:
                return "O e-mail que você digitou não é válido. (Letras maiúsculas também são permitidas. O erro não é esse). Tente novamente ou digite *%s* para voltar à raiz." % (exit_keyword)
            else:
                self.subscribe_email(ascii_message)
                self.update_state('visitor_on_finished_subscription')
                return finished_subscription
        elif state == 'visitor_on_finished_subscription':
            self.update_state('visitor_on_root')
            exit = ExitPlugin(self.visitor_cellnumber, self.cfg)
            exit.exit()
            return exit.yowsupmessage

    def test_if_user_is_already_registered(self):
        self.cursor.execute("select cellnumber from plugin_subscription where cellnumber = %s", self.visitor_cellnumber)
        test = self.cursor.fetchone()
        if test is None:
            return False
        else:
            return True

    def get_ask_for_name_or_not(self):
        self.cursor.execute("select ask_for_name_or_not from plugin_subscription_runtime_messages")
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def get_ask_for_email_or_not(self):
        self.cursor.execute("select ask_for_email_or_not from plugin_subscription_runtime_messages")
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def get_enter_your_name(self):
        self.cursor.execute("select enter_your_name from plugin_subscription_runtime_messages")
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def get_enter_your_email(self):
        self.cursor.execute("select enter_your_email from plugin_subscription_runtime_messages")
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def get_name_saved(self):
        self.cursor.execute("select name_saved from plugin_subscription_runtime_messages")
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def get_finished_subscription(self):
        self.cursor.execute("select finished_subscription from plugin_subscription_runtime_messages")
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def get_state(self):
        self.cursor.execute("select state from plugin_subscription_state where cellnumber = %s", self.visitor_cellnumber)
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def update_state(self, state):
        self.cursor.execute("select id from plugin_subscription_state where cellnumber = %s", self.visitor_cellnumber)
        test = self.cursor.fetchone()
        if test is None:
            self.cursor.execute("insert into plugin_subscription_state(cellnumber,state) values(%s,%s)", (self.visitor_cellnumber, state))
        else:
            self.cursor.execute("update plugin_subscription_state set state = %s where cellnumber = %s", (state, self.visitor_cellnumber))

    def get_subscription_keyword(self):
        self.cursor.execute("select subscription_keyword from plugin_subscription_runtime_messages")
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def get_unknown_input(self):
        self.cursor.execute("select unknown_input from plugin_subscription_runtime_messages")
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def subscribe_name(self, filtered_input_list_ascii_string_version):
        self.cursor.execute("select id from plugin_subscription where cellnumber = %s", self.visitor_cellnumber)
        test = self.cursor.fetchone()
        if test is None:
            self.cursor.execute("insert into plugin_subscription(cellnumber,name) values(%s,%s)", (self.visitor_cellnumber, filtered_input_list_ascii_string_version))
        else:
            self.cursor.execute("update plugin_subscription set name = %s where cellnumber = %s", (filtered_input_list_ascii_string_version, self.visitor_cellnumber))

    def subscribe_email(self, ascii_message):
        self.cursor.execute("select id from plugin_subscription where cellnumber = %s", self.visitor_cellnumber)
        test = self.cursor.fetchone()
        if test is None:
            self.cursor.execute("insert into plugin_subscription(cellnumber,email) values(%s,%s)", (self.visitor_cellnumber, ascii_message.lower()))
        else:
            self.cursor.execute("update plugin_subscription set email = %s where cellnumber = %s", (ascii_message.lower(), self.visitor_cellnumber))

    def subscribe_only_cellphone(self):
        self.cursor.execute("select id from plugin_subscription where cellnumber = %s", self.visitor_cellnumber)
        test = self.cursor.fetchone()
        if test is None:
            self.cursor.execute("insert into plugin_subscription(cellnumber) values(%s)", self.visitor_cellnumber)
        else:
            self.cursor.execute("update plugin_subscription set cellnumber = %s where cellnumber = %s", (self.visitor_cellnumber, self.visitor_cellnumber))

    def get_subscriber_name(self):
        self.cursor.execute("select name from plugin_subscription where cellnumber = %s", self.visitor_cellnumber)
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def get_subscriber_email(self):
        self.cursor.execute("select email from plugin_subscription where cellnumber = %s", self.visitor_cellnumber)
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def close(self):
        self.cursor.close()
        self.db.close()

    def unsubscribe(self):
        self.cursor.execute("select id from plugin_subscription where cellnumber = %s", self.visitor_cellnumber)
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            self.cursor.execute("delete from plugin_subscription where cellnumber = %s", self.visitor_cellnumber)
            self.cursor.execute("delete from plugin_subscription_state where cellnumber = %s", self.visitor_cellnumber)
            return True