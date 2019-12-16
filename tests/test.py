"""
This file is property of the Ingram Micro Cloud Blue.
Copyright (c) 2019 Ingram Micro. All Rights Reserved.
"""

import unittest
from unittest.mock import patch, MagicMock

from connect.models import ActivationTemplateResponse, ActivationTileResponse, TierConfigRequest, Fulfillment
from app.product_fulfillment import ProductFulfillment
from app.tier_fulfillment import TierFulfillment
from tests.testing_utils import TestUtils


class Test(unittest.TestCase):

    @patch('requests.post',
           MagicMock(
               side_effect=[TestUtils.get_response('token'), TestUtils.get_response('provision_reseller'),
                            TestUtils.get_response('provision_admin'),

                            TestUtils.get_response('reset')]))
    @patch('requests.get',
           MagicMock(side_effect=[
               TestUtils.get_response('logged_user'),
               TestUtils.get_response('empty'),
               TestUtils.get_response('applications'),
               TestUtils.get_response('get_offering_items')]))

    @patch('requests.put',
            MagicMock(
                side_effect=[TestUtils.get_response('access_policies'),
                             TestUtils.get_response('put_offerings'),
                             TestUtils.get_response('empty')
                             ]))
    def test_provision_reseller(self):
        request = TestUtils.get_request("requests/request.provision_reseller.http.json", TierConfigRequest)
        product_fulfillment = TestUtils.get_Fulfillment(TierFulfillment)
        self.assertIsInstance(product_fulfillment.process_request(request), ActivationTemplateResponse)

    def test_provision_reseller_skip_by_config(self):
        request = TestUtils.get_request("requests/request.provision_reseller_skip.http.json", TierConfigRequest)
        product_fulfillment = TestUtils.get_Fulfillment(TierFulfillment)
        self.assertIsInstance(product_fulfillment.process_request(request), ActivationTemplateResponse)

    @patch('requests.post',
           MagicMock(side_effect=[TestUtils.get_response('edit')]))
    def test_change(self):
        request = TestUtils.get_request("requests/request.change.http.json", Fulfillment)
        product_fulfillment = TestUtils.get_Fulfillment(ProductFulfillment)
        self.assertIsInstance(product_fulfillment.process_request(request), ActivationTemplateResponse)

    @patch('requests.post',
           MagicMock(
               side_effect=[TestUtils.get_response('token'), TestUtils.get_response('provision_reseller'),
                            TestUtils.get_response('provision_admin'),

                            TestUtils.get_response('reset')]))
    @patch('requests.get',
           MagicMock(side_effect=[
               TestUtils.get_response('logged_user'),
               TestUtils.get_response('empty'),
               TestUtils.get_response('applications'),
               TestUtils.get_response('get_offering_items')]))

    @patch('requests.put',
           MagicMock(
               side_effect=[TestUtils.get_response('access_policies'),
                            TestUtils.get_response('put_offerings'),
                            TestUtils.get_response('empty')
                            ]))
    def test_provision(self):
        request = TestUtils.get_request("requests/request.purchase.http.json", Fulfillment)
        product_fulfillment = TestUtils.get_Fulfillment(ProductFulfillment)
        self.assertIsInstance(product_fulfillment.process_request(request), ActivationTemplateResponse)

    @patch('requests.put', MagicMock(side_effect=[TestUtils.get_response('disable')]))
    @patch('requests.delete', MagicMock(side_effect=[TestUtils.get_response('empty')]))
    def test_cancel(self):
        request = TestUtils.get_request("requests/request.cancel.http.json", Fulfillment)
        product_fulfillment = TestUtils.get_Fulfillment(ProductFulfillment)
        self.assertIsInstance(product_fulfillment.process_request(request), ActivationTileResponse)

    @patch('requests.put', MagicMock(side_effect=[TestUtils.get_response('disable')]))
    def test_suspend(self):
        request = TestUtils.get_request("requests/request.suspend.http.json", Fulfillment)
        product_fulfillment = TestUtils.get_Fulfillment(ProductFulfillment)
        self.assertIsInstance(product_fulfillment.process_request(request), ActivationTileResponse)

    @patch('requests.put', MagicMock(side_effect=[TestUtils.get_response('resume')]))
    def test_resume(self):
        request = TestUtils.get_request("requests/request.resume.http.json", Fulfillment)
        product_fulfillment = TestUtils.get_Fulfillment(ProductFulfillment)
        self.assertIsInstance(product_fulfillment.process_request(request), ActivationTileResponse)
