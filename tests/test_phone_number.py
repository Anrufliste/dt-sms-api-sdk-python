from unittest import TestCase

from dt_sms_sdk.phone_number import E164PhoneNumber


class DTSMSSDKPhoneNumberTest(TestCase):

    def test_init_number_error(self):
        self.assertRaises(ValueError, E164PhoneNumber, 491755555555)

    def test_init_iso2_Error(self):
        self.assertRaises(ValueError, E164PhoneNumber, "+491755555555", 49)
        self.assertRaises(ValueError, E164PhoneNumber, "+491755555555", "D")
        self.assertRaises(ValueError, E164PhoneNumber, "+491755555555", "DEU")

    def test_init_iso2(self):
        n = E164PhoneNumber("+491755555555")
        self.assertEqual(n.iso2, "DE")
        self.assertEqual(n.number, "+491755555555")

        n = E164PhoneNumber("+491755555555", "DE")
        self.assertEqual(n.iso2, "DE")
        self.assertEqual(n.number, "+491755555555")

        n = E164PhoneNumber("+491755555555", "GB")
        self.assertEqual(n.iso2, "GB")
        self.assertEqual(n.number, "+491755555555")

        n = E164PhoneNumber("+447155555555")
        self.assertEqual(n.iso2, "GB")
        self.assertEqual(n.number, "+447155555555")

        n = E164PhoneNumber("+447155555555", "GB")
        self.assertEqual(n.iso2, "GB")
        self.assertEqual(n.number, "+447155555555")

        n = E164PhoneNumber("+447155555555", "DE")
        self.assertEqual(n.iso2, "DE")
        self.assertEqual(n.number, "+447155555555")

        n = E164PhoneNumber("+00000000000")
        self.assertEqual(n.iso2, "ZZ")
        self.assertEqual(n.number, "+00000000000")
