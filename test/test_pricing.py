from unittest import TestCase
from unittest.mock import MagicMock, patch

from decimal import Decimal, getcontext
from dt_sms_sdk.iso2_mapper import ISO2Mapper
from dt_sms_sdk.pricing import Currency, Price, Pricing


class DTSMSSDKPricingTest(TestCase):

    def _test_all_pricing_data_countries_are_mapped_to_iso(self, pricing_data, pricing_data_label):
        """
        Helper Method, to test if the country names used in pricing data are available in iso mapping.

        This method will be used for the offline / default and the currently online Pricing Data.
        """
        missing_iso = 0
        for p in pricing_data:
            if p["country"] not in ISO2Mapper.country_name_to_ISO2_mapping.keys():
                missing_iso += 1
                print(f'{p["country"]} is missing in country_name_to_ISO2_mapping')

        self.assertEqual(missing_iso, 0,
                         msg=f'{missing_iso} country names of {pricing_data_label} Pricing Data are missing in '
                             f'ISO2Mapper.country_name_to_ISO2_mapping')

    def test_all_default_pricing_data_countries_are_mapped_to_iso(self):
        self._test_all_pricing_data_countries_are_mapped_to_iso(Pricing.download(), "default")

    def test_all_current_online_pricing_data_countries_are_mapped_to_iso(self):
        self._test_all_pricing_data_countries_are_mapped_to_iso(Pricing.download(), "current online")

    def _test_all_iso_are_mapped_to_pricing_data_countries(self, pricing_data, pricing_data_label):
        """
        Helper Method, to test if the country names in iso mapping are used in pricing data.

        This method will be used for the offline / default and the currently online Pricing Data.
        """
        missing_country = 0
        countries = set()
        for p in pricing_data:
            countries.add(p["country"])

        for c in ISO2Mapper.country_name_to_ISO2_mapping.keys():
            if c not in countries:
                missing_country += 1
                print(f'{c} is missing in {pricing_data_label} Pricing Data')

        self.assertEqual(missing_country, 0,
                         msg=f'{missing_country} country names of ISO2Mapper.country_name_to_ISO2_mapping '
                             f'are missing in {pricing_data_label} Pricing Data')

    def test_all_iso_are_mapped_to_current_online_pricing_data_countries(self):
        self._test_all_iso_are_mapped_to_pricing_data_countries(Pricing.download(), "current online")

    def test_all_iso_are_mapped_to_default_pricing_data_countries(self):
        self._test_all_iso_are_mapped_to_pricing_data_countries(Pricing.download(), "default")

    @patch('dt_sms_sdk.pricing.requests.get')
    def test_download_connection_error(self, mock_get):
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError()

        # downloading the Pricing and get None for Connection Error
        self.assertEqual(Pricing.download(), None)

    def test_download_header_fields(self):
        import requests_mock
        import requests

        def custom_matcher(request):
            self.assertTrue("User-Agent" in request.headers.keys())
            # "Host" is not part on this level and will automatically be added - no need to test.
            resp = requests.Response()
            resp.status_code = 200
            resp._content = b'[{}]'
            return resp

        with requests_mock.Mocker() as mock:
            mock.add_matcher(custom_matcher)
            self.assertEqual(Pricing.download(), [{}])

    @patch('dt_sms_sdk.pricing.requests.get')
    def test_download_no_json_error(self, mock_get):
        import requests
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = requests.exceptions.JSONDecodeError("error", "\n\n", 1)
        mock_get.return_value = mock_response
        # downloading the Pricing and get None for JSONDecode Error
        self.assertEqual(Pricing.download(), None)

    @patch('dt_sms_sdk.pricing.requests.get')
    def test_download_wrong_basic_json(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}

        mock_get.return_value = mock_response

        # downloading the Pricing and get None for not getting a list
        self.assertEqual(Pricing.download(), None)

    @patch('dt_sms_sdk.pricing.requests.get')
    def test_download_right_basic_json(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"key": "value"}]

        mock_get.return_value = mock_response

        self.assertEqual(Pricing.download(), [{"key": "value"}])

    def test_currency(self):
        self.assertEqual(Currency.EURO, Currency.from_str("€"))
        self.assertEqual(Currency.EURO, Currency.from_str("₠"))
        self.assertEqual(Currency.EURO, Currency.from_str("Euro"))
        self.assertEqual(Currency.EURO, Currency.from_str("EUR"))
        self.assertEqual(Currency.EURO, Currency.from_str("EURO"))

    def test_currency_invalid(self):
        self.assertRaises(ValueError, Currency.from_str, None)
        self.assertRaises(ValueError, Currency.from_str, "")
        self.assertRaises(ValueError, Currency.from_str, " ")
        self.assertRaises(ValueError, Currency.from_str, "!")
        self.assertRaises(ValueError, Currency.from_str, "pocket money")

    def test_currency_not_yet_supported(self):
        """
        Testing all available Unicode Symbols for currencies as listed on
        https://www.compart.com/en/unicode/category/Sc
        """
        self.assertRaises(NotImplementedError, Currency.from_str, "$")
        self.assertRaises(NotImplementedError, Currency.from_str, "﹩")
        self.assertRaises(NotImplementedError, Currency.from_str, "＄")
        self.assertRaises(NotImplementedError, Currency.from_str, "¢")
        self.assertRaises(NotImplementedError, Currency.from_str, "￠")
        self.assertRaises(NotImplementedError, Currency.from_str, "£")
        self.assertRaises(NotImplementedError, Currency.from_str, "￡")
        self.assertRaises(NotImplementedError, Currency.from_str, "¤")
        self.assertRaises(NotImplementedError, Currency.from_str, "¥")
        self.assertRaises(NotImplementedError, Currency.from_str, "￥")
        self.assertRaises(NotImplementedError, Currency.from_str, "֏")
        self.assertRaises(NotImplementedError, Currency.from_str, "؋")
        self.assertRaises(NotImplementedError, Currency.from_str, "߾")
        self.assertRaises(NotImplementedError, Currency.from_str, "߿")
        self.assertRaises(NotImplementedError, Currency.from_str, "৲")
        self.assertRaises(NotImplementedError, Currency.from_str, "৳")
        self.assertRaises(NotImplementedError, Currency.from_str, "৻")
        self.assertRaises(NotImplementedError, Currency.from_str, "૱")
        self.assertRaises(NotImplementedError, Currency.from_str, "௹")
        self.assertRaises(NotImplementedError, Currency.from_str, "฿")
        self.assertRaises(NotImplementedError, Currency.from_str, "៛")
        self.assertRaises(NotImplementedError, Currency.from_str, "₡")
        self.assertRaises(NotImplementedError, Currency.from_str, "₢")
        self.assertRaises(NotImplementedError, Currency.from_str, "₣")
        self.assertRaises(NotImplementedError, Currency.from_str, "₤")
        self.assertRaises(NotImplementedError, Currency.from_str, "₥")
        self.assertRaises(NotImplementedError, Currency.from_str, "₦")
        self.assertRaises(NotImplementedError, Currency.from_str, "₧")
        self.assertRaises(NotImplementedError, Currency.from_str, "₨")
        self.assertRaises(NotImplementedError, Currency.from_str, "₩")
        self.assertRaises(NotImplementedError, Currency.from_str, "￦")
        self.assertRaises(NotImplementedError, Currency.from_str, "₪")
        self.assertRaises(NotImplementedError, Currency.from_str, "₫")
        self.assertRaises(NotImplementedError, Currency.from_str, "₭")
        self.assertRaises(NotImplementedError, Currency.from_str, "₮")
        self.assertRaises(NotImplementedError, Currency.from_str, "₯")
        self.assertRaises(NotImplementedError, Currency.from_str, "₰")
        self.assertRaises(NotImplementedError, Currency.from_str, "₱")
        self.assertRaises(NotImplementedError, Currency.from_str, "₲")
        self.assertRaises(NotImplementedError, Currency.from_str, "₳")
        self.assertRaises(NotImplementedError, Currency.from_str, "₴")
        self.assertRaises(NotImplementedError, Currency.from_str, "₵")
        self.assertRaises(NotImplementedError, Currency.from_str, "₶")
        self.assertRaises(NotImplementedError, Currency.from_str, "₷")
        self.assertRaises(NotImplementedError, Currency.from_str, "₸")
        self.assertRaises(NotImplementedError, Currency.from_str, "₹")
        self.assertRaises(NotImplementedError, Currency.from_str, "₺")
        self.assertRaises(NotImplementedError, Currency.from_str, "₻")
        self.assertRaises(NotImplementedError, Currency.from_str, "₼")
        self.assertRaises(NotImplementedError, Currency.from_str, "₽")
        self.assertRaises(NotImplementedError, Currency.from_str, "₾")
        self.assertRaises(NotImplementedError, Currency.from_str, "₿")
        self.assertRaises(NotImplementedError, Currency.from_str, "꠸")
        self.assertRaises(NotImplementedError, Currency.from_str, "﷼")
        self.assertRaises(NotImplementedError, Currency.from_str, "𑿝")
        self.assertRaises(NotImplementedError, Currency.from_str, "𑿞")
        self.assertRaises(NotImplementedError, Currency.from_str, "𑿟")
        self.assertRaises(NotImplementedError, Currency.from_str, "𑿠")
        self.assertRaises(NotImplementedError, Currency.from_str, "𞋿")
        self.assertRaises(NotImplementedError, Currency.from_str, "𞲰")

    def test_raw_is_list(self):
        self.assertFalse(Pricing._raw_is_list(None))
        self.assertFalse(Pricing._raw_is_list("My Price"))
        self.assertFalse(Pricing._raw_is_list(()))
        self.assertFalse(Pricing._raw_is_list(("p1", "p2")))
        self.assertFalse(Pricing._raw_is_list({}))
        self.assertFalse(Pricing._raw_is_list({"p1": 0, "p2": 1}))

        self.assertTrue(Pricing._raw_is_list([]))
        self.assertTrue(Pricing._raw_is_list(["p1", "p2"]))

    def test_raw_item_iso2_code(self):
        self.assertEqual(Pricing._raw_item_iso2_code(None), None)
        self.assertEqual(Pricing._raw_item_iso2_code(1), None)
        self.assertEqual(Pricing._raw_item_iso2_code("Deutschland"), None)
        self.assertEqual(Pricing._raw_item_iso2_code({"Deutschland"}), None)
        self.assertEqual(Pricing._raw_item_iso2_code({"country"}), None)
        self.assertEqual(Pricing._raw_item_iso2_code({"country": "Wonderland"}), None)
        self.assertEqual(Pricing._raw_item_iso2_code({"country": "Germany"}), "DE")

    def test_price_init(self):

        # testing default vat=0.19 and currency is EURO
        self.assertEqual(
            Price("Wonderland", 0, 0, 0.19, Currency.EURO),
            Price("Wonderland", 0, 0)
        )

        p = Price("Wonderland", 1, 1.1, "0.1", "€")
        getcontext().prec = 4
        self.assertEqual(p.net_price, Decimal("1.0"))
        self.assertEqual(p.gross_price, Decimal("1.1"))
        self.assertEqual(p.vat, Decimal("0.1"))
        self.assertEqual(p.currency, Currency.EURO)

        self.assertRaises(ValueError, Price, "Wonderland", "xx", 1.1, "0.1", "€")
        self.assertRaises(ValueError, Price, "Wonderland", 1, 1.1, "0.1", "$")  # Not yet implemented
        self.assertRaises(ValueError, Price, "Wonderland", 1, 1.1, "0.1", "?")

    def test_raw_item_to_price(self):
        self.assertEqual(Pricing._raw_item_to_price(None), None)
        self.assertEqual(Pricing._raw_item_to_price(1), None)
        self.assertEqual(Pricing._raw_item_to_price("Deutschland"), None)
        self.assertEqual(Pricing._raw_item_to_price({"country"}), None)
        self.assertEqual(Pricing._raw_item_to_price({"country": "Wonderland"}), None)
        self.assertEqual(Pricing._raw_item_to_price({"country": "Germany"}), None)
        self.assertEqual(Pricing._raw_item_to_price(
            {"country": "Wonderland", "grossPrice": 0, "vat": 0.19, "currency": "EUR"}),
            None
        )
        self.assertEqual(Pricing._raw_item_to_price(
            {"country": "Wonderland", "netPrice": 0, "vat": 0.19, "currency": "EUR"}),
            None
        )
        self.assertEqual(Pricing._raw_item_to_price(
            {"country": "Wonderland", "netPrice": 0, "grossPrice": 0, "currency": "EUR"}),
            None
        )
        self.assertEqual(Pricing._raw_item_to_price(
            {"country": "Wonderland", "netPrice": 0, "grossPrice": 0, "vat": 0.19}),
            None
        )
        self.assertEqual(Pricing._raw_item_to_price(
            {"country": "Wonderland", "netPrice": 0, "grossPrice": 0, "vat": 0.19, "currency": "EUR"}),
            Price("Wonderland", 0, 0, 0.19, Currency.EURO)
        )

    def test_raw_list(self):
        p = Pricing.prices_by_iso2(
            [{"country": "Wonderland", "netPrice": 0.22, "grossPrice": 0.3, "vat": 0.19, "currency": "EUR"}]
        )
        self.assertEqual(len(p), 0)

        p = Pricing.prices_by_iso2(
            [{"country": "Germany", "netPrice": 0.22, "grossPrice": 0.3, "vat": 0.19, "currency": "EUR"}]
        )
        self.assertEqual(len(p), 1)
        self.assertEqual(p["DE"].gross_price, Decimal("0.3"))

    def test_default_vs_online(self):
        """
        checks if the default prices are still up-to-date - a new version of the SDK
        should also have a current default price list.
        """
        default = Pricing.prices_by_iso2(Pricing.default())
        online = Pricing.prices_by_iso2(Pricing.download())

        keys = set(val for val in (list(default.keys()) + list(online.keys())))

        all_the_same = True
        for k in keys:
            if not default[k] == online[k]:
                all_the_same = False
                print(f'Default Price of {k} does not match online Price')

        self.assertTrue(all_the_same)

    def test_pricing(self):
        with self.assertLogs() as captured:
            p = Pricing([{"country": "Germany", "netPrice": 0.22, "grossPrice": 0.3, "vat": 0.19, "currency": "EUR"}])
        self.assertEqual(len(captured.records), len(ISO2Mapper.country_name_to_ISO2_mapping)-1)
        for i in range(len(ISO2Mapper.country_name_to_ISO2_mapping)-1):
            self.assertEqual(captured.records[i].getMessage()[:-3],
                             "Loaded Pricing Data does not include Country, which is part of country name mapping:"
                             )

        with self.assertLogs() as captured:
            p = Pricing([{"country": "Wonderland", "netPrice": 0.2, "grossPrice": 0.3, "vat": 0.19, "currency": "EUR"}])
        self.assertEqual(len(captured.records), len(ISO2Mapper.country_name_to_ISO2_mapping)+2)
        self.assertEqual(captured.records[0].getMessage(), "No ISO2 mapping for Wonderland in Pricing data found.")
        self.assertEqual(captured.records[1].getMessage(), "Not all entries of Pricing data could be correctly loaded!")
        for i in range(len(ISO2Mapper.country_name_to_ISO2_mapping)):
            self.assertEqual(captured.records[i+2].getMessage()[:-3],
                             "Loaded Pricing Data does not include Country, which is part of country name mapping:"
                             )

    def test_xxx_price_by_iso2(self):
        p = Pricing([{"country": "Germany", "netPrice": 0.22, "grossPrice": 0.3, "vat": 0.19, "currency": "EUR"}])
        self.assertEqual(p.net_price_by_iso2("DE"), Decimal("0.22"))
        self.assertEqual(p.gross_price_by_iso2("DE"), Decimal("0.3"))

        with self.assertLogs() as captured:
            self.assertTrue(p.net_price_by_iso2("GB").is_nan())
            self.assertTrue(p.gross_price_by_iso2("GB").is_nan())
        self.assertEqual(len(captured.records), 2)
        self.assertEqual(captured.records[0].getMessage(), "No Price Data for ISO2 Code: GB")
        self.assertEqual(captured.records[1].getMessage(), "No Price Data for ISO2 Code: GB")

        p.price_data = "Invalid"
        with self.assertLogs() as captured:
            self.assertTrue(p.net_price_by_iso2("GB").is_nan())
            self.assertTrue(p.gross_price_by_iso2("GB").is_nan())
        self.assertEqual(len(captured.records), 2)
        self.assertEqual(captured.records[0].getMessage(), "Price Data stored in Pricing is not a dictionary.")
        self.assertEqual(captured.records[1].getMessage(), "Price Data stored in Pricing is not a dictionary.")


    def test_message_xxx_price(self):
        from dt_sms_sdk.message import Message
        p = Pricing([{"country": "Germany", "netPrice": 0.22, "grossPrice": 0.3, "vat": 0.19, "currency": "EUR"}])
        m = Message("+491755555555", "+491755555556",
                    "👇👇👇👇👇" +  # 010
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
                    "👇👇1"  # 135
                    # will become 3 Messages
                    )
        self.assertEqual(p.message_net_price(m), Decimal("0.66"))
        self.assertEqual(p.message_gross_price(m), Decimal("0.9"))

        # GB Number
        m = Message("+441755555555", "+441755555556",
                    "👇👇👇👇👇" +  # 010
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
                    "👇👇1"  # 135
                    # will become 3 Messages
                    )
        with self.assertLogs() as captured:
            self.assertTrue(p.message_net_price(m).is_nan())
            self.assertTrue(p.message_gross_price(m).is_nan())
        self.assertEqual(len(captured.records), 2)
        self.assertEqual(captured.records[0].getMessage(), "No Price Data for ISO2 Code: GB")
        self.assertEqual(captured.records[1].getMessage(), "No Price Data for ISO2 Code: GB")

        p.price_data = "Invalid"
        with self.assertLogs() as captured:
            self.assertTrue(p.message_net_price(m).is_nan())
            self.assertTrue(p.message_gross_price(m).is_nan())
        self.assertEqual(len(captured.records), 2)
        self.assertEqual(captured.records[0].getMessage(), "Price Data stored in Pricing is not a dictionary.")
        self.assertEqual(captured.records[1].getMessage(), "Price Data stored in Pricing is not a dictionary.")

    def test_messages_gross_price(self):
        from dt_sms_sdk.message import Message
        p = Pricing([{"country": "Germany", "netPrice": 0.22, "grossPrice": 0.3, "vat": 0.19, "currency": "EUR"}])
        m = Message("+491755555555", "+491755555556",
                    "👇👇👇👇👇" +  # 010
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
                    "👇👇1"  # 135
                    # will become 3 Messages
                    )
        n = Message("+441755555555", "+441755555556",
                    "👇👇👇👇👇" +  # 010
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
                    "👇👇1"  # 135
                    # will become 3 Messages
                    )

        self.assertEqual(p.messages_net_price([m, m, m]), Decimal("0.66") * 3)
        self.assertEqual(p.messages_net_price([m, m, "Something"]), Decimal("0.66") * 2)
        self.assertEqual(p.messages_net_price([m, n, m]), Decimal("0.66") * 2)
        self.assertEqual(p.messages_net_price([m, n, n]), Decimal("0.66"))
        self.assertEqual(p.messages_net_price([n, n, n]), Decimal("0"))
        self.assertEqual(p.messages_net_price([]), Decimal("0"))
        self.assertEqual(p.messages_net_price(None), Decimal("0"))

        self.assertEqual(p.messages_gross_price([m, m, m]), Decimal("0.9") * 3)
        self.assertEqual(p.messages_gross_price([m, m, "Something"]), Decimal("0.9") * 2)
        self.assertEqual(p.messages_gross_price([m, n, m]), Decimal("0.9") * 2)
        self.assertEqual(p.messages_gross_price([m, n, n]), Decimal("0.9"))
        self.assertEqual(p.messages_gross_price([n, n, n]), Decimal("0"))
        self.assertEqual(p.messages_gross_price([]), Decimal("0"))
        self.assertEqual(p.messages_gross_price(None), Decimal("0"))

        self.assertEqual(p.messages_net_price([m, m, m], True), Decimal("0.66") * 3)
        self.assertTrue(p.messages_net_price([m, m, "Someting"], True).is_nan())
        self.assertTrue(p.messages_net_price([m, n, m], True).is_nan())
        self.assertTrue(p.messages_net_price([m, n, n], True).is_nan())
        self.assertTrue(p.messages_net_price([n, n, n], True).is_nan())
        self.assertEqual(p.messages_net_price([], True), Decimal("0"))
        self.assertEqual(p.messages_net_price(None, True), Decimal("0"))

        self.assertEqual(p.messages_gross_price([m, m, m], True), Decimal("0.9") * 3)
        self.assertTrue(p.messages_gross_price([m, m, "Someting"], True).is_nan())
        self.assertTrue(p.messages_gross_price([m, n, m], True).is_nan())
        self.assertTrue(p.messages_gross_price([m, n, n], True).is_nan())
        self.assertTrue(p.messages_gross_price([n, n, n], True).is_nan())
        self.assertEqual(p.messages_gross_price([], True), Decimal("0"))
        self.assertEqual(p.messages_gross_price(None, True), Decimal("0"))
