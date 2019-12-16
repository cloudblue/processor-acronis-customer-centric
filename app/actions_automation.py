"""
This file is property of the Ingram Micro Cloud Blue.
Copyright (c) 2019 Ingram Micro. All Rights Reserved.
"""

from app.utils.utils import Utils
from connect.logger import logger


class Actions:

    @staticmethod
    def reset(req):
        partner_config = Utils.get_partner_data(
            {'connection': req.configuration.connection.id, 'tier_1': req.configuration.account.external_id,
             'tier_2': 'default', 'req_id': req.configuration.id})
        logger.error("PARTNER CONFIG###############################################################################")
        logger.error(partner_config)
        api = Utils.get_api(partner_config)
        api.send_reset_email(
            {
                "login": req.get_param_by_id('admin_login_name').value,
                "email": req.configuration.account.contact_info.contact.email,
                "user_id": req.get_param_by_id('admin_id').value
            }
        )

    @staticmethod
    def sso(req):
        logger.error("SSO####################################################")
        partner_config = Utils.get_partner_data(
            {'connection': req.configuration.connection.id, 'tier_1': req.configuration.account.external_id,
             'tier_2': 'default', 'req_id': req.id})
        api = Utils.get_api(partner_config)
        reseller_id = req.get_param_by_id('tenant_id').value
        admin_id = req.get_param_by_id('admin_id').value
        logger.error("GROUP")
        group = api.get_group_id(reseller_id)
        console_branded = api.get_acc_console_branded(str(group['id']))
        logger.error("CONSOLE BRANDED")
        logger.error(console_branded)
        logger.error("JWT")
        jwt_data = api.sso(admin_id)
        link = console_branded['account_server_url']+'?jwt='+jwt_data['jwt']
        logger.error(link)
        return link
