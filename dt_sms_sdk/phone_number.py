from typing import Optional


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
    "1939": "PR",
    # TODO: Non NANPA Country Codes
    "49": "DE"
}

country_calling_code_min_length = 1
country_calling_code_max_length = 4


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
    def number_to_iso2(number: str) -> Optional[str]:
        """
        In cases a phone number country code is shared by multiple countries, the following area code is evaluated by
            this method to get the individual country ISO2 code.

        Parameters
        ----------
        number: str
            the phone number to calculate the country for

        Returns
        -------
        str
            ISO2 Code of the country the number belongs to
        """
        result = None
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
        self.number = _number
        if _iso2:
            self.iso2 = _iso2.upper()
        else:
            self.iso2 = E164PhoneNumber.number_to_iso2(_number)
