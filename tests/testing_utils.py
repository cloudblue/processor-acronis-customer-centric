"""
This file is property of the Ingram Micro Cloud Blue.
Copyright (c) 2019 Ingram Micro. All Rights Reserved.
"""

import os
import json
from connect.config import Config
from app.utils.utils import Utils


class TestUtils(Utils):

    @staticmethod
    def get_request(file, model_class):
        with open(os.path.join(os.path.dirname(__file__), file)) as request_file:
            request = model_class.deserialize(request_file.read())
        return request

    @staticmethod
    def get_response(response):
        return __class__.extract_data_file("responses/" + response + ".json")

    @staticmethod
    def extract_data_file(file):
        with open(os.path.join(os.path.dirname(__file__), file)) as config_file:
            data_file = json.load(config_file)
        return data_file

    @staticmethod
    def get_Fulfillment(fulfillment):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        os.chdir("../")
        config_file = Utils.get_config_file()
        fulfillment = fulfillment(Config(
            api_url=config_file['quickStart']['url'],
            api_key=config_file['quickStart']['key'],
            products=config_file['quickStart']['products']
        ))
        return fulfillment
