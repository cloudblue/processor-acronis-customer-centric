"""
This file is property of the Ingram Micro Cloud Blue.
Copyright (c) 2019 Ingram Micro. All Rights Reserved.
"""
import json
from requests import api
from connect.logger import logger
from urllib.parse import urlencode, quote_plus


class Client:

    @staticmethod
    def send_request(verb, uri, config, body=None):
        logger.error("REQUEST------------------->")
        logger.error('Request: %s %s' % (verb, uri))
        logger.debug(body)

        options = {'url': uri, 'headers': {'Content-Type': config['Content-Type']}}

        if 'bearer' in config:
            options['headers']['Authorization'] = 'Bearer ' + config['bearer']
        elif 'basic' in config:
            options['headers']['Authorization'] = 'Basic ' + config['basic']

        if body:
            options['data'] = urlencode(body, quote_via=quote_plus) if config[
                                                                           'Content-Type'] == 'application/x-www-form-urlencoded' else json.dumps(
                body)

        response = api.request(verb, **options)

        if 200 <= response.status_code <= 300:
            logger.debug(str(response))
            if response.content:
                return response.json()
        else:
            logger.error('Response')
            logger.error(str(response))
            raise Exception(response.json()['error'])
