# -*- coding: utf-8 -*-
import re
from configobj import ConfigObj
from zap.common.exit_plugin import ExitPlugin
from zap.common.filter_input import FilterInput
from zap.api.auth_middleware import *
from zap.common.unicode_to_ascii import UnicodeToAscii
from zap.api.delivery_api import MongoConn


class Delivery:

    def __init__(self, visitor_cellnumber, cfg):
        self.cfg = cfg
        config = ConfigObj(self.cfg)
        host_db = config['host_db']
        self.user_db = config['user_db']
        self.passdb = config['passdb']
        self.db_name = config['db_name']
        self.phone = config['phone']
        self.db = pymysql.connect(host_db, self.user_db, self.passdb, self.db_name, autocommit=True, charset='utf8')
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
        # filtered_input_list_ascii_string_version = ' '.join(filtered_input_list_ascii_string_version)

        unknown_input_answer = "Desculpe, não entendi sua mensagem. Verifique sua digitação ou digite *Sair* ."

        exit_keyword = 'Sair'
        for word in filtered_input_list_ascii:
            if str(word[0]).lower() == str(exit_keyword).lower():
                self.update_state('on_root')
                exit = ExitPlugin(self.visitor_cellnumber, self.cfg)
                exit.exit()
                return exit.yowsupmessage

        state = self.get_state()
        if state is None:
            self.update_state('on_root')
            state = 'on_root'

        if state == 'on_root':
            operations_dict = self.get_operations_dict()
            operation_list = "\nSelecione uma opção ou digite *Sair* :\n\n"
            if operations_dict is not None:
                for key in sorted(operations_dict.keys()):
                    operation_list = operation_list + str(key[0]) + ": " + operations_dict[key].encode(encoding='utf-8') + "\n"
            else:
                operation_list = "\n Não há opções no momento. Digite *Sair* ."

            self.update_state('on_operation_select')
            return operation_list

        elif state == 'on_operation_select':
            operations_dict = self.get_operations_dict()
            for word in filtered_input_list_ascii:
                for key in operations_dict.keys():
                    if str(word[0]).lower() == str(key[0]):
                        operation_codename = self.get_operation_codename(key)
                        if operation_codename == 'text_menu_massas':
                            mongodb_name = self.get_mongo_dbname()
                            mongo = MongoConn(mongodb_name, 'cardapio_massas')
                            dic = {}
                            # dic = mongo.get_cardapio_dict()
                            resp = ''
                            for i in dic.keys():
                                resp += str(i) + ": " + dic[i] + "\n\n"
                            return resp + "\nSelecione outra opção do menu ou digite *Sair*."
                        elif operation_codename == 'text_menu_bebidas':
                            mongodb_name = self.get_mongo_dbname()
                            mongo = MongoConn(mongodb_name, 'cardapio_bebidas')
                            dic = {}
                            # dic = mongo.get_cardapio_dict()
                            resp = ''
                            for i in dic.keys():
                                resp += str(i) + ": " + dic[i] + "\n\n"
                            return resp + "\nSelecione outra opção do menu ou digite *Sair*."
                        elif operation_codename == 'media_menu':
                            return "Aqui seria mostrado o cardápio em formato de imagem. Selecione outra opção do menu ou digite *Sair*."
                        elif operation_codename == 'show_profile':
                            if self.user_is_already_registered():
                                customer_profile = {}
                                customer_profile['1'] = self.get_customer_name()
                                customer_profile['2'] = self.get_customer_email()
                                customer_profile['3'] = self.get_customer_cep()
                                customer_profile['4'] = self.get_customer_bairro()
                                customer_profile['5'] = self.get_customer_cidade()
                                customer_profile['6'] = self.get_customer_estado()
                                customer_profile['7'] = self.get_customer_complemento()
                                customer_profile['8'] = self.get_customer_referencia()
                                customer_profile['9'] = self.get_customer_telfixo()
                                profile_string = "\n"
                                for i in range(1, 10):
                                    profile_string = profile_string + str(i) + ": " + customer_profile[str(i)].encode(encoding='utf-8') + "\n"
                                self.update_state('on_register_confirmation')
                                return "Seus dados são:" + profile_string + "Se estiverem todos corretos, responda *Sim* . Caso queira corrigir algum dado, digite a opção que deseja corrigir ou *Sair* :"
                            else:
                                return "Você ainda não está cadastrado(a). Seus dados serão solicitados antes de iniciar o pedido de entrega. Selecione outra opção ou digite *Sair* ."
                        elif operation_codename == 'delivery_order':
                            if not self.user_is_already_registered():
                                self.update_state('on_register_name')
                                return "Antes de iniciarmos, informo que não encontrei os dados de entrega vinculados ao seu número de celular. Portanto, vou precisar das seguintes informações *apenas desta vez* a título de cadastro:\nNome\nEmail\nCep\nBairro\nCidade\nEstado(sigla)\nComplemento\nReferência(dicas ou orientações, se houver, para o entregador)\nE telefone fixo(se houver).\n\nDigite seu *Nome* ou *Sair* :"
                            else:
                                profile_string = self.show_profile()
                                self.update_state('on_address_decision')
                                return "Seus dados de entrega cadastrados são:" + profile_string + "Caso a entrega seja neste endereço, responda *Sim* , caso contrário responda *Não* ou *Sair* ."
            return "Opção inválida. Verifique sua digitação ou digite *Sair* ."

        elif state == 'on_register_name':
            self.cursor.execute("insert into plugin_delivery_pizza_customer_data(cellnumber,name) values(%s,%s)", (self.visitor_cellnumber, unicode_message))
            self.update_state('on_register_email')
            return "Ok, por favor, me informe seu *E-mail* ou digite *Sair* :"
        elif state == 'on_register_email':
            emailRegex = re.compile(r'''([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+(\.[a-zA-Z]{2,4}))''', re.VERBOSE)
            email = emailRegex.findall(ascii_message)
            if len(email) == 0:
                return "O e-mail que você digitou não é válido. (Letras maiúsculas também são permitidas. O erro não é esse). Tente novamente ou digite *Sair*"
            else:
                # email = str(email).split(',')[0]
                self.cursor.execute("update plugin_delivery_pizza_customer_data set email = %s where cellnumber = %s", (str(ascii_message).lower(), self.visitor_cellnumber))
                self.update_state('on_register_cep')
                return "Ok, por favor, me informe seu *CEP* ou digite *Sair* :"
        elif state == 'on_register_cep':
            self.cursor.execute("update plugin_delivery_pizza_customer_data set cep = %s where cellnumber = %s", (unicode_message, self.visitor_cellnumber))
            self.update_state('on_register_bairro')
            return "Ok, por favor, me informe seu *Bairro* ou digite *Sair* :"
        elif state == 'on_register_bairro':
            self.cursor.execute("update plugin_delivery_pizza_customer_data set bairro = %s where cellnumber = %s", (unicode_message, self.visitor_cellnumber))
            self.update_state('on_register_cidade')
            return "Ok, por favor, me informe sua *Cidade* ou digite *Sair* :"
        elif state == 'on_register_cidade':
            self.cursor.execute("update plugin_delivery_pizza_customer_data set cidade = %s where cellnumber = %s", (unicode_message, self.visitor_cellnumber))
            self.update_state('on_register_estado')
            return "Ok, por favor, me informe seu *Estado(SIGLA)* ou digite *Sair* :"
        elif state == 'on_register_estado':
            states = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR',
                      'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
            if len(ascii_message) != 2:
                return "Digite apenas a *sigla* (2 dígitos) do Estado ou *Sair* :"
            else:
                for i in states:
                    if i == str(unicode_message).upper():
                        self.cursor.execute("update plugin_delivery_pizza_customer_data set estado = %s where cellnumber = %s", (str(ascii_message).upper(), self.visitor_cellnumber))
                        self.update_state('on_register_complemento')
                        return "Ok, por favor, me informe o *Complemento* ou digite *Sair* :"
                return "A sigla que você digitou não corresponde a nenhum estado brasileiro. Tente novamente ou digite *Sair* :"
        elif state == 'on_register_complemento':
            self.cursor.execute("update plugin_delivery_pizza_customer_data set complemento = %s where cellnumber = %s", (unicode_message, self.visitor_cellnumber))
            self.update_state('on_register_referencia')
            return "Ok, por favor, me informe a *Referência* (se não houver, apenas diga que não tem) ou digite *Sair* :"
        elif state == 'on_register_referencia':
            self.cursor.execute("update plugin_delivery_pizza_customer_data set referencia = %s where cellnumber = %s", (unicode_message, self.visitor_cellnumber))
            self.update_state('on_register_telfixo')
            return "Ok, por favor, me informe o(s) *telefone(s) fixo(s)* (se não houver, apenas diga que não tem) ou digite *Sair* :"
        elif state == 'on_register_telfixo':
            self.cursor.execute("update plugin_delivery_pizza_customer_data set telfixo = %s where cellnumber = %s", (unicode_message, self.visitor_cellnumber))
            profile_string = self.show_profile()
            self.update_state('on_register_confirmation')
            return "Ok, muito obrigado pelas informações. Por favor, verifique se os dados estão corretos:\n" + profile_string + "\nCaso estejam, digite *Sim*. Caso contrário, digite a opção que deseja corrigir ou *Sair* :"

        elif state == 'on_register_confirmation':
            for word in input_msg_list_ascii:
                if str(word).upper() == 'SIM':
                    self.update_state('on_delivery_reception')
                    return "Ok, vamos começar. Gostaria apenas de informar que, a qualquer momento, você pode digitar *Sair* para cancelar o processo.(Digite Ok para continuar)"
                else:
                    if word == '1':
                        self.update_state('on_retype_name')
                        return "Ok, então por favor, informe o nome corrigido:"
                    elif word == '2':
                        self.update_state('on_retype_email')
                        return "Ok, então por favor, informe o email corrigido:"
                    elif word == '3':
                        self.update_state('on_retype_cep')
                        return "Ok, então por favor, informe o CEP corrigido:"
                    elif word == '4':
                        self.update_state('on_retype_bairro')
                        return "Ok, então por favor, informe o bairro corrigido:"
                    elif word == '5':
                        self.update_state('on_retype_cidade')
                        return "Ok, então por favor, informe a cidade corrigida:"
                    elif word == '6':
                        self.update_state('on_retype_estado')
                        return "Ok, então por favor, informe a sigla do estado corrigido:"
                    elif word == '7':
                        self.update_state('on_retype_complemento')
                        return "Ok, então por favor, informe o complemento corrigido:"
                    elif word == '8':
                        self.update_state('on_retype_referencia')
                        return "Ok, então por favor, informe a referência corrigida:"
                    elif word == '9':
                        self.update_state('on_retype_telfixo')
                        return "Ok, então por favor, informe o(s) telefone(s) fixo(s) corrigido(s):"
                    else:
                        return "Opção inválida. Verifique sua digitação ou digite *Sair* ."

        elif state == 'on_retype_name':
            self.cursor.execute("update plugin_delivery_pizza_customer_data set name = %s where cellnumber = %s", (unicode_message, self.visitor_cellnumber))
            self.update_state('on_register_confirmation')
            profile_string = self.show_profile()
            return "Seu nome foi corrigido." + profile_string + "Se os dados estiverem corretos, digite *Sim* , caso contrário digite a opção que deseja corrigir ou *Sair* :"

        elif state == 'on_retype_email':
            emailRegex = re.compile(r'''([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+(\.[a-zA-Z]{2,4}))''', re.VERBOSE)
            email = emailRegex.findall(ascii_message)
            if len(email) == 0:
                return "O e-mail que você digitou não é válido. (Letras maiúsculas também são permitidas. O erro não é esse). Tente novamente ou digite *Sair*"
            else:
                self.cursor.execute("update plugin_delivery_pizza_customer_data set email = %s where cellnumber = %s", (str(ascii_message).lower(), self.visitor_cellnumber))
                self.update_state('on_register_confirmation')
                profile_string = self.show_profile()
                return "Seu email foi corrigido." + profile_string + "Se os dados estiverem corretos, digite *Sim* , caso contrário digite a opção que deseja corrigir ou *Sair* :"
        elif state == 'on_retype_cep':
            self.cursor.execute("update plugin_delivery_pizza_customer_data set cep = %s where cellnumber = %s", (unicode_message, self.visitor_cellnumber))
            self.update_state('on_register_confirmation')
            profile_string = self.show_profile()
            return "Seu CEP foi corrigido." + profile_string + "Se os dados estiverem corretos, digite *Sim* , caso contrário digite a opção que deseja corrigir ou *Sair* :"
        elif state == 'on_retype_bairro':
            self.cursor.execute("update plugin_delivery_pizza_customer_data set bairro = %s where cellnumber = %s", (unicode_message, self.visitor_cellnumber))
            self.update_state('on_register_confirmation')
            profile_string = self.show_profile()
            return "Seu bairro foi corrigido." + profile_string + "Se os dados estiverem corretos, digite *Sim* , caso contrário digite a opção que deseja corrigir ou *Sair* :"
        elif state == 'on_retype_cidade':
            self.cursor.execute("update plugin_delivery_pizza_customer_data set cidade = %s where cellnumber = %s", (unicode_message, self.visitor_cellnumber))
            self.update_state('on_register_confirmation')
            profile_string = self.show_profile()
            return "Sua cidade foi corrigida." + profile_string + "Se os dados estiverem corretos, digite *Sim* , caso contrário digite a opção que deseja corrigir ou *Sair* :"
        elif state == 'on_retype_estado':
            states = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR',
                      'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
            if len(ascii_message) != 2:
                return "Digite apenas a *sigla* (2 dígitos) do Estado ou *Sair* :"
            else:
                for i in states:
                    if i == str(unicode_message).upper():
                        self.cursor.execute("update plugin_delivery_pizza_customer_data set estado = %s where cellnumber = %s", (str(ascii_message).upper(), self.visitor_cellnumber))
                        self.update_state('on_register_confirmation')
                        profile_string = self.show_profile()
                        return "Seu estado foi corrigido." + profile_string + "Se os dados estiverem corretos, digite *Sim* , caso contrário digite a opção que deseja corrigir ou *Sair* :"
                return "A sigla que você digitou não corresponde a nenhum estado brasileiro. Tente novamente ou digite *Sair* :"
        elif state == 'on_retype_complemento':
            self.cursor.execute("update plugin_delivery_pizza_customer_data set complemento = %s where cellnumber = %s", (unicode_message, self.visitor_cellnumber))
            self.update_state('on_register_confirmation')
            profile_string = self.show_profile()
            return "Seu complemento foi corrigido." + profile_string + "Se os dados estiverem corretos, digite *Sim* , caso contrário digite a opção que deseja corrigir ou *Sair* :"
        elif state == 'on_retype_referencia':
            self.cursor.execute("update plugin_delivery_pizza_customer_data set referencia = %s where cellnumber = %s", (unicode_message, self.visitor_cellnumber))
            self.update_state('on_register_confirmation')
            profile_string = self.show_profile()
            return "Sua referencia foi corrigida." + profile_string + "Se os dados estiverem corretos, digite *Sim* , caso contrário digite a opção que deseja corrigir ou *Sair* :"
        elif state == 'on_retype_telfixo':
            self.cursor.execute("update plugin_delivery_pizza_customer_data set telfixo = %s where cellnumber = %s", (unicode_message, self.visitor_cellnumber))
            self.update_state('on_register_confirmation')
            profile_string = self.show_profile()
            return "Seu(s) telefone(s) fixo(s) foi(ram) corrigido(s)." + profile_string + "Se os dados estiverem corretos, digite *Sim* , caso contrário digite a opção que deseja corrigir ou *Sair* :"
        elif state == 'on_address_decision':
            if str(ascii_message).upper() == 'SIM':
                self.update_state('on_delivery_reception')
                mongodb_name = self.get_mongo_dbname()
                var_state_mongo = MongoConn(mongodb_name, '_variable_states')
                cfg_mongo = MongoConn(mongodb_name, '_config')
                next_state = cfg_mongo.get_next_state('root')
                var_state_mongo.update_variable_state(self.visitor_cellnumber, next_state)
                return cfg_mongo.get_return_message('root')
            elif str(ascii_message).upper() == 'NAO':
                self.update_state('on_enter_alternative_address')
                return "Ok, então por favor digite o endereço completo e demais informações necessárias à entrega, por exemplo nome do recebedor, telefones adicionais, orientações ao entregador, pontos de referência e etc ou digite *Sair* :"
            else:
                return unknown_input_answer
        elif state == 'on_enter_alternative_address':
            self.set_alternative_address(unicode_message)
            self.update_state('on_delivery_reception')
            return "Ok, o endereço alternativo para esta entrega foi salvo.(Digite Ok para continuar)"

        elif state == 'on_delivery_reception':
            mongodb_name = self.get_mongo_dbname()
            var_state_mongo = MongoConn(mongodb_name, '_variable_states')
            current_state = var_state_mongo.get_variable_state(self.visitor_cellnumber)
            cfg_mongo = MongoConn(mongodb_name, '_config')

            ascii = UnicodeToAscii(unicode_message)
            ascii_message = ascii.unicode_to_ascii()
            input_msg_list_ascii = ascii_message.split()

            restart_keyword = cfg_mongo.get_restart_keyword()

            for msg in input_msg_list_ascii:
                if str(msg).lower() == str(restart_keyword).lower():
                    var_state_mongo.update_variable_state(self.visitor_cellnumber, "root")
                    return cfg_mongo.get_return_message("root")
            if current_state == 'root':
                codpedido_mongo = MongoConn(mongodb_name, '_codpedido')
                codpedido_atual = codpedido_mongo.get_codpedido(self.visitor_cellnumber)
                codpedido_novo = codpedido_mongo.gen_new_codpedido(self.visitor_cellnumber, codpedido_atual)
                save_flag = cfg_mongo.get_save_flag(current_state)
                if save_flag == "1":
                    val = cfg_mongo.save_input(current_state, unicode_message, codpedido_novo)
                    if val is not True:
                        return val
                else:
                    next_state_override_collection = cfg_mongo.get_next_state_override_collection(current_state)
                    if next_state_override_collection is None:
                        return "Problema na configuração de estados."
                    else:
                        next_state_override = cfg_mongo.get_next_state_override(input_msg_list_ascii, next_state_override_collection)
                        if next_state_override != "null":
                            next_state = next_state_override
                            var_state_mongo.update_variable_state(self.visitor_cellnumber, next_state)
                        else:
                            return "Opção inválida."
            else:
                codpedido_mongo = MongoConn(mongodb_name, '_codpedido')
                codpedido = codpedido_mongo.get_codpedido(self.visitor_cellnumber)
                save_flag = cfg_mongo.get_save_flag(current_state)
                if save_flag == "1":
                    val = cfg_mongo.save_input(current_state, unicode_message, codpedido)
                    if val is not True:
                        previous_state = cfg_mongo.get_previous_state(state)
                        var_state_mongo.update_variable_state(self.visitor_cellnumber, previous_state)
                        return val
                else:
                    next_state_override_collection = cfg_mongo.get_next_state_override_collection(current_state)
                    if next_state_override_collection is None:
                        return "Problema na configuração de estados."
                    else:
                        next_state_override = cfg_mongo.get_next_state_override(input_msg_list_ascii, next_state_override_collection)
                        if next_state_override != "null":
                            next_state = next_state_override
                            var_state_mongo.update_variable_state(self.visitor_cellnumber, next_state)
                        else:
                            return "Opção inválida."
            if save_flag == "1":
                next_state = cfg_mongo.get_next_state(current_state)
                var_state_mongo.update_variable_state(self.visitor_cellnumber, next_state)

            return cfg_mongo.get_return_message(current_state, save_flag)

    def set_alternative_address(self, unicode_message):
        self.cursor.execute("select cellnumber from plugin_delivery_pizza_alternative_address where cellnumber = %s", self.visitor_cellnumber)
        queryset = self.cursor.fetchone()
        if queryset is None:
            self.cursor.execute("insert into plugin_delivery_pizza_alternative_address(cellnumber,full_data) values(%s,%s)", (self.visitor_cellnumber, unicode_message))
        else:
            self.cursor.execute("update plugin_delivery_pizza_alternative_address set full_data = %s where cellnumber = %s", (unicode_message, self.visitor_cellnumber))

    def get_customer_name(self):
        self.cursor.execute("select name from plugin_delivery_pizza_customer_data where cellnumber = %s", self.visitor_cellnumber)
        queryset = self.cursor.fetchone()[0]
        if queryset is None:
            return 'Sem dados.'
        else:
            return queryset

    def get_customer_email(self):
        self.cursor.execute("select email from plugin_delivery_pizza_customer_data where cellnumber = %s", self.visitor_cellnumber)
        queryset = self.cursor.fetchone()[0]
        if queryset is None:
            return 'Sem dados.'
        else:
            return queryset

    def get_customer_cep(self):
        self.cursor.execute("select cep from plugin_delivery_pizza_customer_data where cellnumber = %s", self.visitor_cellnumber)
        queryset = self.cursor.fetchone()[0]
        if queryset is None:
            return 'Sem dados.'
        else:
            return queryset

    def get_customer_bairro(self):
        self.cursor.execute("select bairro from plugin_delivery_pizza_customer_data where cellnumber = %s", self.visitor_cellnumber)
        queryset = self.cursor.fetchone()[0]
        if queryset is None:
            return 'Sem dados.'
        else:
            return queryset

    def get_customer_cidade(self):
        self.cursor.execute("select cidade from plugin_delivery_pizza_customer_data where cellnumber = %s", self.visitor_cellnumber)
        queryset = self.cursor.fetchone()[0]
        if queryset is None:
            return 'Sem dados.'
        else:
            return queryset

    def get_customer_estado(self):
        self.cursor.execute("select estado from plugin_delivery_pizza_customer_data where cellnumber = %s", self.visitor_cellnumber)
        queryset = self.cursor.fetchone()[0]
        if queryset is None:
            return 'Sem dados.'
        else:
            return queryset

    def get_customer_complemento(self):
        self.cursor.execute("select complemento from plugin_delivery_pizza_customer_data where cellnumber = %s", self.visitor_cellnumber)
        return self.cursor.fetchone()[0]

    def get_customer_referencia(self):
        self.cursor.execute("select referencia from plugin_delivery_pizza_customer_data where cellnumber = %s", self.visitor_cellnumber)
        queryset = self.cursor.fetchone()[0]
        if queryset is None:
            return 'Sem dados.'
        else:
            return queryset

    def get_customer_telfixo(self):
        self.cursor.execute("select telfixo from plugin_delivery_pizza_customer_data where cellnumber = %s", self.visitor_cellnumber)
        queryset = self.cursor.fetchone()[0]
        if queryset is None:
            return 'Sem dados.'
        else:
            return queryset

    def update_state(self, state):
        self.cursor.execute("select id from plugin_delivery_pizza_state where cellnumber = %s", self.visitor_cellnumber)
        test = self.cursor.fetchone()
        if test is None:
            self.cursor.execute("insert into plugin_delivery_pizza_state(cellnumber,state) values(%s,%s)", (self.visitor_cellnumber, state))
        else:
            self.cursor.execute("update plugin_delivery_pizza_state set state = %s where cellnumber = %s", (state, self.visitor_cellnumber))

    def get_state(self):
        self.cursor.execute("select state from plugin_delivery_pizza_state where cellnumber = %s", self.visitor_cellnumber)
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def get_operations_dict(self):
        self.cursor.execute("select menu_option from plugin_delivery_pizza_operations_menu")
        queryset = self.cursor.fetchall()
        if len(queryset) == 0:
            return None
        else:
            tempdict = {}
            for i in queryset:
                self.cursor.execute("select description from plugin_delivery_pizza_operations_menu where menu_option = %s", i)
                tempdict[i] = self.cursor.fetchone()[0]
        return tempdict

    def get_operation_codename(self, menu_option):
        self.cursor.execute("select codename from plugin_delivery_pizza_operations_menu where menu_option = %s", menu_option)
        queryset = self.cursor.fetchone()
        if queryset is None:
            return None
        else:
            return queryset[0]

    def user_is_already_registered(self):
        self.cursor.execute("select cellnumber from plugin_delivery_pizza_customer_data where cellnumber = %s", self.visitor_cellnumber)
        test = self.cursor.fetchone()
        if test is None:
            return False
        else:
            return True

    def close(self):
        self.cursor.close()
        self.db.close()

    def show_profile(self):
        profile_string = "\n"
        profile_string = profile_string + "1 - Nome: " + self.get_customer_name().encode(encoding='utf-8') + "\n"
        profile_string = profile_string + "2 - E-mail: " + self.get_customer_email().encode(encoding='utf-8') + "\n"
        profile_string = profile_string + "3 - CEP: " + self.get_customer_cep().encode(encoding='utf-8') + "\n"
        profile_string = profile_string + "4 - Bairro: " + self.get_customer_bairro().encode(encoding='utf-8') + "\n"
        profile_string = profile_string + "5 - Cidade: " + self.get_customer_cidade().encode(encoding='utf-8') + "\n"
        profile_string = profile_string + "6 - Estado: " + self.get_customer_estado().encode(encoding='utf-8') + "\n"
        profile_string = profile_string + "7 - Complemento: " + self.get_customer_complemento().encode(encoding='utf-8') + "\n"
        profile_string = profile_string + "8 - Referência: " + self.get_customer_complemento().encode(encoding='utf-8') + "\n"
        profile_string = profile_string + "9 - Tel(s) Fixo(s): " + self.get_customer_telfixo().encode(encoding='utf-8') + "\n"
        return profile_string

    def get_mongo_dbname(self):
        db = pymysql.connect(api_host_db, api_user_db, api_passdb, api_db_name, autocommit=True)
        cursor = db.cursor()
        cursor.execute("select mongodb_name from api_token where phone = %s", self.phone)
        mongodb_name = cursor.fetchone()[0]
        cursor.close()
        db.close()
        return mongodb_name

    def clear_incomplete_orders(self):
        self.cursor.execute("select codpedido from plugin_delivery_pizza_mongo_codpedido_map where cellnumber = %s", self.visitor_cellnumber)
        codpedido = self.cursor.fetchone()
        if codpedido is not None:
            mongodb_name = self.get_mongo_dbname()
            mongo = MongoConn(mongodb_name, 'pedidos')
            self.cursor.execute("delete from plugin_delivery_pizza_mongo_codpedido_map where cellnumber = %s", self.visitor_cellnumber)
            return mongo.delete_one_by_oid(codpedido)

    def get_codpedido(self):
        self.cursor.execute("select codpedido from plugin_delivery_pizza_mongo_codpedido_map where cellnumber = %s", self.visitor_cellnumber)
        return self.cursor.fetchone()[0]
