from unittest import TestCase

from dt_sms_sdk.message import Message


class DTSMSSDKMessageTestAPISpecific(TestCase):

    # checked on 23rd December 2022 / Version 1.1.5 which double mapping is used on the API:

    def test_gsm_split_count_api_specific_u00E7_vs_u00C7(self):
        self.assertEqual(Message.gsm_split_count(
            "ççççççççççççççççççççççççççççççççççççççççççççççççççççççççççççççççççççççç"
        ), 2)
        self.assertEqual(Message.gsm_split_count(
            "ÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇ"
        ), 1)

    def test_gsm_split_count_api_specific_u0041_vs_u0391(self):
        self.assertEqual(Message.gsm_split_count(
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        ), 1)
        self.assertEqual(Message.gsm_split_count(
            "ΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑΑ"
        ), 2)

    def test_gsm_split_count_api_specific_u0042_vs_u0392(self):
        self.assertEqual(Message.gsm_split_count(
            "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"
        ), 1)
        self.assertEqual(Message.gsm_split_count(
            "ΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒΒ"
        ), 2)

    def test_gsm_split_count_api_specific_u0045_vs_u0395(self):
        self.assertEqual(Message.gsm_split_count(
            "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE"
        ), 1)
        self.assertEqual(Message.gsm_split_count(
            "ΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕΕ"
        ), 2)

    def test_gsm_split_count_api_specific_u0048_vs_u0397(self):
        self.assertEqual(Message.gsm_split_count(
            "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
        ), 1)
        self.assertEqual(Message.gsm_split_count(
            "ΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗΗ"
        ), 2)

    def test_gsm_split_count_api_specific_u0049_vs_u0399(self):
        self.assertEqual(Message.gsm_split_count(
            "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
        ), 1)
        self.assertEqual(Message.gsm_split_count(
            "ΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙΙ"
        ), 2)

    def test_gsm_split_count_api_specific_u004B_vs_u039A(self):
        self.assertEqual(Message.gsm_split_count(
            "KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK"
        ), 1)
        self.assertEqual(Message.gsm_split_count(
            "ΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚΚ"
        ), 2)

    def test_gsm_split_count_api_specific_u004D_vs_u039C(self):
        self.assertEqual(Message.gsm_split_count(
            "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM"
        ), 1)
        self.assertEqual(Message.gsm_split_count(
            "ΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜΜ"
        ), 2)

    def test_gsm_split_count_api_specific_u004E_vs_u039D(self):
        self.assertEqual(Message.gsm_split_count(
            "NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN"
        ), 1)
        self.assertEqual(Message.gsm_split_count(
            "ΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝΝ"
        ), 2)

    def test_gsm_split_count_api_specific_u004D_vs_u039F(self):
        self.assertEqual(Message.gsm_split_count(
            "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"
        ), 1)
        self.assertEqual(Message.gsm_split_count(
            "ΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟΟ"
        ), 2)

    def test_gsm_split_count_api_specific_u0050_vs_u03A1(self):
        self.assertEqual(Message.gsm_split_count(
            "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP"
        ), 1)
        self.assertEqual(Message.gsm_split_count(
            "ΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡΡ"
        ), 2)

    def test_gsm_split_count_api_specific_u0054_vs_u03A4(self):
        self.assertEqual(Message.gsm_split_count(
            "TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT"
        ), 1)
        self.assertEqual(Message.gsm_split_count(
            "ΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤΤ"
        ), 2)

    def test_gsm_split_count_api_specific_u0058_vs_u03A7(self):
        self.assertEqual(Message.gsm_split_count(
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        ), 1)
        self.assertEqual(Message.gsm_split_count(
            "ΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧΧ"
        ), 2)

    def test_gsm_split_count_api_specific_u0059_vs_u03A5(self):
        self.assertEqual(Message.gsm_split_count(
            "YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY"
        ), 1)
        self.assertEqual(Message.gsm_split_count(
            "ΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥΥ"
        ), 2)

    def test_gsm_split_count_api_specific_u005A_vs_u0396(self):
        self.assertEqual(Message.gsm_split_count(
            "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ"
        ), 1)
        self.assertEqual(Message.gsm_split_count(
            "ΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖΖ"
        ), 2)

