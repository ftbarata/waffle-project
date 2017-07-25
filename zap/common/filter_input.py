# -*- coding: utf-8 -*-
# This class removes any character that is not alphanumeric character
import re


class FilterInput:

    def __init__(self, input_msg_list_ascii):
        self.input_msg_list_ascii = input_msg_list_ascii

    def filter(self):
        templist = []
        for i in self.input_msg_list_ascii:
            input = re.findall(r'\w+', i)
            if input:
                templist.append(input)
        return templist
