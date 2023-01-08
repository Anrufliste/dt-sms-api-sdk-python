from dt_sms_sdk.iso2_mapper import ISO2Mapper

import logging
logger = logging.getLogger(__name__)


class E164PhoneNumber(object):
    """
    Providing methods for calculating the country for a given phone number

    Attributes
    ----------
    number: str
        The phone Number in E.164 format
    iso2: str
        The ISO2 code of the country the number belongs to - base for price calculation.
    """

    number: str
    iso2: str

    @staticmethod
    def basic_number_value_validation(number: str, raising_error: bool = False) -> bool:
        """
        Just validating the data type of the number, no validation towards number plan or other complex rules.

        Parameters
        ----------
        number: str
            the phone number to be validated
        raising_error: bool
            flag to control, if negative validation will raise an exception

        Returns
        -------
        bool
            if simple validation of number was successful

        Raises
        ------
        ValueError
            if parameter raising_error is True and validation of number was unsuccessful
        """
        if not isinstance(number, str):
            logger.debug(f'E164PhoneNumber: {number} is not a string.')
            if raising_error:
                raise ValueError('Number of E164PhoneNumber must be a str.')
            return False
        else:
            return True

    def __init__(self, _number: str, _iso2: str = None):
        """
        Country Calling Code vs. Region Code vs. ISO2
        ---------------------------------------------
        The pricing of the API is based on a specific country refered by ISO2 Code.

        In cases a phone number country calling code is shared by multiple countries - like +1,
        the region code delivered by libraries like phonelib would be "US".
        For pricing this is too unspecific, since Canada and the USA have share the same region,
        but have (e.g. € 0.0058 vs. € 0.0094 Price excl. VAT on December the 31st 2022).

        If you know the country, you can provide its ISO2 Code, if not the class will try to calculate it
        from the phone number and even includes the area code after the country code to differentiate individual
        countries within a shared country calling code.

        Parameters
        ----------
        _number : str
            A phone number in E.164 format - starting with "+" followed by country code
        _iso2 : str, optional
            ISO2 Code of the country

        Returns
        -------
        E164PhoneNumber
            A phone number in E.164 format and the country it belongs.

        Raises
        ------
        ValueError
            if _number does not validate against basic number rules or
            _iso2 does not validate against basic ISO2 rules
        """
        E164PhoneNumber.basic_number_value_validation(number=_number, raising_error=True)
        self.number = _number

        if _iso2:
            if ISO2Mapper.basic_iso2_value_validation(iso2=_iso2, raising_error=True):
                self.iso2 = _iso2.upper()
        else:
            logger.debug('ISO2 of E164PhoneNumber calculated from its number.')
            self.iso2 = ISO2Mapper.number_to_iso2(_number)

    def __eq__(self, other):
        """
        Two E164PhoneNumber objects are equal, if their iso2 codes and number attributes have the same values.
        """
        return isinstance(other, E164PhoneNumber) and \
            self.iso2 == other.iso2 and self.number == other.number
