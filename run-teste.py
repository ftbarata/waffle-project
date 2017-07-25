#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
import sys
from layer import *
from yowsup.layers.auth import YowCryptLayer
from yowsup.layers.axolotl import AxolotlReceivelayer
from yowsup.layers.axolotl import AxolotlSendLayer
from yowsup.layers.axolotl import AxolotlControlLayer
from yowsup.layers.auth import YowAuthenticationProtocolLayer
from yowsup.layers.protocol_calls import YowCallsProtocolLayer
from yowsup.layers.protocol_media import YowMediaProtocolLayer
from yowsup.layers.protocol_messages import YowMessagesProtocolLayer
from yowsup.layers.protocol_receipts import YowReceiptProtocolLayer
from yowsup.layers.protocol_acks import YowAckProtocolLayer
from yowsup.layers.protocol_iq.layer import YowIqProtocolLayer
from yowsup.layers.protocol_presence import YowPresenceProtocolLayer
from yowsup.layers.network import YowNetworkLayer
from yowsup.layers.coder import YowCoderLayer
from yowsup.common import YowConstants
from yowsup.layers.logger import YowLoggerLayer

from yowsup.layers import YowLayerEvent, YowParallelLayer
from yowsup.layers.stanzaregulator import YowStanzaRegulator
from yowsup.stacks import YowStack, YOWSUP_CORE_LAYERS
from yowsup.env import YowsupEnv
from configobj import ConfigObj

if len(sys.argv) == 2:
    cfg = sys.argv[1]
    config = ConfigObj(cfg)
    phone = config['phone']
    password = config['password']
    CREDENTIALS = (phone, password)
    # layers = (
    #              EchoLayer,
    #              (YowAuthenticationProtocolLayer, YowMessagesProtocolLayer, YowReceiptProtocolLayer,
    #               YowAckProtocolLayer, YowPresenceProtocolLayer)
    #          ) + YOWSUP_CORE_LAYERS

    layers = (
        EchoLayer,
        YowParallelLayer(
            [YowAuthenticationProtocolLayer, YowMessagesProtocolLayer, YowReceiptProtocolLayer, YowAckProtocolLayer,
             YowMediaProtocolLayer, YowPresenceProtocolLayer, YowIqProtocolLayer, YowCallsProtocolLayer]),
        AxolotlReceivelayer,
        AxolotlControlLayer,
        AxolotlSendLayer,
        YowLoggerLayer,
        YowCoderLayer,
        YowCryptLayer,
        YowStanzaRegulator,
        YowNetworkLayer
    ) + YOWSUP_CORE_LAYERS

    stack = YowStack(layers)
    # Setting credentials
    stack.setProp(YowAuthenticationProtocolLayer.PROP_CREDENTIALS, CREDENTIALS)

    # WhatsApp server address
    stack.setProp(YowNetworkLayer.PROP_ENDPOINT, YowConstants.ENDPOINTS[0])
    stack.setProp(YowCoderLayer.PROP_DOMAIN, YowConstants.DOMAIN)
    stack.setProp(YowCoderLayer.PROP_RESOURCE, YowsupEnv.getCurrent().getResource())

    # Sending connecting signal
    stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))
    print('Iniciado.')
    try:
        # Program main loop
        stack.loop()
    except KeyboardInterrupt as e:
        print('Saindo...')
else:
    print('Syntax: {} <config_file>'.format(sys.argv[0]))




