"""
This file is property of the Ingram Micro Cloud Blue.
Copyright (c) 2019 Ingram Micro. All Rights Reserved.
"""
import time
from connect import TierConfigAutomation
from connect.logger import logger
from connect.models import ActivationTemplateResponse, Param
from app.service.service import Service
from app.utils.utils import Utils
from connect.exceptions import FailRequest, InquireRequest, SkipRequest


class TierFulfillment(TierConfigAutomation):

    def process_request(self, req):
        try:
            setattr(self, 'tenant', None)
            if req.type == 'update':
                raise FailRequest("Update operations are not allowed")
            logger.info("Begin tier config process:" + req.configuration.id)
            logger.debug(req)
            partner_config = Utils.get_partner_data(
                {'connection': req.configuration.connection.id, 'tier_1': req.configuration.account.external_id,
                 'tier_2': 'default', 'req_id': req.id})

            logger.info(
                "Validate if req requires Skip according accountExternalIdsConfigRequestSkipPrefix config parameter")
            if req.configuration.account.external_id.startswith(
                    tuple(partner_config['accountExternalIdsConfigRequestSkipPrefix'])):
                raise SkipRequest('Skipped by processor configuration')
            setattr(self, 'service', Service(partner_config, req.configuration.account))
            # Check if current logged user exists
            self.service.check_login(req.get_param_by_id('admin_login_name').value)

            subs_start = str(time.time())
            internal_tag = 'aps-abc-start-prod-date=%s;aps-abc-tier=%s;aps-abc-billing-model=%s' % (
                subs_start, '-1', 'per_gb')

            # Create tenant subscription
            logger.info("Creating tenant...")
            tenant_created = self.service.create_tenant(req.id, internal_tag)
            logger.debug(tenant_created)
            setattr(self, 'tenant', tenant_created['id'])
            # Create admin for subscription
            logger.info("Creating admin...")
            admin_created = self.service.create_admin(tenant_created,
                                                      req.get_param_by_id('admin_login_name').value, True)
            logger.debug(admin_created)
            # Add access policies for the user
            logger.info("Adding access policies...")
            self.service.access_policies(admin_created, tenant_created, True)
            # Set offerings available for reseller customers
            logger.info("Set offerings...")
            self.service.set_offerings(tenant_created)
            # Send activation email
            logger.info("Sending email...")
            self.service.send_email(req.get_param_by_id('admin_login_name').value, admin_created)

            params = [
                Param(id='tenant_id', value=str(tenant_created['id'])),
                Param(id='admin_id', value=str(admin_created['id'])),
                Param(id='reseller_customer_id', value=str(internal_tag)),
                Param(id='billing_date', value=str(subs_start))
            ]
            logger.info("End tier configuration for " + req.configuration.id)
            self.update_parameters(req.id, params)
            return ActivationTemplateResponse(partner_config['templates']['t1_template'])

        except FailRequest as err:
            self.__rollback()
            logger.error("Issue while processing Purchase request. Print Error: %s" % err)
            raise err
        except SkipRequest as err:
            logger.info(err)
            raise err
        except InquireRequest as err:
            self.__rollback()
            if self.tenant:
                self.service.remove(self.tenant)
            logger.error("Issue while processing Purchase request. Print Error: %s" % err)
            raise err
        except Exception as err:
            self.__rollback()
            if self.tenant:
                self.service.remove(self.tenant)
            logger.error("Issue while processing Purchase request. Print Error: %s" % err)
            raise err

    def __rollback(self):
        if self.tenant:
            suspended = self.service.edit(self.tenant, {'enabled': False, 'version': 1})
            self.service.remove(self.tenant, suspended['version'], {'version': suspended['version']})
