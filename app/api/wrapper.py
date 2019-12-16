"""
This file is property of the Ingram Micro Cloud Blue.
Copyright (c) 2019 Ingram Micro. All Rights Reserved.
"""
from app.api.client import Client
from connect.exceptions import InquireRequest, FailRequest
from base64 import b64encode


class Wrapper:
    config = None

    def configure(self, config):
        self.config = config

    # V1 environment methods
    def auth_v1(self):
        # self.config['service']['host'] = self.get_stack_info()
        user_pass = self.config['service']['username'] + ':' + self.config['service']['password']
        self.config['basic'] = b64encode(str.encode(user_pass)).decode("ascii")

    def get_stack_info(self):
        method = '/accounts?login=%s' + self.config['service']['username']
        self.config['Content-Type'] = 'application/json'
        uri = self.config['service']['root_host'] + self.config['service']['api_version_old'] + method
        response = Client.send_request('GET', uri, self.config)
        return response['server_url']

    def v1_call(self, verb, method, data=None):
        self.auth_v1()
        uri = self.config['service']['host'] + self.config['service']['api_version_old'] + method
        self.config['Content-Type'] = 'application/json'
        return Client.send_request(verb, uri, self.config, data)

    # V1 methods

    def sso(self, user_id):
        method = '/admins/%s/impersonate' % user_id
        return self.v1_call('GET', method)

    def get_group_id(self, uuid):
        method = '/groups/' + uuid
        return self.v1_call('GET', method)

    def get_acc_console_branded(self, group_id):
        method = '/groups/%s/brand' % group_id
        return self.v1_call('GET', method)

    def send_reset_email(self, data):
        method = '/actions/mail/reset'
        return self.v1_call('POST', method, data)

    def send_activation_mail(self, data):
        method = '/actions/mail/activate'
        return self.v1_call('POST', method, data)

    # V2 environment methods

    def v2_call(self, verb, method, data=None):
        self.auth()
        uri = self.config['service']['host'] + self.config['service']['api_version'] + method
        return Client.send_request(verb, uri, self.config, data)

    def get_token(self):
        method = '/idp/token'
        data = {'grant_type': self.config['service']['grant_type'], 'username': self.config['service']['username'],
                'password': self.config['service']['password']}
        self.config['Content-Type'] = 'application/x-www-form-urlencoded'
        uri = self.config['service']['host'] + self.config['service']['api_version'] + method
        return Client.send_request('POST', uri, self.config, data)

    def get_logged_user(self):
        method = '/users/me'
        self.config['Content-Type'] = 'application/json'
        uri = self.config['service']['host'] + self.config['service']['api_version'] + method
        return Client.send_request('GET', uri, self.config)

    def auth(self):
        if not 'bearer' in self.config:
            # self.config['service']['host'] = self.get_stack_info()
            self.config['bearer'] = self.get_token()['access_token']
            self.config['tenant_id'] = self.get_logged_user()['tenant_id']

    # V2 methods

    def provision(self, data):
        method = '/tenants'
        self.auth()
        if data['kind'] is not 'customer':
            data['parent_id'] = self.config['tenant_id']
        uri = self.config['service']['host'] + self.config['service']['api_version'] + method
        return Client.send_request('POST', uri, self.config, data)

    def provision_admin(self, data):
        method = '/users'
        return self.v2_call('POST', method, data)

    def edit(self, tenant_id, data):
        method = '/tenants/' + tenant_id
        return self.v2_call('PUT', method, data)

    def remove(self, tenant_id, version, data):
        method = '/tenants/%s?version=%s' % (tenant_id, version)
        return self.v2_call('DELETE', method, data)

    def get_tenant_info(self, tenant_id):  # Get reseller info in old php connector
        method = '/tenants/' + tenant_id
        return self.v2_call('GET', method)

    def create_access_policies(self, admin_id, data):
        method = '/users/%s/access_policies' % admin_id
        return self.v2_call('PUT', method, data)

    def get_available_offerings(self, tenant_id, child=False):
        method = '/tenants/%s/offering_items' % tenant_id
        if child:
            method += '/available_for_child'
        return self.v2_call('GET', method)

    def set_offerings_for_children(self, tenant_id, data):
        method = '/tenants/%s/offering_items' % tenant_id
        return self.v2_call('PUT', method, data)

    def get_offerings_for_children(self, tenant_id):
        method = '/tenants/%s/offering_items' % tenant_id
        return self.v2_call('GET', method)

    def get_available_apps(self, tenant_id):
        method = '/tenants/%s/applications' % tenant_id
        return self.v2_call('GET', method)

    def check_login(self, username):
        try:
            method = '/users/check_login?username=' + username
            return self.v2_call('GET', method)
        except Exception as err:
            if err.args[0]['code'] == 409:
                raise InquireRequest(err.args[0]['message'])
            else:
                raise FailRequest(err.args[0]['message'])
