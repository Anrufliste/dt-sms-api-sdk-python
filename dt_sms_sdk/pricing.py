from typing import Dict, Optional
from enum import Enum
from decimal import Decimal, getcontext, InvalidOperation
import requests

from dt_sms_sdk.dashboard import DASHBOARD_HOST, DASHBOARD_USER_AGENT
from dt_sms_sdk.iso2_mapper import ISO2Mapper
from dt_sms_sdk.message import Message

import logging
logger = logging.getLogger(__name__)


class Currency(Enum):
    """
    Enumeration used in Price Class to specify the type of the price.

    Currently only the Euro is supported.
    """
    EURO = "EUR"

    @staticmethod
    def from_str(label: str):
        """
        Returns Enum value for a currency for a given string or
        throws a NotImplementedError or ValueError

        Parameters
        ----------
        label: str
            representing a currency

        Returns
        -------
        Currency

        Raises
        ------
        NotImplementedError
            if label is a Unicode Symbol for a currency, which is not yet supported by the API
        ValueError
            if label can't be identified as Currency value at all
        """
        if label and label.upper() in ('EUR', 'EURO', '€', '₠'):
            return Currency.EURO
        elif label in ("$", "﹩", "＄", "¢", "￠", "£", "￡", "¤", "¥", "￥", "֏", "؋", "߾", "߿", "৲", "৳", "৻", "૱", "௹",
                       "฿", "៛", "₡", "₢", "₣", "₤", "₥", "₦", "₧", "₨", "₩", "￦", "₪", "₫", "₭", "₮", "₯", "₰", "₱",
                       "₲", "₳", "₴", "₵", "₶", "₷", "₸", "₹", "₺", "₻", "₼", "₽", "₾", "₿", "꠸", "﷼", "𑿝", "𑿞", "𑿟",
                       "𑿠", "𞋿", "𞲰"):
            logger.error(f'Currency: {label} could not be transferred to a valid Currency value, yet!')
            raise NotImplementedError("Given currency symbol could not be transferred to a valid Currency value, yet!")
        else:
            logger.error(f'Currency: {label} could not be transferred to a valid Currency value!')
            raise ValueError("Given value could not be transferred to a valid Currency value!")


class Price(object):
    """
    A class representing a Price for sending an SMS message to a specific country

    Attributes
    ----------
    country: str
        The country name as used on https://developer.telekom.com/api/v1/prices
    net_price: Decimal
        Price before applying tax (vat)
    gross_price: Decimal
        Price after applying tax (vat)
    vat: Decimal
        Amount of tax which applies on netPrice to get grossPrice
    currency: Currency
        The Currency of the netPrice and grossPrice.
    """
    country: str
    net_price: Decimal
    gross_price: Decimal
    vat: Decimal = 0.19
    currency: Currency = Currency.EURO

    @staticmethod
    def _decimal(d: Decimal) -> Decimal:
        """
        Helper method to transform an object into Decimal with 4 decimal places after the

        Parameters
        ----------
        d: Decimal
            a decimal object which will cut to 4 decimal places
            (also a float or any other transformable object will be transformed).

        Returns
        -------
        Decimal
            a Decimal with maximum of 4 decimal places

        Raises
        ------
        ValueError
            if parameter d is not transferable into a Decimal
        """
        getcontext().prec = 4
        if isinstance(d, Decimal):
            return d
        elif isinstance(d, float):
            return Decimal(format(d, '.4f'))
        else:
            logger.debug(f'Value {d} is not a Decimal')
            try:
                return Decimal(d)
            except (ValueError, InvalidOperation):
                logger.error(f'Value {d} could not be transferred to Decimal.')
                raise ValueError(f'Value {d} could not be transferred to Decimal.')

    def __init__(self, country: str, net_price: Decimal, gross_price: Decimal, vat: Decimal = 0.19,
                 currency: Currency = Currency.EURO):
        """
        Parameters
        ----------
        country : str
            The country name as used in the DT price list
        net_price: Decimal
            Price before applying tax (vat)
        gross_price: Decimal
            Price after applying tax (vat)
        vat: Decimal
            Amount of tax which applies on netPrice to get grossPrice
        currency: Currency
            The Currency of the netPrice and grossPrice.

        Returns
        -------
        Price
            an object containing all provided price data

        Raises
        ------
        ValueError
            if net_price, gross_price or vat are not Decimal (or at least not transferable to a Decimal)
            if currency is not a Currency object (or at least not transferable to a Currency)
        """
        self.country = country
        try:
            self.net_price = self._decimal(net_price)
            self.gross_price = self._decimal(gross_price)
            self.vat = self._decimal(vat)
        except ValueError:
            logger.error("Price could only be created if net_price, gross_price AND vat are Decimal.")
            raise ValueError("Price could only be created if net_price, gross_price AND vat are Decimal.")

        if isinstance(currency, Currency):
            self.currency = currency
        elif isinstance(currency, str):
            try:
                self.currency = Currency.from_str(currency)
            except (ValueError, NotImplementedError):
                logger.error(f'Value {currency} is not convertible to Currency.')
                raise ValueError("Given currency parameter is not usable on Price.")
        else:
            logger.error(f'Value {currency} is not a Currency.')
            raise ValueError("Given currency parameter is not usable on Price.")

    def __eq__(self, other) -> bool:
        """
        Two Price objects are equal, if all their attributes have the same values.

        Returns
        -------
        bool
             if the Price object values is matching the compared object values.
        """
        return isinstance(other, Price) and self.country == other.country and \
            self.net_price == other.net_price and \
            self.gross_price == other.gross_price and \
            self.vat == other.vat and \
            self.currency == other.currency


class Pricing(object):
    """
     A class providing methods to transform a price list data as provided from DT into a data structure, which is a
     dictionary using ISO2 code of the country as key and gives a Price object for that country.

     Furthermore, it also provides an offline default pricelist and a method to download the current online one.
    """

    @staticmethod
    def _raw_is_list(raw) -> bool:
        """
        Returns if raw is a list and if not logs that this could not be Pricing Data

        Parameters
        ----------
        raw:
            data to be checked if it could be Pricing Data as provided by DT

        Returns
        -------
        bool
            is true if raw is at least a list
        """
        if isinstance(raw, list):
            return True
        else:
            logger.warning('Pricing Data is not an expected list JSON object.')
            return False

    @staticmethod
    def _raw_item_iso2_code(item: dict) -> Optional[str]:
        """
        Returns an ISO2 Code for the country used in the raw Pricing Data item.

        Parameters
        ----------
        item: dict
            an item of the raw Pricing Data as provided by DT representing a single price point dictionary

        Returns
        -------
        str, optional
            ISO2 Code of the country referred in item or None if no match could be found or an error happens
        """
        try:
            country_name = item["country"]
        except TypeError:
            logger.debug('Item %s of Pricing is not a dictionary.', item)
        except KeyError:
            logger.debug('Item %s of Pricing data does not have country key.', item)
        else:
            try:
                return ISO2Mapper.country_name_to_ISO2_mapping[country_name]
            except KeyError:
                logger.warning('No ISO2 mapping for %s in Pricing data found.', country_name)

    @staticmethod
    def _raw_item_to_price(item: dict) -> Optional[Price]:
        """
        Converts a single item of Pricing Data from a dictionary into a Price object.

        Parameters
        ----------
        item: dict
            Single Price Data as provided by DT

        Returns
        -------
        Price, optional
            The Price object contains all relevant price data for sending an SMS to a specific country.
            If not all data is available or an error happens, None is returned.
        """
        try:
            return Price(country=item["country"], net_price=item["netPrice"], gross_price=item["grossPrice"],
                         vat=item["vat"], currency=Currency.from_str(item["currency"]))
        except TypeError:
            logger.debug('Item %s of Pricing is not a dictionary.', item)
        except KeyError:
            if "country" in item.keys():
                logger.debug('Incomplete pricing data provided for country: %s.', item["country"])
            else:
                logger.debug('Incomplete pricing data provided for item: %s.', item)

    @staticmethod
    def prices_by_iso2(raw: list) -> Dict[str, Price]:
        """
        Converts a list of Pricing Data into a Dictionary with ISO2 code of the countries as key
        and a Price object as the value.

        Parameters
        ----------
        raw: list
            Pricing Data as provided by DT

        Returns
        -------
        str, optional
            ISO2 Code of the country referred in item or None if no match could be found or an Error happens

        """
        result: Dict[str, Price] = {}

        if Pricing._raw_is_list(raw):
            for p in raw:
                iso2 = Pricing._raw_item_iso2_code(p)
                if iso2:
                    price = Pricing._raw_item_to_price(p)
                    if price:
                        result[iso2] = price
            if not len(raw) == len(result):
                logger.warning("Not all entries of Pricing data could be correctly loaded!")
        return result

    @staticmethod
    def default() -> list:
        """
        Offline Pricing Data as found on https://developer.telekom.com/api/v1/prices

        Returns
        -------
        list
            Offline Pricing Data from 24.12.2012
        """
        return [
            {"country": "Belarus", "netPrice": 0.1458, "grossPrice": 0.1736, "vat": 0.19, "currency": "EUR"},
            {"country": "Timor-Leste", "netPrice": 0.0523, "grossPrice": 0.0623, "vat": 0.19, "currency": "EUR"},
            {"country": "Moldova", "netPrice": 0.0502, "grossPrice": 0.0598, "vat": 0.19, "currency": "EUR"},
            {"country": "Philippines", "netPrice": 0.1221, "grossPrice": 0.1453, "vat": 0.19, "currency": "EUR"},
            {"country": "Poland", "netPrice": 0.0343, "grossPrice": 0.0409, "vat": 0.19, "currency": "EUR"},
            {"country": "Germany", "netPrice": 0.0751, "grossPrice": 0.0894, "vat": 0.19, "currency": "EUR"},
            {"country": "Thailand", "netPrice": 0.0238, "grossPrice": 0.0284, "vat": 0.19, "currency": "EUR"},
            {"country": "Gibraltar", "netPrice": 0.0262, "grossPrice": 0.0312, "vat": 0.19, "currency": "EUR"},
            {"country": "Portugal", "netPrice": 0.0426, "grossPrice": 0.0507, "vat": 0.19, "currency": "EUR"},
            {"country": "Singapore", "netPrice": 0.0324, "grossPrice": 0.0386, "vat": 0.19, "currency": "EUR"},
            {"country": "Luxembourg", "netPrice": 0.0645, "grossPrice": 0.0768, "vat": 0.19, "currency": "EUR"},
            {"country": "Ireland", "netPrice": 0.0585, "grossPrice": 0.0697, "vat": 0.19, "currency": "EUR"},
            {"country": "Brunei Darussalam", "netPrice": 0.0471, "grossPrice": 0.0561, "vat": 0.19, "currency": "EUR"},
            {"country": "Iceland", "netPrice": 0.0532, "grossPrice": 0.0634, "vat": 0.19, "currency": "EUR"},
            {"country": "New Zealand", "netPrice": 0.0821, "grossPrice": 0.0977, "vat": 0.19, "currency": "EUR"},
            {"country": "Albania", "netPrice": 0.073, "grossPrice": 0.0869, "vat": 0.19, "currency": "EUR"},
            {"country": "Malta", "netPrice": 0.0473, "grossPrice": 0.0563, "vat": 0.19, "currency": "EUR"},
            {"country": "Cyprus", "netPrice": 0.0364, "grossPrice": 0.0434, "vat": 0.19, "currency": "EUR"},
            {"country": "Papua New Guinea", "netPrice": 0.1098, "grossPrice": 0.1307, "vat": 0.19, "currency": "EUR"},
            {"country": "Georgia", "netPrice": 0.1041, "grossPrice": 0.1239, "vat": 0.19, "currency": "EUR"},
            {"country": "Armenia", "netPrice": 0.0997, "grossPrice": 0.1187, "vat": 0.19, "currency": "EUR"},
            {"country": "Bulgaria", "netPrice": 0.0876, "grossPrice": 0.1043, "vat": 0.19, "currency": "EUR"},
            {"country": "Turkey", "netPrice": 0.0238, "grossPrice": 0.0284, "vat": 0.19, "currency": "EUR"},
            {"country": "American Samoa", "netPrice": 0.0648, "grossPrice": 0.0772, "vat": 0.19, "currency": "EUR"},
            {"country": "New Caledonia", "netPrice": 0.125, "grossPrice": 0.1488, "vat": 0.19, "currency": "EUR"},
            {"country": "Slovenia", "netPrice": 0.0752, "grossPrice": 0.0895, "vat": 0.19, "currency": "EUR"},
            {"country": "Macedonia", "netPrice": 0.0566, "grossPrice": 0.0674, "vat": 0.19, "currency": "EUR"},
            {"country": "Liechtenstein", "netPrice": 0.0299, "grossPrice": 0.0356, "vat": 0.19, "currency": "EUR"},
            {"country": "Montenegro", "netPrice": 0.0671, "grossPrice": 0.0799, "vat": 0.19, "currency": "EUR"},
            {"country": "Canada", "netPrice": 0.0058, "grossPrice": 0.007, "vat": 0.19, "currency": "EUR"},
            {"country": "United States", "netPrice": 0.0094, "grossPrice": 0.0112, "vat": 0.19, "currency": "EUR"},
            {"country": "Puerto Rico", "netPrice": 0.0575, "grossPrice": 0.0685, "vat": 0.19, "currency": "EUR"},
            {"country": "Mexico", "netPrice": 0.041, "grossPrice": 0.0488, "vat": 0.19, "currency": "EUR"},
            {"country": "Jamaica", "netPrice": 0.0972, "grossPrice": 0.1157, "vat": 0.19, "currency": "EUR"},
            {"country": "French Guiana", "netPrice": 0.132, "grossPrice": 0.1571, "vat": 0.19, "currency": "EUR"},
            {"country": "Egypt", "netPrice": 0.1399, "grossPrice": 0.1665, "vat": 0.19, "currency": "EUR"},
            {"country": "Algeria", "netPrice": 0.1325, "grossPrice": 0.1577, "vat": 0.19, "currency": "EUR"},
            {"country": "Morocco", "netPrice": 0.0748, "grossPrice": 0.0891, "vat": 0.19, "currency": "EUR"},
            {"country": "Tunisia", "netPrice": 0.1412, "grossPrice": 0.1681, "vat": 0.19, "currency": "EUR"},
            {"country": "Libya", "netPrice": 0.1307, "grossPrice": 0.1556, "vat": 0.19, "currency": "EUR"},
            {"country": "Gambia", "netPrice": 0.0889, "grossPrice": 0.1058, "vat": 0.19, "currency": "EUR"},
            {"country": "Senegal", "netPrice": 0.1437, "grossPrice": 0.1711, "vat": 0.19, "currency": "EUR"},
            {"country": "Mauritania", "netPrice": 0.092, "grossPrice": 0.1095, "vat": 0.19, "currency": "EUR"},
            {"country": "Mali", "netPrice": 0.09, "grossPrice": 0.1071, "vat": 0.19, "currency": "EUR"},
            {"country": "Guinea", "netPrice": 0.1234, "grossPrice": 0.1469, "vat": 0.19, "currency": "EUR"},
            {"country": "Saint Kitts and Nevis", "netPrice": 0.1171, "grossPrice": 0.1394, "vat": 0.19,
             "currency": "EUR"},
            {"country": "Ivory Coast", "netPrice": 0.8256, "grossPrice": 0.9825, "vat": 0.19, "currency": "EUR"},
            {"country": "Burkina Faso", "netPrice": 0.0941, "grossPrice": 0.112, "vat": 0.19, "currency": "EUR"},
            {"country": "Niger", "netPrice": 0.1004, "grossPrice": 0.1195, "vat": 0.19, "currency": "EUR"},
            {"country": "Togo", "netPrice": 0.0654, "grossPrice": 0.0779, "vat": 0.19, "currency": "EUR"},
            {"country": "Benin", "netPrice": 0.08, "grossPrice": 0.0952, "vat": 0.19, "currency": "EUR"},
            {"country": "Mauritius", "netPrice": 0.0864, "grossPrice": 0.1029, "vat": 0.19, "currency": "EUR"},
            {"country": "Liberia", "netPrice": 0.0648, "grossPrice": 0.0772, "vat": 0.19, "currency": "EUR"},
            {"country": "Sierra Leone", "netPrice": 0.092, "grossPrice": 0.1095, "vat": 0.19, "currency": "EUR"},
            {"country": "Ghana", "netPrice": 0.1221, "grossPrice": 0.1453, "vat": 0.19, "currency": "EUR"},
            {"country": "Nigeria", "netPrice": 0.1438, "grossPrice": 0.1712, "vat": 0.19, "currency": "EUR"},
            {"country": "Chad", "netPrice": 0.091, "grossPrice": 0.1083, "vat": 0.19, "currency": "EUR"},
            {"country": "Dominica", "netPrice": 0.0972, "grossPrice": 0.1157, "vat": 0.19, "currency": "EUR"},
            {"country": "Central African Republic", "netPrice": 0.021, "grossPrice": 0.025, "vat": 0.19,
             "currency": "EUR"},
            {"country": "Cameroon", "netPrice": 0.0972, "grossPrice": 0.1157, "vat": 0.19, "currency": "EUR"},
            {"country": "Cuba", "netPrice": 0.0661, "grossPrice": 0.0787, "vat": 0.19, "currency": "EUR"},
            {"country": "Cape Verde", "netPrice": 0.0843, "grossPrice": 0.1004, "vat": 0.19, "currency": "EUR"},
            {"country": "Sao Tome and Principe", "netPrice": 0.0739, "grossPrice": 0.088, "vat": 0.19,
             "currency": "EUR"},
            {"country": "Dominican Republic", "netPrice": 0.0695, "grossPrice": 0.0828, "vat": 0.19, "currency": "EUR"},
            {"country": "Equatorial Guinea", "netPrice": 0.0727, "grossPrice": 0.0866, "vat": 0.19, "currency": "EUR"},
            {"country": "Haiti", "netPrice": 0.0972, "grossPrice": 0.1157, "vat": 0.19, "currency": "EUR"},
            {"country": "Gabon", "netPrice": 0.7002, "grossPrice": 0.8333, "vat": 0.19, "currency": "EUR"},
            {"country": "Republic of Congo", "netPrice": 0.0904, "grossPrice": 0.1076, "vat": 0.19, "currency": "EUR"},
            {"country": "Democratic Republic of Congo", "netPrice": 0.092, "grossPrice": 0.1095, "vat": 0.19,
             "currency": "EUR"},
            {"country": "Angola", "netPrice": 0.0503, "grossPrice": 0.0599, "vat": 0.19, "currency": "EUR"},
            {"country": "Guinea-Bissau", "netPrice": 0.0972, "grossPrice": 0.1157, "vat": 0.19, "currency": "EUR"},
            {"country": "Seychelles", "netPrice": 0.0575, "grossPrice": 0.0685, "vat": 0.19, "currency": "EUR"},
            {"country": "Rwanda", "netPrice": 0.0904, "grossPrice": 0.1076, "vat": 0.19, "currency": "EUR"},
            {"country": "Ethiopia", "netPrice": 0.1246, "grossPrice": 0.1483, "vat": 0.19, "currency": "EUR"},
            {"country": "Somalia", "netPrice": 0.1221, "grossPrice": 0.1453, "vat": 0.19, "currency": "EUR"},
            {"country": "Djibouti", "netPrice": 0.0846, "grossPrice": 0.1007, "vat": 0.19, "currency": "EUR"},
            {"country": "Kenya", "netPrice": 0.1359, "grossPrice": 0.1618, "vat": 0.19, "currency": "EUR"},
            {"country": "Tanzania", "netPrice": 0.0904, "grossPrice": 0.1076, "vat": 0.19, "currency": "EUR"},
            {"country": "Uganda", "netPrice": 0.1145, "grossPrice": 0.1363, "vat": 0.19, "currency": "EUR"},
            {"country": "Burundi", "netPrice": 0.1401, "grossPrice": 0.1668, "vat": 0.19, "currency": "EUR"},
            {"country": "Mozambique", "netPrice": 0.045, "grossPrice": 0.0536, "vat": 0.19, "currency": "EUR"},
            {"country": "Zambia", "netPrice": 0.1221, "grossPrice": 0.1453, "vat": 0.19, "currency": "EUR"},
            {"country": "Madagascar", "netPrice": 0.1798, "grossPrice": 0.214, "vat": 0.19, "currency": "EUR"},
            {"country": "Zimbabwe", "netPrice": 0.1202, "grossPrice": 0.1431, "vat": 0.19, "currency": "EUR"},
            {"country": "Namibia", "netPrice": 0.0575, "grossPrice": 0.0685, "vat": 0.19, "currency": "EUR"},
            {"country": "Malawi", "netPrice": 0.0904, "grossPrice": 0.1076, "vat": 0.19, "currency": "EUR"},
            {"country": "Botswana", "netPrice": 0.0797, "grossPrice": 0.0949, "vat": 0.19, "currency": "EUR"},
            {"country": "South Africa", "netPrice": 0.0231, "grossPrice": 0.0275, "vat": 0.19, "currency": "EUR"},
            {"country": "Azerbaijan", "netPrice": 0.1944, "grossPrice": 0.2314, "vat": 0.19, "currency": "EUR"},
            {"country": "Eritrea", "netPrice": 0.09, "grossPrice": 0.1071, "vat": 0.19, "currency": "EUR"},
            {"country": "Kazakhstan", "netPrice": 0.132, "grossPrice": 0.1571, "vat": 0.19, "currency": "EUR"},
            {"country": "South Sudan", "netPrice": 0.068, "grossPrice": 0.081, "vat": 0.19, "currency": "EUR"},
            {"country": "India", "netPrice": 0.0468, "grossPrice": 0.0557, "vat": 0.19, "currency": "EUR"},
            {"country": "Pakistan", "netPrice": 0.1396, "grossPrice": 0.1662, "vat": 0.19, "currency": "EUR"},
            {"country": "Afghanistan", "netPrice": 0.1495, "grossPrice": 0.178, "vat": 0.19, "currency": "EUR"},
            {"country": "Sri Lanka", "netPrice": 0.1386, "grossPrice": 0.165, "vat": 0.19, "currency": "EUR"},
            {"country": "Myanmar", "netPrice": 0.1516, "grossPrice": 0.1805, "vat": 0.19, "currency": "EUR"},
            {"country": "Lebanon", "netPrice": 0.0889, "grossPrice": 0.1058, "vat": 0.19, "currency": "EUR"},
            {"country": "Jordan", "netPrice": 0.1196, "grossPrice": 0.1424, "vat": 0.19, "currency": "EUR"},
            {"country": "Syrian Arab Republic", "netPrice": 0.1463, "grossPrice": 0.1741, "vat": 0.19,
             "currency": "EUR"},
            {"country": "Iraq", "netPrice": 0.1118, "grossPrice": 0.1331, "vat": 0.19, "currency": "EUR"},
            {"country": "Kuwait", "netPrice": 0.1161, "grossPrice": 0.1382, "vat": 0.19, "currency": "EUR"},
            {"country": "Saudi Arabia", "netPrice": 0.0648, "grossPrice": 0.0772, "vat": 0.19, "currency": "EUR"},
            {"country": "Yemen", "netPrice": 0.1546, "grossPrice": 0.184, "vat": 0.19, "currency": "EUR"},
            {"country": "Oman", "netPrice": 0.0742, "grossPrice": 0.0883, "vat": 0.19, "currency": "EUR"},
            {"country": "United Arab Emirates", "netPrice": 0.0654, "grossPrice": 0.0779, "vat": 0.19,
             "currency": "EUR"},
            {"country": "State of Palestine", "netPrice": 0.2299, "grossPrice": 0.2736, "vat": 0.19, "currency": "EUR"},
            {"country": "Bahrain", "netPrice": 0.0236, "grossPrice": 0.0281, "vat": 0.19, "currency": "EUR"},
            {"country": "Qatar", "netPrice": 0.0504, "grossPrice": 0.06, "vat": 0.19, "currency": "EUR"},
            {"country": "Mongolia", "netPrice": 0.1045, "grossPrice": 0.1244, "vat": 0.19, "currency": "EUR"},
            {"country": "Nepal", "netPrice": 0.1309, "grossPrice": 0.1558, "vat": 0.19, "currency": "EUR"},
            {"country": "Iran", "netPrice": 0.1658, "grossPrice": 0.1974, "vat": 0.19, "currency": "EUR"},
            {"country": "Uzbekistan", "netPrice": 0.1798, "grossPrice": 0.214, "vat": 0.19, "currency": "EUR"},
            {"country": "Tajikistan", "netPrice": 0.166, "grossPrice": 0.1976, "vat": 0.19, "currency": "EUR"},
            {"country": "Kyrgyzstan", "netPrice": 0.138, "grossPrice": 0.1643, "vat": 0.19, "currency": "EUR"},
            {"country": "Turkmenistan", "netPrice": 0.1066, "grossPrice": 0.1269, "vat": 0.19, "currency": "EUR"},
            {"country": "Japan", "netPrice": 0.07, "grossPrice": 0.0833, "vat": 0.19, "currency": "EUR"},
            {"country": "Belize", "netPrice": 0.1221, "grossPrice": 0.1453, "vat": 0.19, "currency": "EUR"},
            {"country": "Guatemala", "netPrice": 0.1045, "grossPrice": 0.1244, "vat": 0.19, "currency": "EUR"},
            {"country": "El Salvador", "netPrice": 0.0978, "grossPrice": 0.1164, "vat": 0.19, "currency": "EUR"},
            {"country": "Republic of Korea", "netPrice": 0.0349, "grossPrice": 0.0416, "vat": 0.19, "currency": "EUR"},
            {"country": "Vietnam", "netPrice": 0.0882, "grossPrice": 0.105, "vat": 0.19, "currency": "EUR"},
            {"country": "Honduras", "netPrice": 0.0618, "grossPrice": 0.0736, "vat": 0.19, "currency": "EUR"},
            {"country": "Hong Kong", "netPrice": 0.0448, "grossPrice": 0.0534, "vat": 0.19, "currency": "EUR"},
            {"country": "Nicaragua", "netPrice": 0.068, "grossPrice": 0.081, "vat": 0.19, "currency": "EUR"},
            {"country": "Macao", "netPrice": 0.0261, "grossPrice": 0.0311, "vat": 0.19, "currency": "EUR"},
            {"country": "Cambodia", "netPrice": 0.1045, "grossPrice": 0.1244, "vat": 0.19, "currency": "EUR"},
            {"country": "Costa Rica", "netPrice": 0.035, "grossPrice": 0.0417, "vat": 0.19, "currency": "EUR"},
            {"country": "Panama", "netPrice": 0.0972, "grossPrice": 0.1157, "vat": 0.19, "currency": "EUR"},
            {"country": "Greece", "netPrice": 0.0493, "grossPrice": 0.0587, "vat": 0.19, "currency": "EUR"},
            {"country": "China", "netPrice": 0.0294, "grossPrice": 0.035, "vat": 0.19, "currency": "EUR"},
            {"country": "Peru", "netPrice": 0.0753, "grossPrice": 0.0897, "vat": 0.19, "currency": "EUR"},
            {"country": "Netherlands", "netPrice": 0.0795, "grossPrice": 0.0947, "vat": 0.19, "currency": "EUR"},
            {"country": "Belgium", "netPrice": 0.0822, "grossPrice": 0.0979, "vat": 0.19, "currency": "EUR"},
            {"country": "France", "netPrice": 0.0628, "grossPrice": 0.0748, "vat": 0.19, "currency": "EUR"},
            {"country": "Argentina", "netPrice": 0.0816, "grossPrice": 0.0972, "vat": 0.19, "currency": "EUR"},
            {"country": "Taiwan", "netPrice": 0.058, "grossPrice": 0.0691, "vat": 0.19, "currency": "EUR"},
            {"country": "Brazil", "netPrice": 0.0544, "grossPrice": 0.0648, "vat": 0.19, "currency": "EUR"},
            {"country": "Bangladesh", "netPrice": 0.1787, "grossPrice": 0.2127, "vat": 0.19, "currency": "EUR"},
            {"country": "Spain", "netPrice": 0.0689, "grossPrice": 0.082, "vat": 0.19, "currency": "EUR"},
            {"country": "Hungary", "netPrice": 0.0687, "grossPrice": 0.0818, "vat": 0.19, "currency": "EUR"},
            {"country": "Bosnia and Herzegovina", "netPrice": 0.0669, "grossPrice": 0.0797, "vat": 0.19,
             "currency": "EUR"},
            {"country": "Chile", "netPrice": 0.0784, "grossPrice": 0.0933, "vat": 0.19, "currency": "EUR"},
            {"country": "Croatia", "netPrice": 0.0598, "grossPrice": 0.0712, "vat": 0.19, "currency": "EUR"},
            {"country": "Serbia", "netPrice": 0.0858, "grossPrice": 0.1022, "vat": 0.19, "currency": "EUR"},
            {"country": "Colombia", "netPrice": 0.0394, "grossPrice": 0.0469, "vat": 0.19, "currency": "EUR"},
            {"country": "Italy", "netPrice": 0.0648, "grossPrice": 0.0772, "vat": 0.19, "currency": "EUR"},
            {"country": "Venezuela", "netPrice": 0.056, "grossPrice": 0.0667, "vat": 0.19, "currency": "EUR"},
            {"country": "Bolivia", "netPrice": 0.0836, "grossPrice": 0.0995, "vat": 0.19, "currency": "EUR"},
            {"country": "Guyana", "netPrice": 0.0972, "grossPrice": 0.1157, "vat": 0.19, "currency": "EUR"},
            {"country": "Romania", "netPrice": 0.0604, "grossPrice": 0.0719, "vat": 0.19, "currency": "EUR"},
            {"country": "Ecuador", "netPrice": 0.1006, "grossPrice": 0.1198, "vat": 0.19, "currency": "EUR"},
            {"country": "Switzerland", "netPrice": 0.058, "grossPrice": 0.0691, "vat": 0.19, "currency": "EUR"},
            {"country": "Czech Republic", "netPrice": 0.052, "grossPrice": 0.0619, "vat": 0.19, "currency": "EUR"},
            {"country": "Slovakia", "netPrice": 0.0598, "grossPrice": 0.0712, "vat": 0.19, "currency": "EUR"},
            {"country": "Austria", "netPrice": 0.0766, "grossPrice": 0.0912, "vat": 0.19, "currency": "EUR"},
            {"country": "Paraguay", "netPrice": 0.0166, "grossPrice": 0.0198, "vat": 0.19, "currency": "EUR"},
            {"country": "United Kingdom", "netPrice": 0.0329, "grossPrice": 0.0392, "vat": 0.19, "currency": "EUR"},
            {"country": "Suriname", "netPrice": 0.0972, "grossPrice": 0.1157, "vat": 0.19, "currency": "EUR"},
            {"country": "Uruguay", "netPrice": 0.0628, "grossPrice": 0.0748, "vat": 0.19, "currency": "EUR"},
            {"country": "Denmark", "netPrice": 0.0472, "grossPrice": 0.0562, "vat": 0.19, "currency": "EUR"},
            {"country": "Sweden", "netPrice": 0.0523, "grossPrice": 0.0623, "vat": 0.19, "currency": "EUR"},
            {"country": "Norway", "netPrice": 0.058, "grossPrice": 0.0691, "vat": 0.19, "currency": "EUR"},
            {"country": "Finland", "netPrice": 0.07, "grossPrice": 0.0833, "vat": 0.19, "currency": "EUR"},
            {"country": "Malaysia", "netPrice": 0.0748, "grossPrice": 0.0891, "vat": 0.19, "currency": "EUR"},
            {"country": "Lithuania", "netPrice": 0.0339, "grossPrice": 0.0404, "vat": 0.19, "currency": "EUR"},
            {"country": "Latvia", "netPrice": 0.059, "grossPrice": 0.0703, "vat": 0.19, "currency": "EUR"},
            {"country": "Estonia", "netPrice": 0.0747, "grossPrice": 0.0889, "vat": 0.19, "currency": "EUR"},
            {"country": "Australia", "netPrice": 0.0379, "grossPrice": 0.0452, "vat": 0.19, "currency": "EUR"},
            {"country": "Russian Federation", "netPrice": 0.3762, "grossPrice": 0.4477, "vat": 0.19, "currency": "EUR"},
            {"country": "Indonesia", "netPrice": 0.1929, "grossPrice": 0.2296, "vat": 0.19, "currency": "EUR"},
            {"country": "Ukraine", "netPrice": 0.1169, "grossPrice": 0.1392, "vat": 0.19, "currency": "EUR"}
        ]

    @staticmethod
    def download() -> Optional[list]:
        """
        Pricing Data which will be loaded from https://developer.telekom.com/api/v1/prices

        Returns
        -------
        list, optional
            Online Pricing Data or None if an Error happens
        """
        api_url = f'https://{DASHBOARD_HOST}/api/v1/prices'
        headers = {
            'User-Agent': f'{DASHBOARD_USER_AGENT}'
        }
        try:
            response = requests.get(api_url, headers=headers)
        except requests.exceptions.ConnectionError:
            logger.error('Could not reach Pricing Data at %s.', api_url)
            return None
        else:
            try:
                result = response.json()
                if not Pricing._raw_is_list(result):
                    logger.error('Pricing Data from %s is not an expected list JSON object.', api_url)
                    result = None
            except requests.exceptions.JSONDecodeError:
                logger.error('Could not parse Pricing Data from %s into a JSON object.', api_url)
                return None
        return result

    price_data: Dict[str, Price]

    def __init__(self, price_list: list = None):
        """
        Parameters
        ----------
        price_list: list
            a list of pricing information as used from DT on https://developer.telekom.com/api/v1/prices which will
            be loaded into objects price_data dictionary keyed by the country ISO2 code.

        Returns
        -------
        Pricing
            A Pricing object which holds the given price list internally as Dict[str, Price], so the object has quick
            access to Price objects by ISO2 codes. If no price data parameter has been provided, the object is loading
            the class default price list.
        """

        if price_list:
            self.price_data = Pricing.prices_by_iso2(price_list)
        else:
            self.price_data = Pricing.prices_by_iso2(Pricing.default())

        for v in ISO2Mapper.country_name_to_ISO2_mapping.values():
            if v not in self.price_data.keys():
                logger.warning(
                    f'Loaded Pricing Data does not include Country, which is part of country name mapping: {v}'
                )

    def price_by_iso2(self, iso2: str) -> Optional[Price]:
        """
        Getting a Price object by the country's ISO2 code from the price_data

        Parameters
        ----------
        iso2: str
            ISO2 code of the country the Price is to be looked up

        Returns
        -------
        Price, optional
            if ISO2 code could be found in price_data, corresponding Price object is returned
            otherwise None is returned.
        """
        if isinstance(self.price_data, dict):
            if iso2 in self.price_data.keys():
                return self.price_data[iso2]
            else:
                logger.warning(f'No Price Data for ISO2 Code: {iso2}')
        else:
            logger.error('Price Data stored in Pricing is not a dictionary.')

    def net_price_by_iso2(self, iso2: str) -> Decimal:
        """
        Getting the net price by the country's ISO2 code from the corresponding Price object in the price_data

        Parameters
        ----------
        iso2: str
            ISO2 code of the country the net price is to be looked up

        Returns
        -------
        Decimal
            if ISO2 code could be found in price_data, net price of corresponding Price object is returned
            otherwise Decimal("NaN") -> 'not a number' is returned.
        """
        getcontext().prec = 4
        p = self.price_by_iso2(iso2)
        if p:
            return p.net_price
        else:
            return Decimal("NaN")

    def gross_price_by_iso2(self, iso2: str) -> Decimal:
        """
        Getting the gross price by the country's ISO2 code from the corresponding Price object in the price_data

        Parameters
        ----------
        iso2: str
            ISO2 code of the country the gross price is to be looked up

        Returns
        -------
        Decimal
            if ISO2 code could be found in price_data, gross price of corresponding Price object is returned
            otherwise Decimal("NaN") -> 'not a number' is returned.
        """
        getcontext().prec = 4
        p = self.price_by_iso2(iso2)
        if p:
            return p.gross_price
        else:
            return Decimal("NaN")

    def message_net_price(self, message: Message) -> Decimal:
        """
        Getting the net price for a message, by looking up the net price for the message receiver country
        and multiply this with the number of needed SMS slits, to have overall net price for sending this message.

        Parameters
        ----------
        message: Message
            Message which could be sent over the API

        Returns
        -------
        Decimal
            if price for the message receiver could be found in price_data, overall net price will be returned.
            otherwise Decimal("NaN") -> 'not a number' is returned.
        """
        getcontext().prec = 4
        if not isinstance(message, Message):
            return Decimal("NaN")
        p = self.net_price_by_iso2(message.recipient.iso2)
        if p.is_nan():
            return p
        return p * message.number_of_segments()

    def message_gross_price(self, message: Message) -> Decimal:
        """
        Getting the gross price for a message, by looking up the gross price for the message receiver country
        and multiply this with the number of needed SMS slits, to have overall gross price for sending this message.

        Parameters
        ----------
        message: Message
            Message which could be sent over the API

        Returns
        -------
        Decimal
            if price for the message receiver could be found in price_data, overall gross price will be returned.
            otherwise Decimal("NaN") -> 'not a number' is returned.
        """
        getcontext().prec = 4
        if not isinstance(message, Message):
            return Decimal("NaN")
        p = self.gross_price_by_iso2(message.recipient.iso2)
        if p.is_nan():
            return p
        return p * message.number_of_segments()

    def messages_net_price(self, list_of_messages: list[Message], all_or_none: bool = False) -> Decimal:
        """
        Getting the total net price for a list of messages, by looking up the net price for each message
        and sums them up. If at least one is not defined, it could either be ignored or the total net price
        is not defined, too (controlled by parameter all_or_none).

        Parameters
        ----------
        list_of_messages: list(Message)
            List of Message objects which could be sent over the API
        all_or_none: bool
            if False non defined prices will be ignored
            if True and at least one non defined net price is calculated for a message,
            the total result is also not defined

        Returns
        -------
        Decimal
            Total net price for message. If all_or_none is Ture and at least one message net price
            is 'not a number' the Decimal("NaN") -> 'not a number' is returned.
        """
        result = Decimal("0")
        if list_of_messages and len(list_of_messages) > 0:
            for m in list_of_messages:
                p = self.message_net_price(m)
                if p.is_nan():
                    if all_or_none:
                        logger.info('Aborted summing up the net prices of a message list, '
                                    'because at least one Price was not available.')
                        return p
                else:
                    result += p
        else:
            logger.debug('List for messages_gross_price was None or empty.')
        return result

    def messages_gross_price(self, list_of_messages: list[Message], all_or_none: bool = False) -> Decimal:
        """
        Getting the total gross price for a list of messages, by looking up the gross price for each message
        and sums them up. If at least one is not defined, it could either be ignored or the total gross price
        is not defined, too(controlled by parameter all_or_none).

        Parameters
        ----------
        list_of_messages: list(Message)
            List of Message objects which could be sent over the API
        all_or_none: bool
            if False non defined prices will be ignored
            if True and at least one non defined gross price is calculated for a message,
            the total result is also not defined

        Returns
        -------
        Decimal
            Total gross price for message. If all_or_none is Ture and at least one message gross price
            is 'not a number' the Decimal("NaN") -> 'not a number' is returned.
        """
        result = Decimal("0")
        if list_of_messages and len(list_of_messages) > 0:
            for m in list_of_messages:
                p = self.message_gross_price(m)
                if p.is_nan():
                    if all_or_none:
                        logger.info('Aborted summing up the gross prices of a message list, '
                                    'because at least one Price was not available.')
                        return p
                else:
                    result += p
        else:
            logger.debug('List for messages_gross_price was None or empty.')
        return result
