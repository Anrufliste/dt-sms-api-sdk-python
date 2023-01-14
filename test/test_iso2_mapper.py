from unittest import TestCase

from dt_sms_sdk.iso2_mapper import ISO2Mapper


class DTSMSSDKISO2MapperTest(TestCase):

    def test_all_iso_of_county_are_unique(self):
        """
        Each iso must have only one country name, because that will be the reference for pricing.
        While normally an iso could have many full names, we could not correlate name<->iso<->pricing
        """
        iso2 = set(val for val in ISO2Mapper.country_name_to_ISO2_mapping.values())
        self.assertEqual(len(iso2), len(ISO2Mapper.country_name_to_ISO2_mapping.values()),
                         msg=f'Not all iso2 codes in ISO2Mapper.country_calling_code_to_ISO2_mapping are unique')

    def test_all_iso_of_country_in_iso_of_phone_number(self):
        """
        Check we can find all iso (and therefore pricing) by country calling codes
        """
        iso2 = set(val for val in ISO2Mapper.country_name_to_ISO2_mapping.values())

        missing = 0
        for c in iso2:
            if c not in ISO2Mapper.country_calling_code_to_ISO2_mapping.values():
                missing += 1
                print(f'{c} is missing in country_calling_code_to_ISO2_mapping')

        self.assertEqual(
            missing, 0,
            msg=f'{missing} iso2 country codes are missing in ISO2Mapper.country_calling_code_to_ISO2_mapping'
        )

    def test_all_iso_of_phone_number_are_in_iso_of_country_xor_in_no_routing(self):
        """
        The iso code from country calling code to iso code mapping must be either in the
        country name to iso (for pricing data) or in the no route list (no pricing).
        """
        iso2 = set(val for val in ISO2Mapper.country_calling_code_to_ISO2_mapping.values())

        missing = 0
        double = 0
        for c in iso2:
            if c not in ISO2Mapper.country_name_to_ISO2_mapping.values() and c not in ISO2Mapper.no_routing_of_ISO2:
                missing += 1
                print(f'{c} is missing in ISO2Mapper.country_name_to_ISO2_mapping AND ISO2Mapper.no_routing_of_ISO2')
            if c in ISO2Mapper.country_name_to_ISO2_mapping.values() and c in ISO2Mapper.no_routing_of_ISO2:
                double += 1
                print(f'{c} is in both, ISO2Mapper.country_name_to_ISO2_mapping AND ISO2Mapper.no_routing_of_ISO2')

        self.assertEqual(missing, 0, msg=f'{missing} iso2 country codes are missing in '
                                         f'ISO2Mapper.country_name_to_ISO2_mapping AND ISO2Mapper.no_routing_of_ISO2')
        self.assertEqual(missing, 0, msg=f'{double} iso2 country codes are in both, '
                                         f'ISO2Mapper.country_name_to_ISO2_mapping AND ISO2Mapper.no_routing_of_ISO2')
