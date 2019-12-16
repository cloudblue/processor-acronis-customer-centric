# -*- coding: utf-8 -*-

"""
This file is part of the Ingram Micro Cloud Blue Connect SDK.
Copyright (c) 2019 Ingram Micro. All Rights Reserved.
"""
from connect.config import Config
from connect.logger import logger
from app.tier_fulfillment import TierFulfillment
from app.product_fulfillment import ProductFulfillment
from app.utils.utils import Utils

# Set logger level (default level is ERROR)
logger.setLevel("INFO")

if __name__ == '__main__':
    config_file = Utils.get_config_file()
    tier_request = TierFulfillment(Config(
        api_url=config_file['quickStart']['url'],
        api_key=config_file['quickStart']['key'],
        products=config_file['quickStart']['products']
    ))

    tier_request.process()


    request = ProductFulfillment(Config(
        api_url=config_file['quickStart']['url'],
        api_key=config_file['quickStart']['key'],
        products=config_file['quickStart']['products']
    ))

    request.process()
