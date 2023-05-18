import requests

from decimal import Decimal, getcontext, InvalidOperation
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Union

from dt_sms_sdk.dashboard import DASHBOARD_HOST, DASHBOARD_USER_AGENT
from dt_sms_sdk.pricing import Currency
from dt_sms_sdk.phone_number import E164PhoneNumber
from dt_sms_sdk.sms_api import SMSAPIClient

import logging
logger = logging.getLogger(__name__)


class DashboardError(Exception):
    """
    A basic Error class for Errors returned while accessing DT Developer Portal Dashboard
    """
    pass


class DashboardNotReachableError(DashboardError):
    """
    A general Error if the DT Developer Portal Dashboard could not be reached technically.
    """
    pass


class LoginError(DashboardError):
    """
    A specific Error class for a 401 returned by the DT Developer Portal Token endpoint

    Attributes
    ----------
    username: str
        The username which could not be authorized
    password: str
        The password which could not be authorized
    """
    username: str
    password: str

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        super().__init__('The username and/or password has not been accepted by the DT Developer Portal.')


class TokenError(DashboardError):
    """
    A specific Error class for a 401 returned by the DT Developer Portal Dashboard data endpoints

    Attributes
    ----------
    token: str
        The token used to access the endpoint
    valid_until: datetime
        The timepoint when the token get expired
    """
    token: str
    valid_until: datetime

    def __init__(self, token: str, valid_until: datetime):
        self.token = token
        self.valid_until = valid_until
        super().__init__('The token has not been accepted by the DT Developer Portal.')


class Wallet(object):
    """
    Data Set about the DT Developer Portal Dashboard prepaid wallet which is charged for API usage.

    Attributes
    ----------
    balance: Decimal
        The amount of money stored in the wallet with two digit precision.
    currency: Currency
        The currency of the money stored in the wallet - type is defined at the price list data
    """
    balance: Decimal
    currency: Currency

    @staticmethod
    def _decimal(d: Decimal) -> Decimal:
        """
        Helper method to transform an object into Decimal with 2 decimal places after the

        Parameters
        ----------
        d: Decimal
            a decimal object which will cut to 2 decimal places
            (also a float or any other transformable object will be transformed).

        Returns
        -------
        Decimal
            a Decimal with maximum of 2 decimal places

        Raises
        ------
        ValueError
            if parameter d is not transferable into a Decimal
        """
        getcontext().prec = 2
        if isinstance(d, Decimal):
            return d
        elif isinstance(d, float):
            return Decimal(format(d, '.2f'))
        else:
            logger.debug(f'Value {d} is not a Decimal')
            try:
                return Decimal(d)
            except (ValueError, InvalidOperation):
                logger.error(f'Value {d} could not be transferred to Decimal.')
                raise ValueError(f'Value {d} could not be transferred to Decimal.')

    def __init__(self, balance: Decimal, currency: Union[Currency, str] = Currency.EURO):
        """
        Parameters
        ----------
        balance: Decimal
            The amount of money stored in the wallet with two digit precision.
        currency: Union[Currency, str]
            The currency of the money stored in the wallet - might also be given as a str,
            which will be automatically transferred to a Currency object, if it can't an Error is raised

        Raises
        ------
        NotImplementedError
            if currency is a Unicode Symbol for a currency, which is not yet supported by the API
        ValueError
            if currency can't be identified as Currency value at all
        """
        self.balance = Wallet._decimal(balance)
        if isinstance(currency, Currency):
            self.currency = currency
        else:
            self.currency = Currency.from_str(currency)

    def __eq__(self, other) -> bool:
        """
        Two Wallet objects are equal, if all their attributes have the same values.

        Returns
        -------
        bool
             if the Wallet object values is matching the compared object values.
        """
        return isinstance(other, Wallet) and self.balance == other.balance and \
            self.currency == other.currency


class PhoneNumberRegistrationStatus(Enum):
    """
    Enumeration used in RegisteredPhoneNumber Class to specify the status of the registration.

    Values are not available from an API description but are revers engineered.
    """
    VERIFIED = "VERIFIED"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"

    @staticmethod
    def from_str(label: str):
        """
        Returns Enum value for a PhoneNumberRegistrationStatus for a given string or
        throws a ValueError

        Parameters
        ----------
        label: str
            representing a state of a phone number registraion status on the DT Developer Dashboard

        Returns
        -------
        PhoneNumberRegistrationStatus

        Raises
        ------
        ValueError
            if label can't be transferred to a PhoneNumberRegistrationStatus value
        """
        if label:
            temp_label = label.upper()
            if temp_label == "VERIFIED":
                return PhoneNumberRegistrationStatus.VERIFIED
            elif temp_label == "PENDING_VERIFICATION":
                return PhoneNumberRegistrationStatus.PENDING_VERIFICATION
        logger.error(f'PhoneNumberRegistrationStatus: {label} could not be transferred to a valid Status value!')
        raise ValueError("Given value could not be transferred to a valid PhoneNumberRegistrationStatus value!")


class RegisteredPhoneNumber(object):
    """
    Data Set about a PhoneNumber registered at the DT Developer Portal Dashboard to be used within their APIs

    e.g. as the Sender identification for an SMS

    Attributes
    ----------
    id: str
        Identifier of the phone number data set on the DT Developer Portal Dashboard
    number: E164PhoneNumber
        The phone number itself
    status: PhoneNumberRegistrationStatus
        The status of the phone number data set on the DT Developer Portal Dashboard
    serviceId: str
        The id of the Service (URI) of the API the phone number is registered for on the DT Developer Portal Dashboard
    """
    id: str
    number: E164PhoneNumber
    status: PhoneNumberRegistrationStatus
    serviceId: str

    def __init__(self, id: str, number: Union[E164PhoneNumber, str],
                 status: Union[PhoneNumberRegistrationStatus, str], service_id: str):
        """
        Parameters
        ----------
        id: str
            Identifier of the phone number data set on the DT Developer Portal Dashboard
        number : Union[E164PhoneNumber, str]
            The phone number itself, if str is given in E164 notation, it will be stored as E164PhoneNumber
            if it can't an Error is raised
        status : Union[PhoneNumberRegistrationStatus, str]
            The status of the phone number data set on the DT Developer Portal Dashboard, if str is given
            it will be stored as PhoneNumberRegistrationStatus if it can't an Error is raised
        service_id: str
            The id of the Service (URI) of the API the phone number is registered
            for on the DT Developer Portal Dashboard
        Raises
        ------
        ValueError
            if number can't be transferred to an E164PhoneNumber
            if status can't be transferred to a PhoneNumberRegistrationStatus
        """
        self.id = id
        if isinstance(number, E164PhoneNumber):
            self.number = number
        else:
            self.number = E164PhoneNumber(number=number)
        if isinstance(status, PhoneNumberRegistrationStatus):
            self.status = status
        else:
            self.status = PhoneNumberRegistrationStatus.from_str(status)
        self.serviceId = service_id

    @staticmethod
    def from_dict(d: dict):
        """
        This method creates a new RegisteredPhoneNumber object by taking the values for initializing from
        a dictionary using the JSON labels of the Dashboard response.

        Parameters
        ----------
        d: dict
            a dictionary of RegisteredPhoneNumber values labeled as used on the Dashboard json itself.

        Returns
        -------
        RegisteredPhoneNumber
            A RegisteredPhoneNumber Object containing the values of the API Response
        """
        return RegisteredPhoneNumber(id=d["id"],
                                     number=d["number"],
                                     status=d["status"],
                                     service_id=d["serviceId"])


class Account(object):
    """
    Class to encapsulate the DT Developer Portal Dashboard Account and its assigned data objects
    which are used within their APIs

    An object is initiated with the credentials of the account and tries to get an access token for
    accessing the other data objects of that account, stores it and recreates it if needed and timeout has been reached

    Attributes
    ----------
    username: str
        username as part of the credentials authenticate an Account on the DT Developer Portal Dashboard
    password: str
        password as part of the credentials authenticate an Account on the DT Developer Portal Dashboard
    """
    username: str
    password: str

    _token: str = None
    _token_valid_until: datetime = datetime.now(timezone.utc)

    def token(self) -> str:
        """
        Using the credentials of the object, to login in the DT Developer Portal Dashboard and getting an access token.
        This will be stored during its valid time, so that the method will either return the stored on

        Returns
        -------
        str
            token to access special data entities on the DT Developer Portal Dashboard for a specific account

        Raises
        ------
        DashboardNotReachableError
            If the DT Developer Portal Dashboard could not be reached technically.
        LoginError
            If the credentials could not be used to login into DT Developer Portal Dashboard
        """
        if self._token and (datetime.now(timezone.utc) < self._token_valid_until):
            # stored token
            return self._token
        else:
            # get new token
            api_url = f'https://{DASHBOARD_HOST}/api/v1/oauth/token'
            headers = {
                'User-Agent': f'{DASHBOARD_USER_AGENT}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            try:
                response = requests.post(api_url, headers=headers, data={'username': self.username,
                                                                         'password': self.password,
                                                                         'grant_type': 'password'
                                                                         }
                                         )
            except requests.exceptions.ConnectionError:
                logger.error('Could not reach DT Developer Dashboard: %s.', api_url)
                raise DashboardNotReachableError()
            if response.status_code == 200:
                token_response = response.json()
                self._token = token_response["access_token"]
                self._token_valid_until = datetime.now(timezone.utc) + timedelta(0, token_response["expires_in"])
                return self._token
            elif response.status_code == 400:
                raise LoginError(username=self.username, password=self.password)
            elif response.status_code == 401:
                raise LoginError(username=self.username, password=self.password)
            else:
                raise DashboardError(
                    'While querying the token, '
                    f'the endpoint raised a new {response.status_code} error with message: "{response.text}"'
                )

    def wallet(self) -> Wallet:
        """
        Downloading the actual Wallet data of the account on the DT Developer Portal Dashboard

        Returns
        -------
        Wallet
            The actual Wallet data of the account on the DT Developer Portal Dashboard

        Raises
        ------
        DashboardNotReachableError
            If the DT Developer Portal Dashboard could not be reached technically.
        TokenError
            The used Token of the SMSAPIClient was not accepted by the Wallet Endpoint
        DashboardError
            All upcoming (and then not directly supported) Errors raises this base class error.
        """
        api_url = f'https://{DASHBOARD_HOST}/api/v1/wallet'
        headers = {
            'User-Agent': f'{DASHBOARD_USER_AGENT}',
            'Authorization': f'Bearer {self.token()}'
        }
        try:
            response = requests.get(api_url, headers=headers)
        except requests.exceptions.ConnectionError:
            logger.error('Could not reach DT Developer Dashboard: %s.', api_url)
            raise DashboardNotReachableError()
        if response.status_code == 200:
            wallet_response = response.json()
            return Wallet(wallet_response["balance"], Currency.from_str(wallet_response["currency"]))
        elif response.status_code == 401:
            logger.error("Token has not been accepted on the wallet endpoint.")
            raise TokenError(token=self._token, valid_until=self._token_valid_until)
        else:
            raise DashboardError(
                    'While querying the wallet, '
                    f'the endpoint raised a new {response.status_code} error with message: "{response.text}"'
            )

    def phone_numbers(self) -> list[RegisteredPhoneNumber]:
        """
        Downloading the actual list of all RegisteredPhoneNumber data of
        the account on the DT Developer Portal Dashboard

        Returns
        -------
        list[RegisteredPhoneNumber]
            The actual list of RegisteredPhoneNumber data of the account on the DT Developer Portal Dashboard

        Raises
        ------
        DashboardNotReachableError
            If the DT Developer Portal Dashboard could not be reached technically.
        TokenError
            The used Token of the SMSAPIClient was not accepted by the Wallet Endpoint
        DashboardError
            All upcoming (and then not directly supported) Errors raises this base class error.
        """
        api_url = f'https://{DASHBOARD_HOST}/api/v1/numbers'
        headers = {
            'User-Agent': f'{DASHBOARD_USER_AGENT}',
            'Authorization': f'Bearer {self.token()}'
        }
        try:
            response = requests.get(api_url, headers=headers)
        except requests.exceptions.ConnectionError:
            logger.error('Could not reach DT Developer Dashboard: %s.', api_url)
            raise DashboardNotReachableError()
        if response.status_code == 200:
            numbers = response.json()
            l: list[RegisteredPhoneNumber] = list()
            for n in numbers:
                l.append(RegisteredPhoneNumber.from_dict(n))
            return l
        elif response.status_code == 401:
            logger.error("Token has not been accepted on the RegisteredPhoneNumbers endpoint.")
            raise TokenError(token=self._token, valid_until=self._token_valid_until)
        else:
            raise DashboardError(
                    f'While querying the RegisteredPhoneNumbers, '
                    f'the endpoint raised a new {response.status_code} error with message: "{response.text}"'
            )

    def phone_numbers_for_sms_sender(self) -> list[E164PhoneNumber]:
        result: list[E164PhoneNumber] = list()
        for n in self.phone_numbers():
            if n.status == PhoneNumberRegistrationStatus.VERIFIED and n.serviceId.startswith("/service/sms/"):
                result.append(n.number)
        return result

    def api_key(self) -> str:
        """
        This method queries the API Key of the account from the DT Developer Portal Dashboard

        Returns
        -------
        str
            API Key of the account from the DT Developer Portal Dashboard

        Raises
        ------
        DashboardNotReachableError
            If the DT Developer Portal Dashboard could not be reached technically.
        TokenError
            The used Token of the SMSAPIClient was not accepted by the Wallet Endpoint
        DashboardError
            All upcoming (and then not directly supported) Errors raises this base class error.
        """
        api_url = f'https://{DASHBOARD_HOST}/api/v1/api-keys'
        headers = {
            'User-Agent': f'{DASHBOARD_USER_AGENT}',
            'Authorization': f'Bearer {self.token()}'
        }
        try:
            response = requests.get(api_url, headers=headers)
        except requests.exceptions.ConnectionError:
            logger.error('Could not reach DT Developer Dashboard: %s.', api_url)
            raise DashboardNotReachableError()
        if response.status_code == 200:
            api_key_response = response.json()
            return api_key_response["rawApiKey"]
        elif response.status_code == 401:
            logger.error("Token has not been accepted on the API Key endpoint.")
            raise TokenError(token=self._token, valid_until=self._token_valid_until)
        else:
            raise DashboardError(
                    f'While querying the API Key, '
                    f'the endpoint raised a new {response.status_code} error with message: "{response.text}"'
            )

    def sms_api_client(self) -> SMSAPIClient:
        """
        This method queries the API Key of the account from the DT Developer Portal Dashboard and initialize a
        SMSAPIClient object for accessing the DT SMS API

        Returns
        -------
        SMSAPIClient
            SMSAPIClient object directly configured with API Key of the Account

        Raises
        ------
        DashboardNotReachableError
            If the DT Developer Portal Dashboard could not be reached technically.
        TokenError
            The used Token of the SMSAPIClient was not accepted by the Wallet Endpoint
        DashboardError
            All upcoming (and then not directly supported) Errors raises this base class error.
        """
        return SMSAPIClient(api_key=self.api_key())

    def __init__(self, username: str, password: str, auto_login: bool = True):
        """
        Parameters
        ----------
        username: str
            username as part of the credentials authenticate an Account on the DT Developer Portal Dashboard
        password: str
            password as part of the credentials authenticate an Account on the DT Developer Portal Dashboard
        auto_login: bool
            by default this is set True, which means credentials are directly used to get a token from
            DT Developer Portal Dashboard for further request - if set to false, the login will be delayed until
            needed for the subsequent activities.

        Returns
        -------
        Account
            An Account object to access DT Developer Portal Dashboard data of an account.

        Raises
        ------
        DashboardNotReachableError
            If the DT Developer Portal Dashboard could not be reached technically.
        LoginError
            If the credentials could not be used to login into DT Developer Portal Dashboard
        """
        self.username = username
        self.password = password
        if auto_login:
            self.token()
