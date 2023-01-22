from unittest import TestCase
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from decimal import Decimal

import dt_sms_sdk.account as account
from dt_sms_sdk.phone_number import E164PhoneNumber

import requests_mock
import requests


class DTDashboardAccount(TestCase):

    def _test_token_request_post(self, request: requests.Request):
        self.assertEqual(request.headers["Content-Type"], 'application/x-www-form-urlencoded')
        self.assertEqual(request.url, "https://developer.telekom.com/api/v1/oauth/token")
        self.assertEqual(request.method, "POST")

    def _test_wallet_request_get(self, request: requests.Request):
        self.assertTrue("User-Agent" in request.headers.keys())
        self.assertTrue("Authorization" in request.headers.keys())
        self.assertEqual(request.headers["Authorization"], "Bearer xxx")
        self.assertEqual(request.url, "https://developer.telekom.com/api/v1/wallet")
        self.assertEqual(request.method, "GET")

    def _test_api_key_request_get(self, request: requests.Request):
        self.assertTrue("User-Agent" in request.headers.keys())
        self.assertTrue("Authorization" in request.headers.keys())
        self.assertEqual(request.headers["Authorization"], "Bearer xxx")
        self.assertEqual(request.url, "https://developer.telekom.com/api/v1/api-keys")
        self.assertEqual(request.method, "GET")

    def _test_numbers_request_get(self, request: requests.Request):
        self.assertTrue("User-Agent" in request.headers.keys())
        self.assertTrue("Authorization" in request.headers.keys())
        self.assertEqual(request.headers["Authorization"], "Bearer xxx")
        self.assertEqual(request.url, "https://developer.telekom.com/api/v1/numbers")
        self.assertEqual(request.method, "GET")

    @patch(f'{account.__name__}.datetime', wraps=datetime)
    def test_token_200(self, mock_datetime):
        def custom_matcher(request):
            self._test_token_request_post(request)
            resp = requests.Response()
            resp.status_code = 200
            resp._content = b'{\n' + \
                            b'    "access_token": "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiIiJnY3AiLCJhdWQiOiJodHRwOi8vbG9jYWxob3N0IiwiaWF0IjoxNjczODgxNDQxLCJuYmYiOjE2NzM4ODEzODEsImV4cCI6MTY3MzkxMDI0MSwianRpIjoiNTlhZTc0N2ItY1QzMy00MjBkLWJjYWYtNWYwNmZkZmJkOGIzIiwiaHR0cDovL2djcC50ZWxla29tLmRlL2F4c2NoZW1hL2djcGlkIjoiMjAxMDeWMDAwNTI0MDI1NjEwMDMyMTcxNTA5OSIsImh0dHA6Ly9nY3AudGVsZWtvbS5kZS9heHNjaGVtYS9zdGF0dXMiOiJDT05GFVJNRUQifQ.QC5WahYK-qoY06HlO4P4WboToe59iwRNfgCJLkboV3E",\n' + \
                            b'    "token_type": "bearer",\n' + \
                            b'    "expires_in": 28800,\n' + \
                            b'    "refresh_token": "rQoRWtZ6WUkUtT9hFMTBuCgk_wTzpMdycyVuGqu4cGO0zVKb",\n' + \
                            b'    "scope": "7MEE5ZBJ"\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)

            mock_datetime.now.return_value = datetime(2023, 1, 1)
            a = account.Account(username="Emil@mail.com", password="SuperSecret")
            self.assertEqual(a._token,
                             "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiIiJnY3AiLCJhdWQiOiJodHRwOi8vbG9jYWxob3N0IiwiaWF0IjoxNjczODgxNDQxLCJuYmYiOjE2NzM4ODEzODEsImV4cCI6MTY3MzkxMDI0MSwianRpIjoiNTlhZTc0N2ItY1QzMy00MjBkLWJjYWYtNWYwNmZkZmJkOGIzIiwiaHR0cDovL2djcC50ZWxla29tLmRlL2F4c2NoZW1hL2djcGlkIjoiMjAxMDeWMDAwNTI0MDI1NjEwMDMyMTcxNTA5OSIsImh0dHA6Ly9nY3AudGVsZWtvbS5kZS9heHNjaGVtYS9zdGF0dXMiOiJDT05GFVJNRUQifQ.QC5WahYK-qoY06HlO4P4WboToe59iwRNfgCJLkboV3E")
            self.assertEqual(a._token_valid_until, datetime(2023, 1, 1, 8))  # 28800 sec are 8 h

    @patch(f'{account.__name__}.datetime', wraps=datetime)
    def test_token_200_short(self, mock_datetime):
        def custom_matcher(request):
            self._test_token_request_post(request)
            resp = requests.Response()
            resp.status_code = 200
            resp._content = b'{\n' + \
                            b'    "access_token": "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiIiJnY3AiLCJhdWQiOiJodHRwOi8vbG9jYWxob3N0IiwiaWF0IjoxNjczODgxNDQxLCJuYmYiOjE2NzM4ODEzODEsImV4cCI6MTY3MzkxMDI0MSwianRpIjoiNTlhZTc0N2ItY1QzMy00MjBkLWJjYWYtNWYwNmZkZmJkOGIzIiwiaHR0cDovL2djcC50ZWxla29tLmRlL2F4c2NoZW1hL2djcGlkIjoiMjAxMDeWMDAwNTI0MDI1NjEwMDMyMTcxNTA5OSIsImh0dHA6Ly9nY3AudGVsZWtvbS5kZS9heHNjaGVtYS9zdGF0dXMiOiJDT05GFVJNRUQifQ.QC5WahYK-qoY06HlO4P4WboToe59iwRNfgCJLkboV3E",\n' + \
                            b'    "token_type": "bearer",\n' + \
                            b'    "expires_in": 1,\n' + \
                            b'    "refresh_token": "rQoRWtZ6WUkUtT9hFMTBuCgk_wTzpMdycyVuGqu4cGO0zVKb",\n' + \
                            b'    "scope": "7MEE5ZBJ"\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)

            mock_datetime.now.return_value = datetime(2023, 1, 1)
            a = account.Account(username="Emil@mail.com", password="SuperSecret")
            self.assertEqual(a._token,
                             "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiIiJnY3AiLCJhdWQiOiJodHRwOi8vbG9jYWxob3N0IiwiaWF0IjoxNjczODgxNDQxLCJuYmYiOjE2NzM4ODEzODEsImV4cCI6MTY3MzkxMDI0MSwianRpIjoiNTlhZTc0N2ItY1QzMy00MjBkLWJjYWYtNWYwNmZkZmJkOGIzIiwiaHR0cDovL2djcC50ZWxla29tLmRlL2F4c2NoZW1hL2djcGlkIjoiMjAxMDeWMDAwNTI0MDI1NjEwMDMyMTcxNTA5OSIsImh0dHA6Ly9nY3AudGVsZWtvbS5kZS9heHNjaGVtYS9zdGF0dXMiOiJDT05GFVJNRUQifQ.QC5WahYK-qoY06HlO4P4WboToe59iwRNfgCJLkboV3E")
            self.assertEqual(a._token_valid_until, datetime(2023, 1, 1, 0, 0, 1))

    def test_token_400_no_username(self):
        def custom_matcher(request):
            self._test_token_request_post(request)
            resp = requests.Response()
            resp.status_code = 400
            resp._content = b'{\n' + \
                            b'    "timestamp": "2023-01-16T20:35:17.812+00:00",\n' + \
                            b'    "path": "/oauth/token",\n' + \
                            b'    "status": 400,\n' + \
                            b'    "error": "Bad Request",\n' + \
                            b'    "message": "must not be empty, Username must contain a well-formed email address or a valid user id",\n' + \
                            b'    "requestId": "37600633-37433",\n' + \
                            b'    "traceId": "0bea1929f7710ab1"\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            self.assertRaises(account.LoginError, account.Account, "", "SuperSecret")

    def test_token_400_username_no_email(self):
        def custom_matcher(request):
            self._test_token_request_post(request)
            resp = requests.Response()
            resp.status_code = 400
            resp._content = b'{\n' + \
                            b'    "timestamp": "2023-01-16T20:35:17.812+00:00",\n' + \
                            b'    "path": "/oauth/token",\n' + \
                            b'    "status": 400,\n' + \
                            b'    "error": "Bad Request",\n' + \
                            b'    "message": "Username must contain a well-formed email address or a valid user id",\n' + \
                            b'    "requestId": "37600633-37433",\n' + \
                            b'    "traceId": "0bea1929f7710ab1"\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            self.assertRaises(account.LoginError, account.Account, "Emil@mail", "SuperSecret")

    def test_token_400_no_password(self):
        def custom_matcher(request):
            self._test_token_request_post(request)
            resp = requests.Response()
            resp.status_code = 400
            resp._content = b'{\n' + \
                            b'    "timestamp": "2023-01-16T20:35:17.812+00:00",\n' + \
                            b'    "path": "/oauth/token",\n' + \
                            b'    "status": 400,\n' + \
                            b'    "error": "Bad Request",\n' + \
                            b'    "message": "Password length must be between: 12 and 999 characters",\n' + \
                            b'    "requestId": "37600633-37433",\n' + \
                            b'    "traceId": "0bea1929f7710ab1"\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            self.assertRaises(account.LoginError, account.Account, "emil@mail.com", "")

    def test_token_400_no_username_nor_password(self):
        def custom_matcher(request):
            self._test_token_request_post(request)
            resp = requests.Response()
            resp.status_code = 400
            resp._content = b'{\n' + \
                            b'    "timestamp": "2023-01-16T20:35:17.812+00:00",\n' + \
                            b'    "path": "/oauth/token",\n' + \
                            b'    "status": 400,\n' + \
                            b'    "error": "Bad Request",\n' + \
                            b'    "message": "Password length must be between: 12 and 999 characters, Username must contain a well-formed email address or a valid user id, must not be empty",\n' + \
                            b'    "requestId": "37600633-37433",\n' + \
                            b'    "traceId": "0bea1929f7710ab1"\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            self.assertRaises(account.LoginError, account.Account, "", "")

    def test_token_400_username_no_email_no_passwort(self):
        def custom_matcher(request):
            self._test_token_request_post(request)
            resp = requests.Response()
            resp.status_code = 400
            resp._content = b'{\n' + \
                            b'    "timestamp": "2023-01-16T20:35:17.812+00:00",\n' + \
                            b'    "path": "/oauth/token",\n' + \
                            b'    "status": 400,\n' + \
                            b'    "error": "Bad Request",\n' + \
                            b'    "message": "Username must contain a well-formed email address or a valid user id, must not be empty, Password length must be between: 12 and 999 characters",\n' + \
                            b'    "requestId": "37600633-37433",\n' + \
                            b'    "traceId": "0bea1929f7710ab1"\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            self.assertRaises(account.LoginError, account.Account, "Emil@mail", "")

    def test_token_401(self):
        def custom_matcher(request):
            self._test_token_request_post(request)
            resp = requests.Response()
            resp.status_code = 401
            resp._content = b'{\n' + \
                            b'    "timestamp": "2023-01-16T20:35:17.812+00:00",\n' + \
                            b'    "path": "/oauth/token",\n' + \
                            b'    "status": 401,\n' + \
                            b'    "error": "Unauthorized",\n' + \
                            b'    "message": "Invalid user credential",\n' + \
                            b'    "requestId": "37600633-37433",\n' + \
                            b'    "traceId": "0bea1929f7710ab1"\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            self.assertRaises(account.LoginError, account.Account, "Emil@mail.com", "HackIt")

    def _dummy_account(self) -> account.Account:
        a = account.Account(username="emil@mail.com", password="SuperSecret", auto_login=False)
        a._token = "xxx"
        a._token_valid_until = datetime.now(timezone.utc) + timedelta(1)
        return a

    def test_wallet_200(self):
        def custom_matcher(request):
            self._test_wallet_request_get(request)
            resp = requests.Response()
            resp.status_code = 200
            resp._content = b'{\n' + \
                            b'    "balance":5.26,\n' + \
                            b'    "currency":"EUR"\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            a = self._dummy_account()
            self.assertEqual(a.wallet(), account.Wallet(balance=Decimal("5.26"), currency="EUR"))

    def test_wallet_401(self):
        def custom_matcher(request):
            self._test_wallet_request_get(request)
            resp = requests.Response()
            resp.status_code = 401
            resp._content = b''
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            a = self._dummy_account()
            from dt_sms_sdk.account import TokenError
            self.assertRaises(TokenError, a.wallet)

    def test_wallet_xxx_future_error(self):
        def custom_matcher(request):
            self._test_wallet_request_get(request)
            resp = requests.Response()
            resp.status_code = 499
            resp._content = b''
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            a = self._dummy_account()
            from dt_sms_sdk.account import DashboardError
            self.assertRaises(DashboardError, a.wallet)

    def test_api_key_200(self):
        def custom_matcher(request):
            self._test_api_key_request_get(request)
            resp = requests.Response()
            resp.status_code = 200
            resp._content = b'{\n' + \
                            b'    "rawApiKey": "TWp8MllUUmpPV1l0TkRnek9TMDBPVFTppERsa01EZ3ROakF3TlRJMU9ETTNOV05qUUdaaFpqaGxZek5sTFRSaU0yTXROR1V5WmkxaE4ySm1MVFJtTVrSaU1HUTJZelJrWlE9PToyZjNiODJjMy00ZjYzLTQwZDctYWI9NS0xOTEzZTAxNTU4NTg="\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            a = self._dummy_account()
            self.assertEqual(a.api_key(), "TWp8MllUUmpPV1l0TkRnek9TMDBPVFTppERsa01EZ3ROakF3TlRJMU9ETTNOV05qUUdaaFpqaGxZek5sTFRSaU0yTXROR1V5WmkxaE4ySm1MVFJtTVrSaU1HUTJZelJrWlE9PToyZjNiODJjMy00ZjYzLTQwZDctYWI9NS0xOTEzZTAxNTU4NTg=")

    def test_api_key_401(self):
        def custom_matcher(request):
            self._test_api_key_request_get(request)
            resp = requests.Response()
            resp.status_code = 401
            resp._content = b''
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            a = self._dummy_account()
            from dt_sms_sdk.account import TokenError
            self.assertRaises(TokenError, a.api_key)

    def test_api_key_xxx_future_error(self):
        def custom_matcher(request):
            self._test_api_key_request_get(request)
            resp = requests.Response()
            resp.status_code = 499
            resp._content = b''
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            a = self._dummy_account()
            from dt_sms_sdk.account import DashboardError
            self.assertRaises(DashboardError, a.api_key)

    def test_numbers_key_200(self):
        def custom_matcher(request):
            self._test_numbers_request_get(request)
            resp = requests.Response()
            resp.status_code = 200
            resp._content = b'[{\n' + \
                            b'    "id": "6a9dd48dbc05aa37862babcd",\n' + \
                            b'    "number": "+491755555555",\n' + \
                            b'    "status": "VERIFIED"\n,' + \
                            b'    "serviceId": "/service/sms/v1"\n' + \
                            b'}]'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            a = self._dummy_account()
            l = a.phone_numbers()
            self.assertEqual(len(l), 1)
            self.assertEqual(l[0].number, E164PhoneNumber("+491755555555"))

    def test_numbers_key_401(self):
        def custom_matcher(request):
            self._test_numbers_request_get(request)
            resp = requests.Response()
            resp.status_code = 401
            resp._content = b''
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            a = self._dummy_account()
            from dt_sms_sdk.account import TokenError
            self.assertRaises(TokenError, a.phone_numbers)

    def test_numbers_xxx_future_error(self):
        def custom_matcher(request):
            self._test_numbers_request_get(request)
            resp = requests.Response()
            resp.status_code = 499
            resp._content = b''
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            a = self._dummy_account()
            from dt_sms_sdk.account import DashboardError
            self.assertRaises(DashboardError, a.phone_numbers)
