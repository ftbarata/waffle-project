# -*- coding: utf-8 -*-
from configobj import ConfigObj

class SendMessageOrMedia:

    def __init__(self, destination_cellnumber, cfg):
        cfg = cfg
        config = ConfigObj(cfg)
        self.phone = config['phone']
        self.password = config['password']
        self.destination_cellnumber = destination_cellnumber
        self.client = Client(login=self.phone, password=self.password)

    def send_text(self, text):
        self.client.send_message(self.destination_cellnumber, 'teste')

    def send_image(self, image):
        self.client.send_media(self.destination_cellnumber, path='/Users/tax/Desktop/logo.jpg')
