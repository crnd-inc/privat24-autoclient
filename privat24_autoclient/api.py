import json
from datetime import datetime, timedelta

import requests

PAYMENT_REQUIDED_FIELDS = [
    'document_number',
    'recipient_nceo',
    'payment_naming',
    'recipient_ifi',
    'payment_amount',
    'payment_destination',
]

PAYMENT_FIELDS = PAYMENT_REQUIDED_FIELDS + [
    'recipient_account',
    'recipient_card',

    'document_type',
    'payment_date',
    'payment_accept_date',
    'payment_cb_ref',
    'copy_from_ref',
    'attach',
    'signer_msg',
    'odb_msg',
    'recipient_ifi_text',
]


class Privat24AutoclientApi(object):
    BASE_URL = 'https://acp.privatbank.ua/api/proxy'
    HEADERS = {
        'User-Agent': 'python',
        'id': '',
        'Token': '',
        'Content-Type': 'application/json;charset=utf8',
        'Accept': 'application/json',
    }

    def __init__(self, bank_acc_number, client_id, token):
        super().__init__()
        self.bank_acc_number = bank_acc_number
        self.HEADERS['id'] = client_id
        self.HEADERS['Token'] = token

    def request_url(self, type_request='data', **arg):
        url = '{}/{}'.format(self.BASE_URL, type_request)
        r = requests.get(url, params=arg, headers=self.HEADERS)
        if r.status_code in [200, 201]:
            if type_request == 'data':
                return r.json()
            if type_request == 'transactions':
                return r.json()['StatementsResponse']['statements']
            if type_request == 'rest':
                return r.json()['balanceResponse']
        elif r.status_code == 400:
            raise Exception(
                'Invalid request format or missing one or more required '
                'headers! Error 400')
        elif r.status_code == 401:
            raise Exception(
                'Incorrect credentials for access (id and / or token)! '
                'Error 401')
        elif r.status_code == 403:
            raise Exception(
                'If the account is disabled through the management '
                'interface of the Privat24 for Businesses! Error 403}')
        elif r.status_code == 500 or r.status_code == 502:
            raise Exception(
                'Internal server error! Status code {}'.format(r.status_code))
        elif r.status_code == 503 or r.status_code == 504:
            raise Exception(
                'Server temporary is unavailable! Status code {}'.format(
                    r.status_code))

    def get_statement_today(self):
        return self.get_statement(datetime.now(), datetime.now())

    def get_statement_yesterday(self):
        yesterday = datetime.now() - timedelta(days=1)
        return self.get_statement(yesterday, yesterday)

    def get_statement(self, start_date, end_date):
        start_date_text = datetime.strftime(start_date, "%d-%m-%Y")
        end_date_text = datetime.strftime(end_date, "%d-%m-%Y")
        return self.request_url(
            type_request='transactions',
            period='date',
            acc=self.bank_acc_number.replace(' ', ''),
            startDate=start_date_text,
            endDate=end_date_text,
        )

    def get_rest_today(self):
        return self.get_rest(datetime.now(), datetime.now())

    def get_rest_yesterday(self):
        yesterday = datetime.now() - timedelta(days=1)
        return self.get_rest(yesterday, yesterday)

    def get_rest(self, start_date, end_date):
        start_date_text = datetime.strftime(start_date, "%d-%m-%Y")
        end_date_text = datetime.strftime(end_date, "%d-%m-%Y")
        return self.request_url(
            type_request='rest',
            period='date',
            acc=self.bank_acc_number,
            startDate=start_date_text,
            endDate=end_date_text,
        )

    def get_server_date(self):
        return self.request_url(type_request='date', )

    def create_payment(self, **kwargs):
        kwargs['payer_account'] = self.bank_acc_number

        for x in PAYMENT_REQUIDED_FIELDS:
            if x not in kwargs.keys():
                raise Exception(
                    '"{}" parameter is required!'.format(x))

        if 'recipient_account' not in kwargs.keys() and \
                'recipient_card' not in kwargs.keys():
            raise Exception(
                '"recipient_account" or "recipient_card" '
                'parameter is required!')

        for x in kwargs.keys():
            if x not in PAYMENT_FIELDS:
                kwargs.pop(x)

        return self.request_url(
            type_request='payment/create_pred',
            body=json.dumps(kwargs),
        )
