from typing import Optional

import logging
logger = logging.getLogger(__name__)

country_calling_code_to_ISO2_mapping = {
    # https://nationalnanpa.com/area_code_maps/ac_map_static.html
    "1": "US",  # using country calling code 1 for US, as default to skip as much area codes as possible
    # https://cnac.ca/area_code_maps/canadian_area_codes.htm
    "1204": "CA", "1226": "CA", "1236": "CA", "1249": "CA", "1250": "CA", "1263": "CA", "1289": "CA",
    "1306": "CA", "1343": "CA", "1354": "CA", "1365": "CA", "1367": "CA", "1368": "CA", "1382": "CA",
    "1403": "CA", "1416": "CA", "1418": "CA", "1428": "CA", "1431": "CA", "1437": "CA", "1438": "CA", "1450": "CA",
    "1456": "CA",  # see https://cnac.ca/canadian_dial_plan/Canadian_Dial_Plan_Table.pdf
    "1468": "CA", "1474": "CA",
    "1506": "CA", "1514": "CA", "1519": "CA", "1548": "CA", "1579": "CA", "1581": "CA", "1584": "CA", "1587": "CA",
    "1600": "CA",  # see https://cnac.ca/canadian_dial_plan/Canadian_Dial_Plan_Table.pdf
    "1604": "CA", "1613": "CA",
    "1622": "CA",  # see https://cnac.ca/canadian_dial_plan/Canadian_Dial_Plan_Table.pdf
    "1639": "CA", "1647": "CA", "1672": "CA", "1683": "CA",
    "1705": "CA", "1709": "CA",
    "1710": "CA",  # see https://cnac.ca/canadian_dial_plan/Canadian_Dial_Plan_Table.pdf
    "1742": "CA", "1753": "CA", "1778": "CA", "1780": "CA", "1782": "CA",
    "1807": "CA", "1819": "CA", "1825": "CA", "1867": "CA", "1873": "CA", "1879": "CA",
    "1902": "CA", "1905": "CA",
    # https://nationalnanpa.com/area_code_maps/area_code_maps_Country_Territory.html
    "1242": "BS", "1246": "BB", "1264": "AI", "1268": "AG", "1284": "VG",
    "1340": "VI", "1345": "KY",
    "1441": "BM", "1473": "GD",
    "1649": "TC", "1664": "MS", "1670": "MP", "1671": "GU", "1684": "AS",
    "1721": "SX", "1758": "LC", "1787": "PR", "1767": "DM", "1784": "VC",
    "1809": "DO", "1829": "DO", "1849": "DO", "1868": "TT", "1869": "KN", "1876": "JM",
    "1658": "JM",  # https://www.itu.int/dms_pub/itu-t/oth/02/02/T020200006C0002PDFE.pdf
    "1939": "PR",
    # https://www.itu.int/oth/T0202.aspx?parent=T0202
    "93": "AF", "355": "AL", "213": "DZ", "376": "AD", "244": "AO", "54": "AR", "374": "AM", "297": "AW", "61": "AU",
    "43": "AT", "994": "AZ",
    "973": "BH", "880": "BD", "375": "BY", "32": "BE", "501": "BZ", "229": "BJ", "975": "BT", "591": "BO", "387": "BA",
    "267": "BW", "55": "BR", "673": "BN", "359": "BG", "226": "BF", "257": "BI",
    "238": "CV", "855": "KH", "237": "CM", "236": "CF", "235": "TD", "56": "CL", "86": "CN", "57": "CO", "269": "KM",
    "242": "CG", "682": "CK", "506": "CR", "225": "CI", "385": "HR", "53": "CU", "357": "CY", "420": "CZ",
    "850": "KP", "243": "CD", "45": "DK", "253": "DJ",
    "593": "EC", "20": "EG", "503": "SV", "240": "GQ", "291": "ER", "372": "EE", "268": "SZ", "251": "ET",
    "500": "FK", "298": "FO", "679": "FJ", "358": "FI", "33": "FR", "262": "TF", "594": "GF", "689": "PF",
    "241": "GA", "220": "GM", "995": "GE", "49": "DE", "233": "GH", "350": "GI", "30": "GR", "299": "GL", "590": "GP",
    "502": "GT", "224": "GN", "245": "GW", "592": "GY",
    "509": "HT", "504": "HN", "852": "HK", "36": "HU",
    "354": "IS", "91": "IN", "62": "ID", "98": "IR", "964": "IQ", "353": "IE", "972": "IL", "39": "IT",
    "81": "JP", "962": "JO",
    "254": "KE", "686": "KI", "82": "KR", "383": "XK", "965": "KW", "996": "KG",
    "856": "LA", "371": "LV", "961": "LB", "266": "LS", "231": "LR", "218": "LY", "423": "LI", "370": "LT", "352": "LU",
    "853": "MO", "261": "MG", "265": "MW", "60": "MY", "960": "MV", "223": "ML", "356": "MT", "692": "MH", "596": "MQ",
    "222": "MR", "230": "MU", "52": "MX", "691": "FM", "373": "MD", "377": "MC", "976": "MN", "382": "ME", "212": "MA",
    "258": "MZ", "95": "MM",
    "264": "NA", "674": "NR", "977": "NP", "31": "NL", "687": "NC", "64": "NZ", "505": "NI", "227": "NE", "234": "NG",
    "683": "NU", "672": "NF", "389": "MK", "47": "NO",
    "968": "OM",
    "92": "PK", "680": "PW", "507": "PA", "675": "PG", "595": "PY", "51": "PE", "63": "PH", "48": "PL", "351": "PT",
    "974": "QA",
    "40": "RO", "250": "RW",
    "290": "SH", "247": "SH", "508": "PM", "685": "WS", "378": "SM", "239": "ST", "966": "SA", "221": "SN", "381": "RS",
    "248": "SC", "232": "SL", "65": "SG", "421": "SK", "386": "SI", "677": "SB", "252": "SO", "27": "ZA", "211": "SS",
    "34": "ES", "94": "LK", "249": "SD", "597": "SR", "46": "SE", "41": "CH", "963": "SY",
    "886": "TW", "992": "TJ", "255": "TZ", "66": "TH", "670": "TL", "228": "TG", "690": "TK", "676": "TO", "216": "TN",
    "90": "TR",  "993": "TM",  "688": "TV",
    "256": "UG", "380": "UA", "971": "AE", "44": "GB", "598": "UY", "998": "UZ",
    "678": "VU", "58": "VE", "84": "VN",
    "681": "WF",
    "967": "YE",
    "260": "ZM", "263": "ZW",
    # International Special Cases:
    "970": "PS",  # https://en.wikipedia.org/wiki/Telephone_numbers_in_the_State_of_Palestine
    "7": "RU",  # using country calling code 7 for RU, as default to skip as much area codes as possible
    "76": "KZ", "77": "KZ",  # https://www.itu.int/dms_pub/itu-t/oth/02/02/T020200006F0002PDFE.pdf
    # normally Diego Garcia belongs to British Indian Ocean Territory (IO), but ITU reserved DG for this island
    # see https://en.wikipedia.org/wiki/ISO_3166-2:IO
    "246": "DG",
    # https://www.itu.int/dms_pub/itu-t/oth/02/02/T02020000F80003PDFE.pdf
    "5997": "CW", "5994": "CW", "5993": "CW",
    # https://www.itu.int/dms_pub/itu-t/oth/02/02/T02020000F50004PDFE.pdf
    "5999": "BQ", "5996": "BQ",
    # TODO: Check if SMS could be sent to International Networks
    # "888237": "$A",  # AT&T Cingular Wireless Network
    # "8835110": "$B",  # Bandwidth.com, Inc.
    # "88234": "$C",  # BebbiCell AG
    # "8818": "$D", "8819": "$$", # Globalstar Inc.
    # "870": "$E",  # Inmarsat
    # "8816": "$F", "8817": "$$",  # Iridium
    # "88232": "$G",  # Maritime Communications Partner (MCP)
    # "888": "$H",  # returned to spare
    # "8835130": "$I",  # Sipme
    # "88233": "$J",  # spare
    # "88213": "$K",  # Telespazio S.p.A.
    # "88216": "$L",  # Thuraya
    # "87810": "$M",  # VISIONng
    # "8835100": "$N",  # Voxbone SA
}

country_calling_code_min_length = 1
country_calling_code_max_length = 4  # if comercial country calling codes are included this needs to be 7


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

    @staticmethod
    def number_to_iso2(number: str) -> str:
        """
        In cases a phone number country code is shared by multiple countries, the following area code is evaluated by
        this method to get the individual country ISO2 code. If no code can be found it returns 'ZZ' (ISO2 for Unknown)

        Alternatives:
        -------------
        Be aware, that geocoder of phonelib will give you the full country name with country_name_for_number
        So you would need a mapping to ISO2 code - like provided with https://pypi.org/project/pycountry/

        This method could be replaced by https://pypi.org/project/phone-iso3166/ which is currently in beta.

        Parameters
        ----------
        number: str
            the phone number to calculate the country for

        Returns
        -------
        str
            ISO2 Code of the country the number belongs to
        """
        result = 'ZZ'  # ISO2 default for 'unknown'
        l: int = len(number)
        # a loop testing from small to larger parts will override an already found region
        # from a small code with a region of a longer code, so we do not need to define all
        # cc to region and can group common regions with short code and only need longer for the rare exceptions
        for i in range(country_calling_code_min_length, country_calling_code_max_length + 1):
            if l > i:
                cc = number[1:i+1]
                if cc in country_calling_code_to_ISO2_mapping.keys():
                    result = country_calling_code_to_ISO2_mapping[cc]
        return result

    def __init__(self, _number: str, _iso2: str = None):
        """
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


        Country Calling Code vs. Region Code vs. ISO2
        ---------
            The pricing of the API is based on a specific country refered by ISO2 Code.

            In cases a phone number country calling code is shared by multiple countries - like +1,
            the region code delivered by libraries like phonelib would be "US".
            For pricing this is too unspecific, since Canada and the USA have share the same region,
            but have (e.g. € 0.0058 vs. € 0.0094 Price excl. VAT on December the 31st 2022).

            If you know the country, you can provide its ISO2 Code, if not the class will try to calculate it
            from the phone number and even includes the area code after the country code to differentiate individual
            countries within a shared country calling code.
        """
        E164PhoneNumber.basic_number_value_validation(number=_number, raising_error=True)
        self.number = _number

        if _iso2:
            if isinstance(_iso2, str):
                if len(_iso2) == 2:
                    self.iso2 = _iso2.upper()
                else:
                    logger.error(f'{_iso2} is not a two character string.')
                    raise ValueError('ISO2 of E164PhoneNumber must be a str of exactly two charters.')
            else:
                logger.error(f'{_iso2} is not a string.')
                raise ValueError('ISO2 of E164PhoneNumber must be a str.')
        else:
            logger.debug('ISO2 of E164PhoneNumber calculated from its number.')
            self.iso2 = E164PhoneNumber.number_to_iso2(_number)

    def __eq__(self, other):
        return isinstance(other, E164PhoneNumber) and \
            self.iso2 == other.iso2 and self.number == other.number
