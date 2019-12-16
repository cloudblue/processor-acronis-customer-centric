"""
This file is property of the Ingram Micro Cloud Blue.
Copyright (c) 2019 Ingram Micro. All Rights Reserved.
"""
from connect import FulfillmentAutomation
from connect.logger import logger
from connect.models import ActivationTemplateResponse, ActivationTileResponse, Param
from connect.exceptions import FailRequest, InquireRequest, SkipRequest
from connect.models.fulfillment import Fulfillment
from app.utils.utils import Utils
from app.service.service import Service


class ProductFulfillment(FulfillmentAutomation):

    def process_request(self, req: Fulfillment) -> object:
        try:
            logger.info("Processing request " + req.id)
            partner_config = Utils.get_partner_data(req)
            setattr(self, 'service', Service(partner_config, req.asset.tiers.customer))

            switcher = {
                "purchase": lambda: __class__.__purchase(self, req),
                "cancel": lambda: __class__.__cancel(self, req),
                "change": lambda: __class__.__change(self, req),
                "suspend": lambda: __class__.__toggle(self, False, req),
                "resume": lambda: __class__.__toggle(self, True, req)
            }

            switcher.get(req.type, "ERROR: Action type is no valid")()

            if req.type in ['purchase', 'change', 'resume']:
                result = ActivationTemplateResponse(partner_config['templates']['activation_template'])
            else:
                result = ActivationTileResponse('Operation ' + req.type + ' done successfully')
            logger.info("Finishing request " + req.id)
            return result
        except SkipRequest as err:
            logger.info(err.message)
            raise SkipRequest(str(err))
        except FailRequest as err:
            logger.error("Issue while processing Purchase request. Print Error: %s" % str(err))
            raise err
        except InquireRequest as err:
            logger.error("Issue while processing Purchase request. Print Error: %s" % str(err))
            raise err
        except Exception as err:
            logger.error("Issue while processing Purchase request. Print Error: %s" % str(err))

            raise err

    def __purchase(self, req):
        logger.info("PURCHASE")
        setattr(self, 'tenant', None)
        login_name = req.asset.get_param_by_id('customer_admin').value
        # Check if logged user exists
        self.service.check_login(login_name)
        try:
            # Create customer account
            logger.info("Creating tenant...")
            tenant_created = self.service.provision_customer(req.id, self.get_tier_config(req.asset.tiers.tier1.id,
                                                                                          self.config.products[
                                                                                              0]).get_param_by_id(
                'tenant_id').value)
            logger.debug(tenant_created)
            setattr(self, 'tenant', tenant_created['id'])
            # Set offering based in sku
            logger.info("Setting offerings...")
            self.service.set_customer_offerings(tenant_created['id'], self.get_tier_config(req.asset.tiers.tier1.id,
                                                                                           self.config.products[
                                                                                               0]).get_param_by_id(
                'tenant_id').value, [Utils.sku_to_offering_item(item) for item in req.asset.items if item.quantity > 0])
            # Create admin for user account
            logger.info("Creating admin...")
            admin_created = self.service.create_admin(tenant_created, login_name)
            logger.debug(admin_created)
            # Create access policies for created user
            self.service.access_policies(admin_created, tenant_created)
            # Send activation email
            self.service.send_email(login_name, admin_created)
            params = [
                Param(id='customer_tenant_id', value=str(tenant_created['id'])),
            ]
            self.update_parameters(req.id, params)
            logger.info("PURCHASE END")

        except Exception as err:
            if self.tenant:
                logger.error("Rollback tenant creation")
                suspended = self.service.edit(self.tenant, {'enabled': False, 'version': 1})
                self.service.remove(self.tenant, suspended['version'], {'version': suspended['version']})
            raise FailRequest(err)

    def __cancel(self, req):
        logger.info("Cancelling...")
        tenant_id = req.asset.get_param_by_id("customer_tenant_id").value
        tenant_suspended = self.__toggle(False, req)
        self.service.remove(tenant_id, tenant_suspended['version'], {'version': tenant_suspended['version']})
        logger.info("Cancelled")

    def __toggle(self, enabled, req):
        logger.info("Toggle")
        tenant_id = req.asset.get_param_by_id("customer_tenant_id").value
        version = self.service.get_tenant_info(tenant_id)['version']
        result = self.service.edit(tenant_id, {'enabled': enabled, 'version': version})
        return result

    def __change(self, req):
        logger.info("Changing...")
        changed = [Utils.sku_to_offering_item(item) for item in req.asset.items if
                   item.quantity > 1 and item.quantity != 0]
        logger.debug(changed)
        self.service.set_customer_offerings(req.asset.get_param_by_id("customer_tenant_id").value,
                                            self.get_tier_config(req.asset.tiers.tier1.id,
                                                                 self.config.products[0]).get_param_by_id(
                                                'tenant_id').value, changed, True)
