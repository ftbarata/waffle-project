#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
from datetime import *
import sys
from yowsup.stacks import  YowStackBuilder
from yowsup.layers.auth import AuthError
from yowsup.layers import YowLayerEvent
from yowsup.layers.network import YowNetworkLayer
from yowsup.layers.protocol_media.protocolentities  import *
from yowsup.env import YowsupEnv
from configobj import ConfigObj
from zap.plugins.basic_conversation.basic_conversation import BasicConversationFlow
from yowsup.layers.protocol_messages.protocolentities  import TextMessageProtocolEntity
from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from zap.common.unicode_to_ascii import UnicodeToAscii
import logging
logging.basicConfig(level=logging.INFO)


class EchoLayer(YowInterfaceLayer):
    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):

        if messageProtocolEntity.getType() == 'text':
            self.onTextMessage(messageProtocolEntity)
        elif messageProtocolEntity.getType() == 'media':
            self.onMediaMessage(messageProtocolEntity)

        # self.toLower(messageProtocolEntity.forward(messageProtocolEntity.getFrom()))
        self.toLower(messageProtocolEntity.ack())
        self.toLower(messageProtocolEntity.ack(True))

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        self.toLower(entity.ack())

    def onTextMessage(self,messageProtocolEntity):
        currdate = date.today()
        a = datetime.now()
        currtime = a.strftime('%H:%M:%S')
        visitor_cellnumber = messageProtocolEntity.getFrom(False)
        unicode_message = messageProtocolEntity.getBody()
        print('{} {} De: {}'.format(currdate, currtime, visitor_cellnumber))
        ascii = UnicodeToAscii(unicode_message)
        ascii_message = ascii.unicode_to_ascii()
        print('Mensagem: {}'.format(ascii_message))
        c = BasicConversationFlow(visitor_cellnumber, cfg)
        c.navigation(unicode_message)
        resposta = c.get_yowsupmessage()
        print('Reposta: {}'.format(resposta))
        outgoingMessageProtocolEntity = TextMessageProtocolEntity(resposta, to=messageProtocolEntity.getFrom())
        self.toLower(outgoingMessageProtocolEntity)

    def onMediaMessage(self, messageProtocolEntity):
        # just print info
        if messageProtocolEntity.getMediaType() == "image":
            print("Echoing image %s to %s" % (messageProtocolEntity.url, messageProtocolEntity.getFrom(False)))

        elif messageProtocolEntity.getMediaType() == "location":
            print("Echoing location (%s, %s) to %s" % (messageProtocolEntity.getLatitude(), messageProtocolEntity.getLongitude(), messageProtocolEntity.getFrom(False)))
            outLocation = LocationMediaMessageProtocolEntity(messageProtocolEntity.getLatitude(), messageProtocolEntity.getLongitude(), encoding = "raw", url="http://www.conntracktecnologia.com.br", name="Waffle - Geolocalização", to=messageProtocolEntity.getFrom())
            self.toLower(outLocation)

        elif messageProtocolEntity.getMediaType() == "vcard":
            print("Echoing vcard (%s, %s) to %s" % (messageProtocolEntity.getName(), messageProtocolEntity.getCardData(), messageProtocolEntity.getFrom(False)))

    def send_message(self):
        self.toLower(TextMessageProtocolEntity('bla2', to='5521997741018' + '@s.whatsapp.net'))


if len(sys.argv) == 2:
    cfg = sys.argv[1]
    config = ConfigObj(cfg)
    phone = config['phone']
    password = config['password']
    credentials = (phone, password)

    if __name__==  "__main__":
        stackBuilder = YowStackBuilder()

        stack = stackBuilder.pushDefaultLayers(True).push(EchoLayer).build()

        stack.setCredentials(credentials)
        stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))   #sending the connect signal
        print('Iniciado.')
        try:
            EchoLayer().send_message()
            stack.loop() #this is the program mainloop
        except KeyboardInterrupt as e:
            print('Saindo...')

else:
    print('Syntax: {} <config_file>'.format(sys.argv[0]))
