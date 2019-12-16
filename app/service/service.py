"""
This file is property of the Ingram Micro Cloud Blue.
Copyright (c) 2019 Ingram Micro. All Rights Reserved.
"""
from app.utils.utils import Utils
from app.api.wrapper import Wrapper
from connect.logger import logger


class Service(Wrapper):
    user = ''

    def __init__(self, partner_config, user):
        self.configure(partner_config)
        self.user = user

    # RESELLER
    def create_tenant(self, request_id, internal_tag):
        phone_number = self.user.contact_info.contact.phone_number
        country_code = phone_number.country_code if phone_number.country_code else ''
        area_code = phone_number.area_code if phone_number.area_code else ''
        p_number = phone_number.phone_number if phone_number.phone_number else ''

        reseller_data = {
            'name': self.user.name + " " + request_id,
            'parent_id': '',
            'kind': 'partner',
            'contact': {
                'email': self.user.contact_info.contact.email,
                'address': self.user.contact_info.address_line1,
                'phone': country_code + area_code + p_number
            },
            'customer_id': '',
            'reseller_id': '',
            'internal_tag': internal_tag,
            'language': 'en_US'
        }
        return self.provision(reseller_data)

    def set_offerings(self, tenant_created):
        apps = self.get_available_apps(tenant_created['parent_id'])
        logger.debug(apps)
        offerings = self.get_available_offerings(tenant_created['parent_id'])
        logger.debug(offerings)
        offerings['offering_items'] = {}
        for item in offerings['items']:
            if item['status'] == 1 and item['application_id'] in apps['items']:
                if 'locked' in item: del item['locked']
                if 'measurement_unit' in item: del item['measurement_unit']
                if 'quota' in item: del item['quota']
                if 'type' in item: del item['type']
                key = item['application_id'] + item['name'] + item['infra_id'] if 'infra_id' in item else item[
                                                                                                              'application_id'] + \
                                                                                                          item['name']
                offerings['offering_items'][key] = item
        del offerings['items']
        self.set_offerings_for_children(tenant_created['id'],
                                        {'offering_items': list(offerings['offering_items'].values())})

    # CUSTOMER
    def provision_customer(self, request_id, parent_id=''):
        # Provision customer
        phone_number = self.user.contact_info.contact.phone_number
        country_code = phone_number.country_code if phone_number.country_code else ''
        area_code = phone_number.area_code if phone_number.area_code else ''
        p_number = phone_number.phone_number if phone_number.phone_number else ''
        customer_data = {
            'name': self.user.name + ' ' + request_id,
            'parent_id': parent_id,
            'kind': 'customer',
            'contact': {
                'email': self.user.contact_info.contact.email,
                'address': self.user.contact_info.address_line1,
                'phone': country_code + area_code + p_number
            },
            'language': 'en_US'
        }
        return self.provision(customer_data)

    def set_customer_offerings(self, customer_created_id, parent_id, items, update=False):
        available = self.get_available_offerings(parent_id, True)
        version = self.get_tenant_info(customer_created_id)['version']
        # Get matching avaliable offerings with purchased offerings
        offerings = {str(av['application_id']) + str(av['name']): Utils.add_value_to_offer(av, item, version) for av in
                     available['items'] for item in
                     items if
                     av['name'] == item.mpn}
        # Remove duplicates
        offerings = list(offerings.values())
        logger.debug(offerings)

        if update:
            current_offerings = self.get_offerings_for_children(customer_created_id)
            for offer in offerings:
                current_offering = [item for item in current_offerings['items'] if
                                    item['name'] == offer['name'] and 'quota' in item]
                offer['quota']['version'] = current_offering[0]['quota']['version']

        items = {'offering_items': offerings}
        self.set_offerings_for_children(customer_created_id, items)

    # COMMMON

    def create_admin(self, customer_created, admin_login, reseller=False):
        # Provision customer user
        phone_number = self.user.contact_info.contact.phone_number
        country_code = phone_number.country_code if phone_number.country_code else ''
        area_code = phone_number.area_code if phone_number.area_code else ''
        p_number = phone_number.phone_number if phone_number.phone_number else ''
        user_data = {
            'tenant_id': customer_created['id'],
            'login': admin_login,
            'contact':
                {
                    'email': self.user.contact_info.contact.email,
                    'address1': self.user.contact_info.address_line1,
                    'address2': self.user.contact_info.address_line2,
                    'country': self.user.contact_info.country,
                    'state': self.user.contact_info.state,
                    'zipcode': self.user.contact_info.postal_code,
                    'city': self.user.contact_info.city,
                    'phone': country_code + area_code + p_number,
                    'firstname': self.user.contact_info.contact.first_name,
                    'lastname': self.user.contact_info.contact.last_name
                },
            'enabled': True,
            'language': 'en_US',
            'business_types': [
                'buyer'
            ]
        }
        if reseller:
            user_data['notifications'] = [
                'quota',
                'reports',
                'backup_error',
                'backup_warning',
                'backup_info',
                'backup_daily_report',
                'backup_critical'
            ]
        return self.provision_admin(user_data)

    def send_email(self, admin_name, admin_created):
        email_data = {'login': admin_name, 'email': self.user.contact_info.contact.email,
                      'user_id': admin_created['id']}
        self.send_activation_mail(email_data)

    def access_policies(self, admin_created, tenant_created, reseller=False):
        access_policies = {"items": [{
            "trustee_type": "user",
            "version": 0,
            "issuer_id": "00000000-0000-0000-0000-000000000000",
            "role_id": "partner_admin" if reseller else "backup_user",
            "trustee_id": admin_created['id'],
            "tenant_id": tenant_created['id'],
            "id": "00000000-0000-0000-0000-000000000000"
        }]}

        self.create_access_policies(admin_created['id'], access_policies)
