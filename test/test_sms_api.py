from unittest import TestCase
from datetime import datetime, timezone

from dt_sms_sdk.sms_api import Client, NotAuthorizedError, SenderNumberNotVerifiedError, UnsupportedMediaTypeError, \
    NotEnoughMoneyOnTheWalletError, InternalSMSAPIError, NoRouteToRecipientNumberError, SMSAPIError, \
    SMSAPIMessageStatus, SMSMessageDirection, MessageNotFoundError
from dt_sms_sdk.message import Message

import requests_mock
import requests


class DTSMSSDKAPIClient(TestCase):

    def _test_request_get(self, request: requests.Request, expected_key):
        self.assertTrue("X-API-Key" in request.headers.keys())
        self.assertEqual(request.headers["X-API-Key"], expected_key)
        self.assertTrue(request.url.startswith("https://api.telekom.com/service/sms/v1/messages/"))
        self.assertEqual(request.method, "GET")

    def _test_request_post(self, request: requests.Request, expected_key):
        self.assertTrue("X-API-Key" in request.headers.keys())
        self.assertEqual(request.headers["X-API-Key"], expected_key)
        self.assertEqual(request.headers["Content-Type"], 'application/x-www-form-urlencoded')
        self.assertEqual(request.url, "https://api.telekom.com/service/sms/v1/messages")
        self.assertEqual(request.method, "POST")

    def test_init(self):
        c = Client(api_key="myKey")
        self.assertEqual(c.api_key, "myKey")

    def test_send_401(self):
        def custom_matcher(request):
            self._test_request_post(request, "Invalid Key")
            resp = requests.Response()
            resp.status_code = 401
            resp._content = ''
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            c = Client(api_key="Invalid Key")
            m = Message(_from="+491755555555", _to="+4915111111111", _body="Hello World")
            self.assertRaises(NotAuthorizedError, c.send, m)

    def test_send_415(self):
        def custom_matcher(request):
            self._test_request_post(request, "Invalid Media Type")
            resp = requests.Response()
            resp.status_code = 415
            # normally the header field content type is referred in the message between \'\'
            resp._content = b'{\n' + \
                            b'    "timestamp": "2023-01-11T08:06:51.631+00:00",\n' + \
                            b'    "path": "/service/sms/v1/messages",\n' + \
                            b'    "status": 415,\n' + \
                            b'    "error": "Unsupported Media Type",\n' + \
                            b'    "message": "Content type \'\' not supported",\n' + \
                            b'    "requestId": "ffc84d0f-164227"\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            c = Client(api_key="Invalid Media Type")
            m = Message(_from="+491755555555", _to="+4915111111111", _body="Hello World")
            self.assertRaises(UnsupportedMediaTypeError, c.send, m)

    def test_send_422_invalid_number(self):
        def custom_matcher(request):
            self._test_request_post(request, "Invalid Number")
            resp = requests.Response()
            resp.status_code = 422
            resp._content = b'{\n' + \
                            b'    "timestamp": "2023-01-11T08:06:51.631+00:00",\n' + \
                            b'    "path": "/service/sms/v1/messages",\n' + \
                            b'    "status": 422,\n' + \
                            b'    "error": "Unprocessable Entity",\n' + \
                            b'    "message": "Number: +491755555555 cannot be used because is not verified",\n' + \
                            b'    "requestId": "ffc84d0f-164227"\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            c = Client(api_key="Invalid Number")
            m = Message(_from="+491755555555", _to="+4915111111111", _body="Hello World")
            self.assertRaises(SenderNumberNotVerifiedError, c.send, m)

    def test_send_422_not_enough_money(self):
        def custom_matcher(request):
            self._test_request_post(request, "Invalid Number")
            resp = requests.Response()
            resp.status_code = 422
            resp._content = b'{\n' + \
                            b'    "timestamp": "2023-01-11T08:06:51.631+00:00",\n' + \
                            b'    "path": "/service/sms/v1/messages",\n' + \
                            b'    "status": 422,\n' + \
                            b'    "error": "Unprocessable Entity",\n' + \
                            b'    "message": "Not enough money on the wallet",\n' + \
                            b'    "requestId": "ffc84d0f-164227"\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            c = Client(api_key="Invalid Number")
            m = Message(_from="+491755555555", _to="+4915111111111", _body="Hello World")
            self.assertRaises(NotEnoughMoneyOnTheWalletError, c.send, m)

    def test_send_422_invalid_route(self):
        def custom_matcher(request):
            self._test_request_post(request, "Invalid Route")
            resp = requests.Response()
            resp.status_code = 422
            resp._content = b'{\n' + \
                            b'    "timestamp": "2023-01-11T08:06:51.631+00:00",\n' + \
                            b'    "path": "/service/sms/v1/messages",\n' + \
                            b'    "status": 422,\n' + \
                            b'    "error": "Unprocessable Entity",\n' + \
                            b'    "message": "No routing available for sms from: +491755555555 to: +49203555555",\n' + \
                            b'    "requestId": "ffc84d0f-164227"\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            c = Client(api_key="Invalid Route")
            m = Message(_from="+491755555555", _to="+4915111111111", _body="Hello World")
            self.assertRaises(NoRouteToRecipientNumberError, c.send, m)

    def test_send_422_future_error(self):
        def custom_matcher(request):
            self._test_request_post(request, "Future")
            resp = requests.Response()
            resp.status_code = 422
            resp._content = b'{\n' + \
                            b'    "timestamp": "2023-01-11T08:06:51.631+00:00",\n' + \
                            b'    "path": "/service/sms/v1/messages",\n' + \
                            b'    "status": 422,\n' + \
                            b'    "error": "Unprocessable Entity",\n' + \
                            b'    "message": "In the future I do not want to do SMS anymore ;-)",\n' + \
                            b'    "requestId": "ffc84d0f-164227"\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            c = Client(api_key="Future")
            m = Message(_from="+491755555555", _to="+4915111111111", _body="Hello World")
            self.assertRaises(SMSAPIError, c.send, m)

    def test_send_500(self):
        def custom_matcher(request):
            self._test_request_post(request, "Server Error")
            resp = requests.Response()
            resp.status_code = 500
            resp._content = b'{\n' + \
                            b'    "timestamp": "2023-01-11T08:06:51.631+00:00",\n' + \
                            b'    "path": "/service/sms/v1/messages",\n' + \
                            b'    "status": 500,\n' + \
                            b'    "error": "Internal Server Error",\n' + \
                            b'    "message": "Something went wrong.",\n' + \
                            b'    "requestId": "ffc84d0f-164227"\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            c = Client(api_key="Server Error")
            m = Message(_from="+491755555555", _to="+4915111111111", _body="Hello World")
            self.assertRaises(InternalSMSAPIError, c.send, m)

    def test_send_200(self):
        def custom_matcher(request):
            self._test_request_post(request, "Good Case")
            self.assertEqual(request.body, 'From=%2B491755555555&To=%2B4915111111111&Body=Hello+World')

            resp = requests.Response()
            resp.status_code = 200
            resp._content = b'{\n' + \
                            b'    "sid":"23bcd1bb62dc2248596d52e9",\n' + \
                            b'    "date_created":"Wed, 11 Jan 2023 15:11:55 +0000",\n' + \
                            b'    "date_updated":"Wed, 11 Jan 2023 15:11:56 +0000",\n' + \
                            b'    "from":"+491755555555",\n' + \
                            b'    "to":"+4915111111111",\n' + \
                            b'    "body":"Hello World",\n' + \
                            b'    "status":"accepted",\n' + \
                            b'    "uri":"/service/sms/v1/messages/23bcd1bb62dc2248596d52e9",\n' + \
                            b'    "direction":"outbound-api",\n' + \
                            b'    "api_version":"1.1.5",\n' + \
                            b'    "num_segments":1\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            c = Client(api_key="Good Case")
            m = Message(_from="+491755555555", _to="+4915111111111", _body="Hello World")
            r = c.send(m)
            self.assertEqual(r.sid, "23bcd1bb62dc2248596d52e9")
            self.assertEqual(r.date_created, datetime(year=2023, month=1, day=11,
                                                      hour=15, minute=11, second=55, tzinfo=timezone.utc))
            self.assertEqual(r.date_updated, datetime(year=2023, month=1, day=11,
                                                      hour=15, minute=11, second=56, tzinfo=timezone.utc))
            self.assertTrue(isinstance(r.message, Message))
            self.assertEqual(str(r.message.sender), "+491755555555")
            self.assertEqual(str(r.message.recipient), "+4915111111111")
            self.assertEqual(r.message.body, "Hello World")
            self.assertEqual(r.status, SMSAPIMessageStatus.ACCEPTED)
            self.assertEqual(r.uri, "/service/sms/v1/messages/23bcd1bb62dc2248596d52e9")
            self.assertEqual(r.direction, SMSMessageDirection.OUTBOUND)
            self.assertEqual(r.api_version, "1.1.5")
            self.assertEqual(r.num_segments, 1)

    def test_send_200_num_seg_mismath(self):
        def custom_matcher(request):
            self._test_request_post(request, "Good Case")
            self.assertEqual(request.body, 'From=%2B491755555555&To=%2B4915111111111&Body=Hello+World')

            resp = requests.Response()
            resp.status_code = 200
            resp._content = b'{\n' + \
                            b'    "sid":"23bcd1bb62dc2248596d52e9",\n' + \
                            b'    "date_created":"Wed, 11 Jan 2023 15:11:55 +0000",\n' + \
                            b'    "date_updated":"Wed, 11 Jan 2023 15:11:56 +0000",\n' + \
                            b'    "from":"+491755555555",\n' + \
                            b'    "to":"+4915111111111",\n' + \
                            b'    "body":"Hello World",\n' + \
                            b'    "status":"accepted",\n' + \
                            b'    "uri":"/service/sms/v1/messages/23bcd1bb62dc2248596d52e9",\n' + \
                            b'    "direction":"outbound-api",\n' + \
                            b'    "api_version":"1.1.5",\n' + \
                            b'    "num_segments":2\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            c = Client(api_key="Good Case")
            m = Message(_from="+491755555555", _to="+4915111111111", _body="Hello World")
            with self.assertLogs() as captured:
                r = c.send(m)
            self.assertEqual(r.sid, "23bcd1bb62dc2248596d52e9")
            self.assertEqual(r.date_created, datetime(year=2023, month=1, day=11,
                                                      hour=15, minute=11, second=55, tzinfo=timezone.utc))
            self.assertEqual(r.date_updated, datetime(year=2023, month=1, day=11,
                                                      hour=15, minute=11, second=56, tzinfo=timezone.utc))
            self.assertTrue(isinstance(r.message, Message))
            self.assertEqual(str(r.message.sender), "+491755555555")
            self.assertEqual(str(r.message.recipient), "+4915111111111")
            self.assertEqual(r.message.body, "Hello World")
            self.assertEqual(r.status, SMSAPIMessageStatus.ACCEPTED)
            self.assertEqual(r.uri, "/service/sms/v1/messages/23bcd1bb62dc2248596d52e9")
            self.assertEqual(r.direction, SMSMessageDirection.OUTBOUND)
            self.assertEqual(r.api_version, "1.1.5")
            self.assertEqual(r.num_segments, 2)  # this one is set wrong to simulate API split more than we assume
            # when SDK and API calculate different num seg, SDK places a warning in the logs
            self.assertEqual(len(captured.records), 1)
            self.assertEqual(captured.records[0].getMessage(),
                             "DT SMS API split the message into 2 while SDK calculates 1 splits!")

    def test_send_xxx_future_error(self):
        def custom_matcher(request):
            self._test_request_post(request, "Future2")
            resp = requests.Response()
            resp.status_code = 499
            resp._content = b'{\n' + \
                            b'    "timestamp": "2023-01-11T08:06:51.631+00:00",\n' + \
                            b'    "path": "/service/sms/v1/messages",\n' + \
                            b'    "status": 499,\n' + \
                            b'    "error": "Future Error",\n' + \
                            b'    "message": "In the future I do not want to do SMS anymore ;-)",\n' + \
                            b'    "requestId": "ffc84d0f-164227"\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            c = Client(api_key="Future2")
            m = Message(_from="+491755555555", _to="+4915111111111", _body="Hello World")
            self.assertRaises(SMSAPIError, c.send, m)

    def test_status_200(self):
        def custom_matcher(request):
            self._test_request_get(request, "Good Case")
            self.assertEqual(request.url, "https://api.telekom.com/service/sms/v1/messages/23bcd1bb62dc2248596d52e9")
            resp = requests.Response()
            resp.status_code = 200
            resp._content = b'{\n' + \
                            b'    "sid":"23bcd1bb62dc2248596d52e9",\n' + \
                            b'    "date_created":"Wed, 11 Jan 2023 15:11:55 +0000",\n' + \
                            b'    "date_updated":"Wed, 11 Jan 2023 15:11:56 +0000",\n' + \
                            b'    "from":"+491755555555",\n' + \
                            b'    "to":"+4915111111111",\n' + \
                            b'    "body":"Hello World",\n' + \
                            b'    "status":"accepted",\n' + \
                            b'    "uri":"/service/sms/v1/messages/23bcd1bb62dc2248596d52e9",\n' + \
                            b'    "direction":"outbound-api",\n' + \
                            b'    "api_version":"1.1.5",\n' + \
                            b'    "num_segments":1\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            c = Client(api_key="Good Case")
            r = c.status("23bcd1bb62dc2248596d52e9")
            self.assertEqual(r.sid, "23bcd1bb62dc2248596d52e9")
            self.assertEqual(r.date_created, datetime(year=2023, month=1, day=11,
                                                      hour=15, minute=11, second=55, tzinfo=timezone.utc))
            self.assertEqual(r.date_updated, datetime(year=2023, month=1, day=11,
                                                      hour=15, minute=11, second=56, tzinfo=timezone.utc))
            self.assertTrue(isinstance(r.message, Message))
            self.assertEqual(str(r.message.sender), "+491755555555")
            self.assertEqual(str(r.message.recipient), "+4915111111111")
            self.assertEqual(r.message.body, "Hello World")
            self.assertEqual(r.status, SMSAPIMessageStatus.ACCEPTED)
            self.assertEqual(r.uri, "/service/sms/v1/messages/23bcd1bb62dc2248596d52e9")
            self.assertEqual(r.direction, SMSMessageDirection.OUTBOUND)
            self.assertEqual(r.api_version, "1.1.5")
            self.assertEqual(r.num_segments, 1)

    def test_status_200_num_seg_mismath(self):
        def custom_matcher(request):
            self._test_request_get(request, "Good Case")
            self.assertEqual(request.url, "https://api.telekom.com/service/sms/v1/messages/23bcd1bb62dc2248596d52e9")
            resp = requests.Response()
            resp.status_code = 200
            resp._content = b'{\n' + \
                            b'    "sid":"23bcd1bb62dc2248596d52e9",\n' + \
                            b'    "date_created":"Wed, 11 Jan 2023 15:11:55 +0000",\n' + \
                            b'    "date_updated":"Wed, 11 Jan 2023 15:11:56 +0000",\n' + \
                            b'    "from":"+491755555555",\n' + \
                            b'    "to":"+4915111111111",\n' + \
                            b'    "body":"Hello World",\n' + \
                            b'    "status":"accepted",\n' + \
                            b'    "uri":"/service/sms/v1/messages/23bcd1bb62dc2248596d52e9",\n' + \
                            b'    "direction":"outbound-api",\n' + \
                            b'    "api_version":"1.1.5",\n' + \
                            b'    "num_segments":2\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            c = Client(api_key="Good Case")
            with self.assertLogs() as captured:
                r = c.status("23bcd1bb62dc2248596d52e9")
            self.assertEqual(r.sid, "23bcd1bb62dc2248596d52e9")
            self.assertEqual(r.date_created, datetime(year=2023, month=1, day=11,
                                                      hour=15, minute=11, second=55, tzinfo=timezone.utc))
            self.assertEqual(r.date_updated, datetime(year=2023, month=1, day=11,
                                                      hour=15, minute=11, second=56, tzinfo=timezone.utc))
            self.assertTrue(isinstance(r.message, Message))
            self.assertEqual(str(r.message.sender), "+491755555555")
            self.assertEqual(str(r.message.recipient), "+4915111111111")
            self.assertEqual(r.message.body, "Hello World")
            self.assertEqual(r.status, SMSAPIMessageStatus.ACCEPTED)
            self.assertEqual(r.uri, "/service/sms/v1/messages/23bcd1bb62dc2248596d52e9")
            self.assertEqual(r.direction, SMSMessageDirection.OUTBOUND)
            self.assertEqual(r.api_version, "1.1.5")
            self.assertEqual(r.num_segments, 2)  # this one is set wrong to simulate API split more than we assume
            # when SDK and API calculate different num seg, SDK places a warning in the logs
            self.assertEqual(len(captured.records), 1)
            self.assertEqual(captured.records[0].getMessage(),
                             "DT SMS API split the message into 2 while SDK calculates 1 splits!")

    def test_status_401(self):
        def custom_matcher(request):
            self._test_request_get(request, "Invalid Key")
            resp = requests.Response()
            resp.status_code = 401
            resp._content = ''
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            c = Client(api_key="Invalid Key")
            self.assertRaises(NotAuthorizedError, c.status, "xxxxxxx")

    def test_status_404(self):
        def custom_matcher(request):
            self._test_request_get(request, "Invalid SID")
            resp = requests.Response()
            resp.status_code = 404
            # normally the header field content type is referred in the message between \'\'
            resp._content = b'{\n' + \
                            b'    "timestamp": "2023-01-11T08:06:51.631+00:00",\n' + \
                            b'    "path": "/service/sms/v1/messages/xxxxxxx",\n' + \
                            b'    "status": 404,\n' + \
                            b'    "error": "Not Found",\n' + \
                            b'    "message": "Message: xxxxxxx not found",\n' + \
                            b'    "requestId": "ffc84d0f-164227"\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            c = Client(api_key="Invalid SID")
            self.assertRaises(MessageNotFoundError, c.status, "xxxxxxx")

    def test_status_500(self):
        def custom_matcher(request):
            self._test_request_get(request, "Server Error")
            resp = requests.Response()
            resp.status_code = 500
            resp._content = b'{\n' + \
                            b'    "timestamp": "2023-01-11T08:06:51.631+00:00",\n' + \
                            b'    "path": "/service/sms/v1/messages/xxxxxxx",\n' + \
                            b'    "status": 500,\n' + \
                            b'    "error": "Internal Server Error",\n' + \
                            b'    "message": "Something went wrong.",\n' + \
                            b'    "requestId": "ffc84d0f-164227"\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            c = Client(api_key="Server Error")
            self.assertRaises(InternalSMSAPIError, c.status, "xxxxxxx")

    def test_status_xxx_future_error(self):
        def custom_matcher(request):
            self._test_request_get(request, "Future3")
            resp = requests.Response()
            resp.status_code = 499
            resp._content = b'{\n' + \
                            b'    "timestamp": "2023-01-11T08:06:51.631+00:00",\n' + \
                            b'    "path": "/service/sms/v1/messages/xxxxxxx",\n' + \
                            b'    "status": 499,\n' + \
                            b'    "error": "Future Error",\n' + \
                            b'    "message": "In the future I do not want to do SMS anymore ;-)",\n' + \
                            b'    "requestId": "ffc84d0f-164227"\n' + \
                            b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            c = Client(api_key="Future3")
            self.assertRaises(SMSAPIError, c.status, "xxxxxxx")

    def test_status_usage(self):
        c = Client(api_key="usage")
        self.assertRaises(ValueError, c.status, 1)
        self.assertRaises(ValueError, c.status, None)

    def test_send_and_status(self):
        def custom_matcher(request):
            resp = requests.Response()
            resp.status_code = 200
            if request.method == "POST":
                resp._content = b'{\n' + \
                                b'    "sid":"23bcd1bb62dc2248596d52e9",\n' + \
                                b'    "date_created":"Wed, 11 Jan 2023 15:11:55 +0000",\n' + \
                                b'    "date_updated":"Wed, 11 Jan 2023 15:11:56 +0000",\n' + \
                                b'    "from":"+491755555555",\n' + \
                                b'    "to":"+4915111111111",\n' + \
                                b'    "body":"Hello World",\n' + \
                                b'    "status":"accepted",\n' + \
                                b'    "uri":"/service/sms/v1/messages/23bcd1bb62dc2248596d52e9",\n' + \
                                b'    "direction":"outbound-api",\n' + \
                                b'    "api_version":"1.1.5",\n' + \
                                b'    "num_segments":1\n' + \
                                b'}'
            else:
                resp._content = b'{\n' + \
                                b'    "sid":"23bcd1bb62dc2248596d52e9",\n' + \
                                b'    "date_created":"Wed, 11 Jan 2023 15:11:55 +0000",\n' + \
                                b'    "date_updated":"Wed, 11 Jan 2023 15:11:58 +0000",\n' + \
                                b'    "from":"+491755555555",\n' + \
                                b'    "to":"+4915111111111",\n' + \
                                b'    "body":"Hello World",\n' + \
                                b'    "status":"delivered",\n' + \
                                b'    "uri":"/service/sms/v1/messages/23bcd1bb62dc2248596d52e9",\n' + \
                                b'    "direction":"outbound-api",\n' + \
                                b'    "api_version":"1.1.5",\n' + \
                                b'    "num_segments":1\n' + \
                                b'}'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            c = Client(api_key="Full")
            m = Message(_from="+491755555555", _to="+4915111111111", _body="Hello World")
            r1 = c.send(m)
            self.assertEqual(r1.sid, "23bcd1bb62dc2248596d52e9")
            self.assertEqual(r1.date_created, datetime(year=2023, month=1, day=11,
                                                      hour=15, minute=11, second=55, tzinfo=timezone.utc))
            self.assertEqual(r1.date_updated, datetime(year=2023, month=1, day=11,
                                                      hour=15, minute=11, second=56, tzinfo=timezone.utc))
            self.assertTrue(isinstance(r1.message, Message))
            self.assertEqual(str(r1.message.sender), "+491755555555")
            self.assertEqual(str(r1.message.recipient), "+4915111111111")
            self.assertEqual(r1.message.body, "Hello World")
            self.assertEqual(r1.status, SMSAPIMessageStatus.ACCEPTED)
            self.assertEqual(r1.uri, "/service/sms/v1/messages/23bcd1bb62dc2248596d52e9")
            self.assertEqual(r1.direction, SMSMessageDirection.OUTBOUND)
            self.assertEqual(r1.api_version, "1.1.5")
            self.assertEqual(r1.num_segments, 1)
            # querying status by passing the response from sending!
            r2 = c.status(r1)
            self.assertEqual(r2.sid, r1.sid)
            self.assertEqual(r2.date_created, r2.date_created)
            self.assertEqual(r2.date_updated, datetime(year=2023, month=1, day=11,
                                                       hour=15, minute=11, second=58, tzinfo=timezone.utc))
            self.assertTrue(isinstance(r2.message, Message))
            self.assertEqual(str(r2.message.sender), str(r1.message.sender))
            self.assertEqual(str(r2.message.recipient), str(r1.message.recipient))
            self.assertEqual(r2.message.body, r1.message.body)
            self.assertEqual(r2.status, SMSAPIMessageStatus.DELIVERED)
            self.assertEqual(r2.uri, r1.uri)
            self.assertEqual(r2.direction, r1.direction)
            self.assertEqual(r2.api_version, r1.api_version)
            self.assertEqual(r2.num_segments, r1.num_segments)


