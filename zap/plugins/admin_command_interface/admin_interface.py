# -*- coding: utf-8 -*-
import pymysql
from configobj import ConfigObj
from ..admin_auth.auth import Auth
from zap.common.exit_plugin import ExitPlugin
from zap.common.filter_input import FilterInput
from zap.common.unicode_to_ascii import UnicodeToAscii
from phishing_message.phishing import PhishingMessage


class AdminCommandInterface:

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

        exit_keyword = 'Sair'
        for word in filtered_input_list_ascii:
            if str(word[0]).lower() == str(exit_keyword).lower():
                self.update_state('visitor_on_root')
                exit = ExitPlugin(self.visitor_cellnumber, self.cfg)
                exit.exit()
                return exit.yowsupmessage

        enter_keyword = 'acessar'

        state = self.get_state()
        if state is None:
            self.update_state('visitor_on_root')
            state = 'visitor_on_root'

        if state == 'visitor_on_root':
            for word in filtered_input_list_ascii:
                if str(word[0]).lower() == str(enter_keyword).lower():
                    authenticate = Auth(self.visitor_cellnumber, self.cfg)
                    if authenticate.get_authorization(1):
                        self.update_state('visitor_on_granted_root')
                        operations_dict = self.get_operations_dict()
                        operation_list = "\nSelecione uma opção ou digite *Sair* :\n\n"
                        if operations_dict is not None:
                            for key in sorted(operations_dict.keys()):
                                operation_list = operation_list + str(key[0]) + ": " + operations_dict[key] + "\n"
                        else:
                            operation_list = "\n Não há operações administrativas disponíveis no momento."

                        return authenticate.get_access_granted_message() + operation_list
                    else:
                        exit = ExitPlugin(self.visitor_cellnumber, self.cfg)
                        exit.exit()
                        return authenticate.get_access_denied_message() + "\n" + exit.yowsupmessage
        elif state == 'visitor_on_granted_root':
            operations_dict = self.get_operations_dict()
            for word in filtered_input_list_ascii:
                for key in operations_dict.keys():
                    if str(word[0]).lower() == str(key[0]):
                        operation_codename = self.get_operation_codename(key)
                        if operation_codename == 'add_administrator':
                            self.update_state('visitor_on_cellnumber_prompt')
                            return 'Informe o número de celular do(a) novo(a) administrador(a), no formato *55 + DDD + NÚMERO* . ex: *5521999999999* ou *Sair* :'
                        elif operation_codename == 'list_administrators':
                            authenticate = Auth(self.visitor_cellnumber, self.cfg)
                            admin_dict = authenticate.get_administrators_list()
                            name_list = "Lista dos administradores cadastrados: (Você continua na raiz do menu administrativo. Escolha uma opção ou digite *Sair* ):\n\n"
                            if admin_dict is not None:
                                for key in admin_dict.keys():
                                    name_list = name_list + str(key[0]) + ": " + admin_dict[key] + "\n"
                            else:
                                name_list = "\n Não há administradores cadastrados."
                            return name_list
                        elif operation_codename == 'remove_administrator':
                            self.update_state('visitor_on_remove_administrator_prompt')
                            authenticate = Auth(self.visitor_cellnumber, self.cfg)
                            admin_dict = authenticate.get_administrators_list()
                            name_list = "Digite o número *completo* do telefone do(a) administrador(a) abaixo que deseja remover ou digite *Sair* :\n\n"
                            if admin_dict is not None:
                                for key in admin_dict.keys():
                                    name_list = name_list + str(key[0]) + ": " + admin_dict[key] + "\n"
                            else:
                                name_list = "\n Não há administradores cadastrados."
                            return name_list
                        elif operation_codename == 'send_phishing_message':
                            msg = PhishingMessage(self.visitor_cellnumber, self.cfg)
                            if not msg.get_phishing_message_status():
                                content = msg.get_phishing_message_content()
                                author = msg.get_phishing_message_created_by()
                                created_at = msg.get_phishing_message_created_at()
                                recipients_count = msg.get_current_phishing_recipients_count()
                                msg.close()
                                return "Já existe a mensagem (isca): \n *" + content + "* \" em processamento criada por " + author + " em " + created_at + " para " + recipients_count + " atuais destinatários. É preciso aguardar o término deste processamento para enviar nova mensagem de isca. Entretanto, caso novos números desconhecidos forem sendo adicionados no banco de dados, a mensagem atual será enviada para estes também. Escolha outra opção do menu administrativo ou *Sair* ."
                            else:
                                msg.close()
                                self.update_state('visitor_on_phishing_message_prompt')
                                return "Atenção: A mensagem \"isca\" serve para fazer com que o destinatário desconhecido responda qualquer mensagem. Isso evitará possível bloqueio do número que estou usando registrado nos servidores do WhatsApp.\n Dica: Envie um \"oi\", \"olá\", \"bom dia\" por exemplo. Provavelmente a resposta será \" quem é?\" \n\nDigite sua mensagem de isca ou *Sair* ."
            return "Opção inválida."
        elif state == 'visitor_on_cellnumber_prompt':
            authenticate = Auth(self.visitor_cellnumber, self.cfg)
            if not authenticate.add_administrator_cellnumber(ascii_message):
                name = authenticate.get_administrator_name(ascii_message)
                self.update_state('visitor_on_granted_root')
                return "Já existe um(a) administrador(a) cadastrado(a) com este número, vinculado ao nome de " + name[0] + ". Escolha novamente uma das opções do menu administrativo ou *Sair* ."
            else:
                self.update_state('visitor_on_name_prompt')
                return 'Informe o nome do(a) novo(a) administrador(a):'
        elif state == 'visitor_on_name_prompt':
            authenticate = Auth(self.visitor_cellnumber, self.cfg)
            authenticate.update_administrator_name(ascii_message)
            self.update_state('visitor_on_finished_new_admin_subscribed')
            return 'Novo(a) administrador(a) cadastrado(a) com sucesso.'
        elif state == 'visitor_on_finished_new_admin_subscribed':
            self.update_state('visitor_on_granted_root')
            operations_dict = self.get_operations_dict()
            operation_list = "\n\n"
            if operations_dict is not None:
                for key in sorted(operations_dict.keys()):
                    operation_list = operation_list + str(key[0]) + ": " + operations_dict[key] + "\n"
            else:
                operation_list = "\n Não há operações administrativas disponíveis no momento."
            return "Você está de volta ao menu raiz das opções administrativas. Escolha uma das operações abaixo ou digite *Sair* ." + operation_list

        elif state == 'visitor_on_remove_administrator_prompt':
            authenticate = Auth(self.visitor_cellnumber, self.cfg)
            name_test = authenticate.get_administrator_name(ascii_message)
            if name_test is not None:
                name = name_test[0]
            else:
                name = " "
            result = authenticate.remove_administrator(ascii_message)
            if result:
                self.update_state('visitor_on_granted_root')
                return 'O(a) administrador(a) ' + name + ' foi removido. Você está de volta ao menu administrativo raiz. Escolha uma operação ou *Sair* .'
            else:
                return 'Não foi encontrado nenhum(a) administrador(a) associado(a) a este número. Tente novamente ou digite *Sair* .'
        elif state == 'visitor_on_phishing_message_prompt':
            msg = PhishingMessage(self.visitor_cellnumber, self.cfg)
            if msg.send_phishing_message_to_spool(unicode_message):
                msg.close()
                self.update_state('visitor_on_granted_root')
                return "A mensagem de isca foi cadastrada com sucesso e começará a ser enviada, com um intervalo de 3 minutos entre cada destinatário, dentro de alguns instantes para os destinatários ainda desconhecidos.\nSelecione uma das operações do menu administrativo ou *Sair* . "
            else:
                msg.close()
                self.update_state('visitor_on_granted_root')
                return "Ocorreu um erro ao cadastrar a mensagem de isca. Informe ao suporte.\nSelecione uma das operações do menu administrativo ou *Sair* . "

    def update_state(self, state):
        self.cursor.execute("select id from plugin_subscription_state where cellnumber = %s", self.visitor_cellnumber)
        test = self.cursor.fetchone()
        if test is None:
            self.cursor.execute("insert into plugin_subscription_state(cellnumber,state) values(%s,%s)", (self.visitor_cellnumber, state))
        else:
            self.cursor.execute("update plugin_subscription_state set state = %s where cellnumber = %s", (state, self.visitor_cellnumber))

    def get_state(self):
        self.cursor.execute("select state from plugin_subscription_state where cellnumber = %s", self.visitor_cellnumber)
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def get_operations_dict(self):
        self.cursor.execute("select menu_option from plugin_admin_command_interface_operation_list")
        queryset = self.cursor.fetchall()
        if len(queryset) == 0:
            return None
        else:
            tempdict = {}
            for i in queryset:
                self.cursor.execute("select operation from plugin_admin_command_interface_operation_list where menu_option = %s", i)
                operation = self.cursor.fetchone()[0]
                tempdict[i] = operation
        return tempdict

    def get_operation_codename(self, menu_option):
        self.cursor.execute("select codename from plugin_admin_command_interface_operation_list where menu_option = %s", menu_option)
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def close(self):
        self.cursor.close()
        self.db.close()

