from unittest import TestCase

from dt_sms_sdk.message import Message
from dt_sms_sdk.phone_number import E164PhoneNumber


class DTSMSSDKMessageTest(TestCase):

    def test_is_gsm_char_set(self):
        self.assertEqual(Message._len_non_gsm_char("A"), 1)
        self.assertEqual(Message._len_non_gsm_char("\uFFFF"), 1)
        self.assertEqual(Message._len_non_gsm_char("𐀀"), 2)
        self.assertEqual(Message._len_non_gsm_char("👇"), 2)

    def test_len_non_gsm_str(self):
        self.assertEqual(Message._len_non_gsm_str("A"), 1)
        self.assertEqual(Message._len_non_gsm_str("AB"), 2)
        self.assertEqual(Message._len_non_gsm_str("\uFFFF"), 1)
        self.assertEqual(Message._len_non_gsm_str("𐀀"), 2)
        self.assertEqual(Message._len_non_gsm_str("👇"), 2)
        self.assertEqual(Message._len_non_gsm_str("👨‍👨‍👧‍👧"), 11)

    def test_gsm_split_count_0(self):
        self.assertEqual(Message.gsm_split_count(None), 0)
        self.assertEqual(Message.gsm_split_count(""), 0)

    def test_gsm_split_count_1(self):
        self.assertEqual(Message.gsm_split_count("0"), 1)
        self.assertEqual(Message.gsm_split_count("0123456789" +  # 010
                                                 "0123456789" +  # 020
                                                 "0123456789" +  # 030
                                                 "0123456789" +  # 040
                                                 "0123456789" +  # 050
                                                 "0123456789" +  # 060
                                                 "0123456789" +  # 070
                                                 "0123456789" +  # 080
                                                 "0123456789" +  # 090
                                                 "0123456789" +  # 100
                                                 "0123456789" +  # 110
                                                 "0123456789" +  # 120
                                                 "0123456789" +  # 130
                                                 "0123456789" +  # 140
                                                 "0123456789" +  # 150
                                                 "0123456789"    # 160
                                                 ), 1)
        self.assertEqual(Message.gsm_split_count("👇"), 1)
        self.assertEqual(Message.gsm_split_count("👇👇👇👇👇" +  # 10
                                                 "👇👇👇👇👇" +  # 20
                                                 "👇👇👇👇👇" +  # 30
                                                 "👇👇👇👇👇" +  # 40
                                                 "👇👇👇👇👇" +  # 50
                                                 "👇👇👇👇👇" +  # 60
                                                 "👇👇👇👇👇"    # 70
                                                 ), 1)
        self.assertEqual(Message.gsm_split_count("0123456789" +  # 010
                                                 "0123456789" +  # 020
                                                 "0123456789" +  # 030
                                                 "0123456789" +  # 040
                                                 "0123456789" +  # 050
                                                 "0123456789" +  # 060
                                                 "012345678" +   # 069
                                                 "\uFFFF"        # 070, but non GSM
                                                 ), 1)

    def test_gsm_split_count_2(self):
        self.assertEqual(Message.gsm_split_count("0123456789" +  # 010
                                                 "0123456789" +  # 020
                                                 "0123456789" +  # 030
                                                 "0123456789" +  # 040
                                                 "0123456789" +  # 050
                                                 "0123456789" +  # 060
                                                 "0123456789" +  # 070
                                                 "0123456789" +  # 080
                                                 "0123456789" +  # 090
                                                 "0123456789" +  # 100
                                                 "0123456789" +  # 110
                                                 "0123456789" +  # 120
                                                 "0123456789" +  # 130
                                                 "0123456789" +  # 140
                                                 "0123456789" +  # 150
                                                 "01234567891"   # 161
                                                 ), 2)
        self.assertEqual(Message.gsm_split_count("0123456789" +  # 010
                                                 "0123456789" +  # 020
                                                 "0123456789" +  # 030
                                                 "0123456789" +  # 040
                                                 "0123456789" +  # 050
                                                 "0123456789" +  # 060
                                                 "0123456789" +  # 070
                                                 "0123456789" +  # 080
                                                 "0123456789" +  # 090
                                                 "0123456789" +  # 100
                                                 "0123456789" +  # 110
                                                 "0123456789" +  # 120
                                                 "0123456789" +  # 130
                                                 "0123456789" +  # 140
                                                 "0123456789" +  # 150
                                                 "0123456789" +  # 160
                                                 "0123456789" +  # 170
                                                 "0123456789" +  # 180
                                                 "0123456789" +  # 190
                                                 "0123456789" +  # 200
                                                 "0123456789" +  # 210
                                                 "0123456789" +  # 220
                                                 "0123456789" +  # 230
                                                 "0123456789" +  # 240
                                                 "0123456789" +  # 250
                                                 "0123456789" +  # 260
                                                 "0123456789" +  # 270
                                                 "0123456789" +  # 280
                                                 "0123456789" +  # 290
                                                 "0123456789" +  # 300
                                                 "012345"        # 306
                                                 ), 2)
        self.assertEqual(Message.gsm_split_count("👇👇👇👇👇" +  # 10
                                                 "👇👇👇👇👇" +  # 20
                                                 "👇👇👇👇👇" +  # 30
                                                 "👇👇👇👇👇" +  # 40
                                                 "👇👇👇👇👇" +  # 50
                                                 "👇👇👇👇👇" +  # 60
                                                 "👇👇👇👇👇1"   # 71
                                                 ), 2)
        self.assertEqual(Message.gsm_split_count("👇👇👇👇👇" +  # 010
                                                 "👇👇👇👇👇" +  # 020
                                                 "👇👇👇👇👇" +  # 030
                                                 "👇👇👇👇👇" +  # 040
                                                 "👇👇👇👇👇" +  # 050
                                                 "👇👇👇👇👇" +  # 060
                                                 "👇👇👇👇👇" +  # 070
                                                 "👇👇👇👇👇" +  # 080
                                                 "👇👇👇👇👇" +  # 090
                                                 "👇👇👇👇👇" +  # 100
                                                 "👇👇👇👇👇" +  # 110
                                                 "👇👇👇👇👇" +  # 120
                                                 "👇👇👇👇👇" +  # 130
                                                 "👇👇"          # 134
                                                 ), 2)
    def test_gsm_split_count_3(self):
        self.assertEqual(Message.gsm_split_count("0123456789" +  # 010
                                                 "0123456789" +  # 020
                                                 "0123456789" +  # 030
                                                 "0123456789" +  # 040
                                                 "0123456789" +  # 050
                                                 "0123456789" +  # 060
                                                 "0123456789" +  # 070
                                                 "0123456789" +  # 080
                                                 "0123456789" +  # 090
                                                 "0123456789" +  # 100
                                                 "0123456789" +  # 110
                                                 "0123456789" +  # 120
                                                 "0123456789" +  # 130
                                                 "0123456789" +  # 140
                                                 "0123456789" +  # 150
                                                 "0123456789" +  # 160
                                                 "0123456789" +  # 170
                                                 "0123456789" +  # 180
                                                 "0123456789" +  # 190
                                                 "0123456789" +  # 200
                                                 "0123456789" +  # 210
                                                 "0123456789" +  # 220
                                                 "0123456789" +  # 230
                                                 "0123456789" +  # 240
                                                 "0123456789" +  # 250
                                                 "0123456789" +  # 260
                                                 "0123456789" +  # 270
                                                 "0123456789" +  # 280
                                                 "0123456789" +  # 290
                                                 "0123456789" +  # 300
                                                 "0123456"       # 307
                                                 ), 3)
        self.assertEqual(Message.gsm_split_count("👇👇👇👇👇" +  # 010
                                                 "👇👇👇👇👇" +  # 020
                                                 "👇👇👇👇👇" +  # 030
                                                 "👇👇👇👇👇" +  # 040
                                                 "👇👇👇👇👇" +  # 050
                                                 "👇👇👇👇👇" +  # 060
                                                 "👇👇👇👇👇" +  # 070
                                                 "👇👇👇👇👇" +  # 080
                                                 "👇👇👇👇👇" +  # 090
                                                 "👇👇👇👇👇" +  # 100
                                                 "👇👇👇👇👇" +  # 110
                                                 "👇👇👇👇👇" +  # 120
                                                 "👇👇👇👇👇" +  # 130
                                                 "👇👇1"         # 135
                                                 ), 3)
        self.assertEqual(Message.gsm_split_count("0123456789" +  # 010
                                                 "0123456789" +  # 020
                                                 "0123456789" +  # 030
                                                 "0123456789" +  # 040
                                                 "0123456789" +  # 050
                                                 "0123456789" +  # 060
                                                 "0123456789" +  # 070
                                                 "0123456789" +  # 080
                                                 "0123456789" +  # 090
                                                 "0123456789" +  # 100
                                                 "0123456789" +  # 110
                                                 "0123456789" +  # 120
                                                 "0123456789" +  # 130
                                                 "0123" +        # 134
                                                 "\uFFFF"        # 135, but non GSM
                                                 ), 3)

    def test_init_sender(self):
        m = Message("NoWhere", E164PhoneNumber("+491755555555"), "Hello World")
        self.assertEqual(m.sender, "NoWhere")

        m = Message("+4917111111", E164PhoneNumber("+491755555555"), "Hello World")
        self.assertEqual(m.sender, E164PhoneNumber("+4917111111"))

        m = Message(4917111111, E164PhoneNumber("+491755555555"), "Hello World")
        self.assertEqual(m.sender, E164PhoneNumber("+4917111111"))

        m = Message("+49", E164PhoneNumber("+491755555555"), "Hello World")
        self.assertEqual(m.sender, "+49")

    def test_init_receiver(self):
        m = Message("NoWhere", E164PhoneNumber("+491755555555"), "Hello World")
        self.assertEqual(m.recipient, E164PhoneNumber("+491755555555"))
        self.assertEqual(m.recipient.iso2, "DE")

        m = Message("NoWhere", E164PhoneNumber("+491755555555", "GB"), "Hello World")
        self.assertEqual(m.recipient.number, "+491755555555")
        self.assertEqual(m.recipient.iso2, "GB")

        m = Message("NoWhere", "+491755555555", "Hello World")
        self.assertEqual(m.recipient, E164PhoneNumber("+491755555555"))
        self.assertEqual(m.recipient.iso2, "DE")

        m = Message("NoWhere", 491755555555, "Hello World")
        self.assertEqual(m.recipient, E164PhoneNumber("+491755555555"))
        self.assertEqual(m.recipient.iso2, "DE")

        with self.assertRaises(ValueError):
            Message("NoWhere", "+49", "Hello World")

        with self.assertRaises(ValueError):
            Message("NoWhere", "SomeWhere", "Hello World")

    def test_init(self):
        m = Message(E164PhoneNumber("+49175444444"), E164PhoneNumber("+491755555555"), "Hello World")
        self.assertEqual(m.sender, E164PhoneNumber("+49175444444"))
        self.assertEqual(m.recipient, E164PhoneNumber("+491755555555"))
        self.assertEqual(m.recipient.iso2, "DE")
        self.assertEqual(m.body, "Hello World")
        self.assertEqual(m.number_of_segments(), 1)
