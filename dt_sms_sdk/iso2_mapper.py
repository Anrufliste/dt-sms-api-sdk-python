import logging
logger = logging.getLogger(__name__)


class ISO2Mapper(object):
    """
    A class mapping different keys for a country to ISO2 representation, so ISO2 Code interlinks those
    different key domains. Additionally lists of ISO2 codes are provided to specify a group and you can look up if a
    country belongs to it

    Dictionaries
    ------------
    country_calling_code_to_ISO2_mapping
        Country Calling Code of a phone number. There are helping constants
        country_calling_code_min_length & country_calling_code_max_length which specify the length of the used keys.
    country_name_to_ISO2_mapping
        Name of the country used in the DT price list

    Lists
    -----
    no_routing_of_ISO2
        Countries which are not routed by the API
    """

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
        "93": "AF", "355": "AL", "213": "DZ", "376": "AD", "244": "AO", "54": "AR", "374": "AM", "297": "AW",
        "61": "AU",
        "43": "AT", "994": "AZ",
        "973": "BH", "880": "BD", "375": "BY", "32": "BE", "501": "BZ", "229": "BJ", "975": "BT", "591": "BO",
        "387": "BA",
        "267": "BW", "55": "BR", "673": "BN", "359": "BG", "226": "BF", "257": "BI",
        "238": "CV", "855": "KH", "237": "CM", "236": "CF", "235": "TD", "56": "CL", "86": "CN", "57": "CO",
        "269": "KM",
        "242": "CG", "682": "CK", "506": "CR", "225": "CI", "385": "HR", "53": "CU", "357": "CY", "420": "CZ",
        "850": "KP", "243": "CD", "45": "DK", "253": "DJ",
        "593": "EC", "20": "EG", "503": "SV", "240": "GQ", "291": "ER", "372": "EE", "268": "SZ", "251": "ET",
        "500": "FK", "298": "FO", "679": "FJ", "358": "FI", "33": "FR", "262": "TF", "594": "GF", "689": "PF",
        "241": "GA", "220": "GM", "995": "GE", "49": "DE", "233": "GH", "350": "GI", "30": "GR", "299": "GL",
        "590": "GP",
        "502": "GT", "224": "GN", "245": "GW", "592": "GY",
        "509": "HT", "504": "HN", "852": "HK", "36": "HU",
        "354": "IS", "91": "IN", "62": "ID", "98": "IR", "964": "IQ", "353": "IE", "972": "IL", "39": "IT",
        "81": "JP", "962": "JO",
        "254": "KE", "686": "KI", "82": "KR", "383": "XK", "965": "KW", "996": "KG",
        "856": "LA", "371": "LV", "961": "LB", "266": "LS", "231": "LR", "218": "LY", "423": "LI", "370": "LT",
        "352": "LU",
        "853": "MO", "261": "MG", "265": "MW", "60": "MY", "960": "MV", "223": "ML", "356": "MT", "692": "MH",
        "596": "MQ",
        "222": "MR", "230": "MU", "52": "MX", "691": "FM", "373": "MD", "377": "MC", "976": "MN", "382": "ME",
        "212": "MA",
        "258": "MZ", "95": "MM",
        "264": "NA", "674": "NR", "977": "NP", "31": "NL", "687": "NC", "64": "NZ", "505": "NI", "227": "NE",
        "234": "NG",
        "683": "NU", "672": "NF", "389": "MK", "47": "NO",
        "968": "OM",
        "92": "PK", "680": "PW", "507": "PA", "675": "PG", "595": "PY", "51": "PE", "63": "PH", "48": "PL", "351": "PT",
        "974": "QA",
        "40": "RO", "250": "RW",
        "290": "SH", "247": "SH", "508": "PM", "685": "WS", "378": "SM", "239": "ST", "966": "SA", "221": "SN",
        "381": "RS",
        "248": "SC", "232": "SL", "65": "SG", "421": "SK", "386": "SI", "677": "SB", "252": "SO", "27": "ZA",
        "211": "SS",
        "34": "ES", "94": "LK", "249": "SD", "597": "SR", "46": "SE", "41": "CH", "963": "SY",
        "886": "TW", "992": "TJ", "255": "TZ", "66": "TH", "670": "TL", "228": "TG", "690": "TK", "676": "TO",
        "216": "TN",
        "90": "TR", "993": "TM", "688": "TV",
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
        # "8818": "$D", "8819": "$D", # Globalstar Inc.
        # "870": "$E",  # Inmarsat
        # "8816": "$F", "8817": "$F",  # Iridium
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
    country_calling_code_max_length = 4  # if commercial country calling codes are included this needs to be 7

    country_name_to_ISO2_mapping = {
        # searched country names used on https://developer.telekom.com/api/v1/prices and searched them on
        # https://www.iso.org/obp/ui/#search/code/ ... some are not correctly ISO used names, so an additional web search
        # was necessary to find the right match.
        "Belarus": "BY",
        "Timor-Leste": "TL",
        "Moldova": "MD",
        "Philippines": "PH",
        "Poland": "PL",
        "Germany": "DE",
        "Thailand": "TH",
        "Gibraltar": "GI",
        "Portugal": "PT",
        "Singapore": "SG",
        "Luxembourg": "LU",
        "Ireland": "IE",
        "Brunei Darussalam": "BN",
        "Iceland": "IS",
        "New Zealand": "NZ",
        "Albania": "AL",
        "Malta": "MT",
        "Cyprus": "CY",
        "Papua New Guinea": "PG",
        "Georgia": "GE",
        "Armenia": "AM",
        "Bulgaria": "BG",
        "Turkey": "TR",
        "American Samoa": "AS",
        "New Caledonia": "NC",
        "Slovenia": "SI",
        "Macedonia": "MK",
        "Liechtenstein": "LI",
        "Montenegro": "ME",
        "Canada": "CA",
        "United States": "US",
        "Puerto Rico": "PR",
        "Mexico": "MX",
        "Jamaica": "JM",
        "French Guiana": "GF",
        "Egypt": "EG",
        "Algeria": "DZ",
        "Morocco": "MA",
        "Tunisia": "TN",
        "Libya": "LY",
        "Gambia": "GM",
        "Senegal": "SN",
        "Mauritania": "MR",
        "Mali": "ML",
        "Guinea": "GN",
        "Saint Kitts and Nevis": "KN",
        "Ivory Coast": "CI",
        "Burkina Faso": "BF",
        "Niger": "NE",
        "Togo": "TG",
        "Benin": "BJ",
        "Mauritius": "MU",
        "Liberia": "LR",
        "Sierra Leone": "SL",
        "Ghana": "GH",
        "Nigeria": "NG",
        "Chad": "TD",
        "Dominica": "DM",
        "Central African Republic": "CF",
        "Cameroon": "CM",
        "Cuba": "CU",
        "Cape Verde": "CV",
        "Sao Tome and Principe": "ST",
        "Dominican Republic": "DO",
        "Equatorial Guinea": "GQ",
        "Haiti": "HT",
        "Gabon": "GA",
        "Republic of Congo": "CG",
        "Democratic Republic of Congo": "CD",
        "Angola": "AO",
        "Guinea-Bissau": "GW",
        "Seychelles": "SC",
        "Rwanda": "RW",
        "Ethiopia": "ET",
        "Somalia": "SO",
        "Djibouti": "DJ",
        "Kenya": "KE",
        "Tanzania": "TZ",
        "Uganda": "UG",
        "Burundi": "BI",
        "Mozambique": "MZ",
        "Zambia": "ZM",
        "Madagascar": "MG",
        "Zimbabwe": "ZW",
        "Namibia": "NA",
        "Malawi": "MW",
        "Botswana": "BW",
        "South Africa": "ZA",
        "Azerbaijan": "AZ",
        "Eritrea": "ER",
        "Kazakhstan": "KZ",
        "South Sudan": "SS",
        "India": "IN",
        "Pakistan": "PK",
        "Afghanistan": "AF",
        "Sri Lanka": "LK",
        "Myanmar": "MM",
        "Lebanon": "LB",
        "Jordan": "JO",
        "Syrian Arab Republic": "SY",
        "Iraq": "IQ",
        "Kuwait": "KW",
        "Saudi Arabia": "SA",
        "Yemen": "YE",
        "Oman": "OM",
        "United Arab Emirates": "AE",
        "State of Palestine": "PS",
        "Bahrain": "BH",
        "Qatar": "QA",
        "Mongolia": "MN",
        "Nepal": "NP",
        "Iran": "IR",
        "Uzbekistan": "UZ",
        "Tajikistan": "TJ",
        "Kyrgyzstan": "KG",
        "Turkmenistan": "TM",
        "Japan": "JP",
        "Belize": "BZ",
        "Guatemala": "GT",
        "El Salvador": "SV",
        "Republic of Korea": "KR",
        "Vietnam": "VN",
        "Honduras": "HN",
        "Hong Kong": "HK",
        "Nicaragua": "NI",
        "Macao": "MO",
        "Cambodia": "KH",
        "Costa Rica": "CR",
        "Panama": "PA",
        "Greece": "GR",
        "China": "CN",
        "Peru": "PE",
        "Netherlands": "NL",
        "Belgium": "BE",
        "France": "FR",
        "Argentina": "AR",
        "Taiwan": "TW",
        "Brazil": "BR",
        "Bangladesh": "BD",
        "Spain": "ES",
        "Hungary": "HU",
        "Bosnia and Herzegovina": "BA",
        "Chile": "CL",
        "Croatia": "HR",
        "Serbia": "RS",
        "Colombia": "CO",
        "Italy": "IT",
        "Venezuela": "VE",
        "Bolivia": "BO",
        "Guyana": "GY",
        "Romania": "RO",
        "Ecuador": "EC",
        "Switzerland": "CH",
        "Czech Republic": "CZ",
        "Slovakia": "SK",
        "Austria": "AT",
        "Paraguay": "PY",
        "United Kingdom": "GB",
        "Suriname": "SR",
        "Uruguay": "UY",
        "Denmark": "DK",
        "Sweden": "SE",
        "Norway": "NO",
        "Finland": "FI",
        "Malaysia": "MY",
        "Lithuania": "LT",
        "Latvia": "LV",
        "Estonia": "EE",
        "Australia": "AU",
        "Russian Federation": "RU",
        "Indonesia": "ID",
        "Ukraine": "UA"
    }

    no_routing_of_ISO2 = [
        # currently 01.01.2023 - the following 59 countries are neither listed in the pricing table, nor is an SMS sent to
        # a valid number of those countries by the API. Error Code is 422 with "No routing available for SMS ... " message.
        # The codes can be found by finding no match of phone_number.country_calling_code_to_ISO2_mapping values on
        # the pricing.country_name_to_ISO2_mapping values
        "MQ", "FJ", "BM", "KI",  # no routing confirmed
        "SB", "SD", "LC", "GD", "TC", "TF", "MV", "TV", "PW", "CW", "FM", "GP", "SM", "LA", "VC", "LS", "BT", "BB",
        "TK", "MP", "GL", "TO", "WS", "XK", "PF", "VG", "WF", "MC", "AW", "KM", "DG", "TT", "BS", "NF", "SH", "BQ",
        "AI", "FK", "MS", "NU", "MH", "FO", "IL", "VU", "SX", "GU", "AG", "AD", "NR", "KP", "SZ", "CK", "PM", "KY", "VI"
    ]

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
            the phone number in E164 format to calculate the country for

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
        for i in range(ISO2Mapper.country_calling_code_min_length, ISO2Mapper.country_calling_code_max_length + 1):
            if l > i:
                cc = number[1: i + 1]
                if cc in ISO2Mapper.country_calling_code_to_ISO2_mapping.keys():
                    result = ISO2Mapper.country_calling_code_to_ISO2_mapping[cc]
        return result

    @staticmethod
    def basic_iso2_value_validation(iso2: str, raising_error: bool = False) -> bool:
        """
        Just validating the data type of the iso2 and simple structure rules,
        no validation towards assigned iso2 codes.

        Parameters
        ----------
        iso2: str
            iso2 code
        raising_error: bool
            flag to control, if negative validation will raise an exception

        Returns
        -------
        bool
            if simple validation of iso2 code was successful

        Raises
        ------
        ValueError
            if parameter raising_error is True and validation of the iso2 code was unsuccessful
        """
        if not isinstance(iso2, str):
            logger.debug(f'ISO2Mapper: {iso2} is not a string.')
            if raising_error:
                raise ValueError('ISO2 Code be a str.')
            return False
        else:
            if len(iso2) == 2:
                return True
            else:
                logger.error(f'ISO2Mapper: {iso2} is not a two character string.')
                if raising_error:
                    raise ValueError('ISO2 Code must be a str of exactly two charters.')
                return False
