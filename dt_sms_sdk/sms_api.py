import requests
from datetime import datetime
from enum import Enum
from typing import Union

from dt_sms_sdk.message import Message
from dt_sms_sdk.phone_number import E164PhoneNumber

import logging
logger = logging.getLogger(__name__)


class SMSAPIError(Exception):
    """
    A basic Error class for Errors returned by the DT SMS API
    """
    pass


class SMSAPINotReachableError(SMSAPIError):
    """
    A general Error if the DT SMS API could not be reached technically.
    """
    pass


class MessageNotFoundError(SMSAPIError):
    """
    A specific Error class for a 404 returned by the DT SMS API

    Attributes
    ----------
    sid: str
        The sid of the message for which the status has been requested
    """
    sid: str

    def __init__(self, sid):
        self.sid = sid
        super().__init__(f'The sid "{sid}" was not found by the DT SMS API.')


class NotAuthorizedError(SMSAPIError):
    """
    A specific Error class for a 401 returned by the DT SMS API

    Attributes
    ----------
    api_key: str
        The API key which could not be authorized
    """
    api_key: str

    def __init__(self, api_key):
        self.api_key = api_key
        super().__init__(f'The API Key "{api_key}" was not accepted by the DT SMS API.')


class SenderNumberNotVerifiedError(SMSAPIError):
    """
    A specific Error class for a 422 returned by the DT SMS API, which also
    has an error message with the pattern 'Number: %1 cannot be used because is not verified'

    Attributes
    ----------
    api_key: str
        The API key where the sender_number needs to be registered
    sender_number: str
        The Number which should be registered under the API Key
    """
    api_key: str
    sender_number: str

    def __init__(self, api_key, sender_number):
        self.api_key = api_key
        self.sender_number = sender_number
        super().__init__(f'"{sender_number}" is not verified for the account of the API key "{api_key}".')


class NoRouteToRecipientNumberError(SMSAPIError):
    """
    A specific Error class for a 422 returned by the DT SMS API, which also
    has an error message with the pattern 'No routing available for sms from: %1 to: %2'

    Attributes
    ----------
    api_key: str
        The API key which is used for sending
    recipient_number: str
        The Number where SMS should be sent to
    """
    api_key: str
    recipient_number: str

    def __init__(self, recipient_number):
        self.recipient_number = recipient_number
        super().__init__(f'"API has no route to send SMS to {recipient_number}".')


class UnsupportedMediaTypeError(SMSAPIError):
    """
    A specific Error class for a 415 returned by the DT SMS API
    """
    pass


class InternalSMSAPIError(SMSAPIError):
    """
    A specific Error class for a 500 returned by the DT SMS API
    """
    pass


class NotEnoughMoneyOnTheWalletError(SMSAPIError):
    """
    A specific Error class for a 422 returned by the DT SMS API, which also
    has an error message with the pattern 'Not enough money on the wallet'

    Attributes
    ----------
    api_key: str
        The API key of which wallet is not sufficient
    """
    api_key: str

    def __init__(self, api_key):
        self.api_key = api_key
        super().__init__(f'The wallet for the account of the API key "{api_key}" does not have enough money.')


class SMSAPIMessageStatus(Enum):
    """
    Enumeration used in SMSAPIResponse Class to specify the status of the request.
    """
    ACCEPTED = "accepted"
    QUEUED = "queued"
    UNDELIVERED = "undelivered"
    RECEIVED = "received"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"

    @staticmethod
    def from_str(label: str):
        """
        Returns Enum value for a status for a given string

        Parameters
        ----------
        label: str
            representing a status

        Returns
        -------
        SMSAPIMessageStatus
            An SMSAPIMessageStatus if value could be mapped or None if not.
        """
        if label:
            temp_label = label.upper()
            if temp_label == 'ACCEPTED':
                return SMSAPIMessageStatus.ACCEPTED
            elif temp_label == 'QUEUED':
                return SMSAPIMessageStatus.QUEUED
            elif temp_label == 'UNDELIVERED':
                return SMSAPIMessageStatus.UNDELIVERED
            elif temp_label == 'SENDING':
                return SMSAPIMessageStatus.SENDING
            elif temp_label == 'SENT':
                return SMSAPIMessageStatus.SENT
            elif temp_label == 'DELIVERED':
                return SMSAPIMessageStatus.DELIVERED
            elif temp_label == 'FAILED':
                return SMSAPIMessageStatus.FAILED
        logger.error(f'SMSAPIMessageStatus: {label} could not be transferred to a valid SMSAPIMessageStatus value!')


class SMSMessageDirection(Enum):
    """
    Enumeration used in SMSAPIResponse Class to specify the direction of the request.

    Currently only the 'outbound-api' is supported.
    """
    OUTBOUND = "outbound-api"

    @staticmethod
    def from_str(label: str):
        """
        Returns Enum value for a direction for a given string

        Parameters
        ----------
        label: str
            representing a direction

        Returns
        -------
        SMSMessageDirection
            An SMSMessageDirection if value could be mapped or None if not.
        """
        if label and label.upper() == 'OUTBOUND-API':
            return SMSMessageDirection.OUTBOUND
        logger.error(f'SMSMessageDirection: {label} could not be transferred to a valid SMSMessageDirection value!')


SMSAPI_DATETIME_FORMAT = '%a, %d %b %Y %H:%M:%S %z'
SMSAPI_HOST = 'api.telekom.com'
SMSAPI_USER_AGENT = 'dt-sms-api-sdk-python 1.0'


class SMSAPIResponse(object):
    """
    A class representing a response of the DT SMS API for sending an SMS

    Attributes
    ----------
    sid: str
        The SMS message identifier.
    date_created: datetime
        The date representation of when this resource was created.
    date_updated: datetime
        The date on which this resource was last updated.
    status: SMSAPIMessageStatus
        The status of the Message.
    message: Message
        The Message objects holds the API response values for:
        from (Telephone number in E.164 format, Sender ID, or short code.)
        to (Telephone number in E.164 format.)
        body (Text body of the SMS message.)
    uri: str
        The suffix for the HTTP resource, relative to the base domain.
    direction: SMSMessageDirection = SMSMessageDirection.OUTBOUND
        The direction of the request.
    api_version: str
        The version of the SMS API that handled the request.
    num_segments: int
        Amount of text messages needed for delivering the body in the respective encoding.

    Methods
    -------
    from_dict -> SMSAPIResponse
        Returns the number of SMS the Message body has to be split
    """

    sid: str
    date_created: datetime
    date_updated: datetime
    status: SMSAPIMessageStatus
    message: Message
    uri: str
    direction: SMSMessageDirection = SMSMessageDirection.OUTBOUND
    api_version: str
    num_segments: int

    def __init__(self, sid: str, date_created: str, date_updated: str,
                 message_status: str, message_from: str, message_to: str, message_body: str,
                 uri: str, num_segments: int, direction: str,
                 api_version: str = "1.1.5"):
        """
        Parameters
        ----------
        sid: str
            The SMS message identifier.
        date_created: str
            The date representation of when this resource was created
            str in SMSAPI_DATETIME_FORMAT , will be transferred to DateTime
        date_updated: str
            The date on which this resource was last updated
            str in SMSAPI_DATETIME_FORMAT, will be transferred to DateTime
        message_status: str
            The status of the Message as str value, will be transferred to SMSAPIMessageStatus
        message_from: str
            Telephone number in E.164 format, Sender ID, or short code, will become message.sender
        message_to: str
            Telephone number in E.164 format, will be transformed to E164PhoneNumber and become message.recipient
        message_body: str
            Text body of the SMS message, will become message.body
        uri: str
            The suffix for the HTTP resource, relative to the base domain.
        direction: str
            The direction of the request, be transferred to SMSMessageDirection
        api_version: str
            The version of the SMS API that handled the request.
        num_segments: int
            Amount of SMS the SMS API split the body in the respective encoding.

        Returns
        -------
        SMSAPIResponse
            A SMSAPIResponse object holding SMS API responded data

        Raises
        ------
        ValueError
            if message_to can't be transferred to an E164PhoneNumber object inside Message class
        """

        self.sid = sid
        self.date_created = datetime.strptime(date_created, SMSAPI_DATETIME_FORMAT)
        self.date_updated = datetime.strptime(date_updated, SMSAPI_DATETIME_FORMAT)
        self.status = SMSAPIMessageStatus.from_str(message_status)
        self.message = Message(sender=message_from, recipient=E164PhoneNumber(message_to), body=message_body)
        self.uri = uri
        self.num_segments = num_segments
        self.api_version = api_version
        self.direction = SMSMessageDirection.from_str(direction)
        if not self.num_segments == self.message.number_of_segments():
            logger.warning(f'DT SMS API split the message into {self.num_segments} '
                           f'while SDK calculates {self.message.number_of_segments()} splits!')

    @staticmethod
    def from_dict(d: dict):
        """
        This method creates a new SMSAPIResponse object by taking the values for initializing from a dictionary using
        the JSON labels of the API response.

        Parameters
        ----------
        d: dict
            a dictionary of SMSAPIResponse values labeled as used on the API json itself.

        Returns
        -------
        SMSAPIResponse
            A SMSAPIResponse Object containing the values of the API Response
        """
        return SMSAPIResponse(sid=d["sid"],
                              date_created=d["date_created"],
                              date_updated=d["date_updated"],
                              message_status=d["status"],
                              message_from=d["from"],
                              message_to=d["to"],
                              message_body=d["body"],
                              uri=d["uri"],
                              direction=d["direction"],
                              api_version=d["api_version"],
                              num_segments=d["num_segments"]
                              )


class SMSAPIClient(object):
    """
    A class which is used to encapsulate the communication to the DT SMS API.

    Attributes
    ----------
    api_key
        The API Key which is used to authenticate the requests towards the DT SMS API

    Methods
    -------
    send(self, message: Message) -> SMSAPIResponse:
        SMSAPIClient object will send the Message Object using its API Key and gives back an SMSAPIResponse or
        throws an SMSAPIError or a subclass of that.

    """
    api_key: str

    def __init__(self, api_key: str):
        """
        Parameters
        ----------
        api_key
            The accounts api key which authorize any further API request at the DT Developer Portal

        Returns
        -------
        SMSAPIClient
            A SMSAPIClient object which could be used to invoke SMS API endpoints at the DT Developer Portal
        """
        self.api_key = api_key

    def status(self, sid: Union[str, SMSAPIResponse]) -> SMSAPIResponse:
        """
        This method will query the status of a Message sent over the DT SMS API

        Parameters
        ----------
        sid: Union[str, SMSAPIResponse]
            Identifier of the Message, which is part of the SMSAPIResponse object you get back from the send method.
            You could either provide the sid string of that object attribute or just provide the attribute and the method
            will get the sid attribute from it.

        Returns
        -------
        SMSAPIResponse
            The SMSAPIResponse objects holds all data returned by the DT SMS API

        Raises
        ------
        SMSAPIError
            All upcoming (and then not directly supported) Errors raises this base class error.
        SMSAPINotReachableError
            If the DT SMS API could not be reached technically.
        NotAuthorizedError
            API Key could not be authorized
        MessageNotFoundError
            If no status could be found for the given message id (at the used Account)
        InternalSMSAPIError
            The DT SMS API has an internal error
        """
        if isinstance(sid, SMSAPIResponse):
            api_url = f'https://{SMSAPI_HOST}{sid.uri}'
            m_id = sid.sid
        elif isinstance(sid, str):
            api_url = f'https://{SMSAPI_HOST}/service/sms/v1/messages/{sid}'
            m_id = sid
        else:
            logger.error('Without valid sid for the API request, the SDK could not query the status.')
            raise ValueError(f'Given sid {sid} can\'t be used to query status from the DT SMS API')
        headers = {
            'User-Agent': f'{SMSAPI_USER_AGENT}',
            'X-API-Key': self.api_key
        }
        try:
            response = requests.get(api_url, headers=headers)
        except requests.exceptions.ConnectionError:
            logger.error('Could not reach SMS API: %s.', api_url)
            raise SMSAPINotReachableError()
        if response.status_code == 200:
            sent_response = response.json()
            return SMSAPIResponse.from_dict(sent_response)
        elif response.status_code == 401:
            raise NotAuthorizedError(api_key=self.api_key)
        elif response.status_code == 404:
            logger.error("Requesting status of a message results in 404 Error")
            raise MessageNotFoundError(m_id)
        elif response.status_code == 500:
            raise InternalSMSAPIError()
        else:
            raise SMSAPIError(
                    f'While querying the message status, '
                    f'the API raised a new {response.status_code} error with message: "{response.text}"'
            )

    def send(self, message: Message) -> SMSAPIResponse:
        """
        This method will send the Message to the DT SMS API

        Parameters
        ----------
        message: Message
            The Message object which holds all necessary data: from, to and body

        Returns
        -------
        SMSAPIResponse
            The SMSAPIResponse objects holds all data returned by the DT SMS API after a seccussfull call

        Raises
        ------
        SMSAPIError
            All upcoming (and then not directly supported) Errors raises this base class error.
        SMSAPINotReachableError
            If the DT SMS API could not be reached technically.
        NotAuthorizedError
            API Key could not be authorized
        SenderNumberNotVerifiedError
            Sender number could not be verfied on the API Key account
        NotEnoughMoneyOnTheWalletError
            Wallet assigned to API Key does not provide enough money for (split) SMS
        NoRouteToRecipientNumberError
            The DT SMS API has no route to deliver the Message to the recipient number
        InternalSMSAPIError
            The DT SMS API has an internal error
        """
        api_url = f'https://{SMSAPI_HOST}/service/sms/v1/messages'
        headers = {
            'User-Agent': f'{SMSAPI_USER_AGENT}',
            'X-API-Key': self.api_key,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        try:
            response = requests.post(api_url, headers=headers, data=message.data())
        except requests.exceptions.ConnectionError:
            logger.error('Could not reach SMS API: %s.', api_url)
            raise SMSAPINotReachableError()
        if response.status_code == 200:
            sent_response = response.json()
            return SMSAPIResponse.from_dict(sent_response)
        elif response.status_code == 401:
            raise NotAuthorizedError(api_key=self.api_key)
        elif response.status_code == 415:
            logger.error("Sending an SMS results in 415 Error, "
                         "which indicates that SDK has become incompatible with API")
            raise UnsupportedMediaTypeError("Sending an SMS results in 415 Error, "
                                            "which indicates that SDK has become incompatible with API")
        elif response.status_code == 422:
            error_response = response.json()
            if error_response["message"].startswith("Number: ") and \
                    error_response["message"].endswith(" cannot be used because is not verified"):
                raise SenderNumberNotVerifiedError(api_key=self.api_key, sender_number=str(message.sender))
            elif error_response["message"] == "Not enough money on the wallet":
                raise NotEnoughMoneyOnTheWalletError(api_key=self.api_key)
            elif error_response["message"].startswith("No routing available for sms from:"):
                raise NoRouteToRecipientNumberError(recipient_number=str(message.recipient))
            else:
                raise SMSAPIError(
                    f'API raised an 422 error with an unknown message: "{error_response["message"]}"'
                )
        elif response.status_code == 500:
            raise InternalSMSAPIError()
        else:
            raise SMSAPIError(
                    f'While sending a message, '
                    f'the API raised a new {response.status_code} error with message: "{response.text}"'
            )
