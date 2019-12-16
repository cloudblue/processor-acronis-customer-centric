# -*- coding: utf-8 -*-

"""
This file is part of the Ingram Micro Cloud Blue Connect SDK.
Copyright (c) 2019 Ingram Micro. All Rights Reserved.
"""
from app.product_fulfillment import ProductFulfillment
from app.tier_fulfillment import TierFulfillment
from app.utils.utils import Utils
from connect.config import Config
from connect import TierConfigAutomation
from app.utils.utils import Utils
from connect.logger import logger
from app.actions_automation import Actions
from cherrypy.process.plugins import Daemonizer
from logging import FileHandler
import cherrypy
import jwt as jwt_parser



class FulfilmentExecution(object):

    def __init__(self, config):
        self.config_file = config
    
    @cherrypy.expose
    def aec_processor(self):
        try:
            webhook_secret = self.config_file['webhookSecret']
            encoded_jwt = cherrypy.request.headers['AUTHENTICATION'].replace("Bearer ", "")
            decoded_jwt = jwt_parser.decode(encoded_jwt, webhook_secret, algorithms=['HS256'])
            logger.error(decoded_jwt)
            if "webhook_id" in decoded_jwt:
                tier_request = TierFulfillment(Config(
                    api_url=self.config_file['quickStart']['url'],
                    api_key=self.config_file['quickStart']['key'],
                    products=self.config_file['quickStart']['products']
                ))

                tier_request.process()

                request = ProductFulfillment(Config(
                    api_url=self.config_file['quickStart']['url'],
                    api_key=self.config_file['quickStart']['key'],
                    products=self.config_file['quickStart']['products']
                ))

                request.process()
        except Exception as err:
            logger.error(err)


    @cherrypy.expose
    def aec_actions(self, jwt):
        webhook_secret = self.config_file['actionsSecret']
        decoded_jwt = jwt_parser.decode(jwt, webhook_secret, algorithms=['HS256'])
        automation = TierConfigAutomation()
        filters = automation.filters(
            status='approved',
            configuration__id=decoded_jwt['configuration_id'],
            configuration__product__id=self.config_file['quickStart']['products']
        )
        tier_requests = automation.list(filters)
        request = tier_requests[0]
        if decoded_jwt['action_id'] == 'SSO':
            link = Actions.sso(request)
            logger.error("LINK: " + link)
            raise cherrypy.HTTPRedirect(link)
        elif decoded_jwt['action_id'] == 'RESET':
            Actions.reset(request)


def error_page_404(status, message, traceback, version):
    return "404 Error!: Message:" + message


def error_page_500(status, message, traceback, version):
    logger.error(status)
    logger.error(message)
    return "500 Error!"

def start_server():
    try:
        config_file = Utils.get_config_file()
        Config(
            api_url=config_file['quickStart']['url'],
            api_key=config_file['quickStart']['key'],
            products=config_file['quickStart']['products']
        )

        logger.setLevel(config_file['quickStart']['log_level'])
        logger.addHandler(FileHandler(config_file['logFilename']))

        daemonizer = Daemonizer(cherrypy.engine)
        daemonizer.subscribe()
        # Configure and launch
        cherrypy.config.update({'server.socket_port': config_file['executionPort']})
        cherrypy.quickstart(FulfilmentExecution(config_file))
    except Exception as err:
        raise err


if __name__ == '__main__':
    start_server()