"""
This file is property of the Ingram Micro Cloud Blue.
Copyright (c) 2019 Ingram Micro. All Rights Reserved.
"""

import os
import json
from connect.models.fulfillment import Fulfillment
from typing import Any, Dict
from connect.models.exception import FulfillmentFail
from connect.models.exception import Skip
from app.api.wrapper import Wrapper


class Utils:

    @staticmethod
    def get_partner_data(req) -> Dict[str, Any]:
        if isinstance(req, Fulfillment):
            connection = req.asset.connection.id
            req_id = req.id
        else:
            connection = req['connection']
            req_id = req['req_id']

        config = __class__.get_config_file()

        # Simplified for take partner data just for connection, in connect v17 should be changed and add marketplace
        if connection in config['partnerConfig']:
            return config['partnerConfig'][connection]['default']
        else:
            raise Skip('Request: ' + req_id + ' not processed by this processor')

    @staticmethod
    def get_config_file() -> Dict[str, Any]:
        with open(os.path.dirname(os.path.abspath(__file__)) + '/../../config.json') as file_handle:
            config = json.load(file_handle)
        return config

    @staticmethod
    def get_api(partner_config) -> Wrapper:
        api = Wrapper()
        api.configure(partner_config)
        return api

    @staticmethod
    def get_product(items):
        product = None
        active_items = 0
        for item in items:
            if item.quantity > 0:
                product = item
                active_items += 1

        if active_items > 1:
            raise Exception('Too many products in the request')
        else:
            return product

    @staticmethod
    def sku_to_offering_item(item):
        try:
            item.mpn = item.mpn.split('__')[1]
            return item
        except Exception:
            raise FulfillmentFail("Wrong mpn format")

    @staticmethod
    def add_value_to_offer(av, item, version):
        av['quota'] = {'value': item.quantity, 'overage': item.quantity, 'version': version}
        return av
