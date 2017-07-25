#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
import falcon
import delivery_api


api = application = falcon.API()

delivery = delivery_api.Resource()

api.add_route('/delivery/{operation}', delivery)
