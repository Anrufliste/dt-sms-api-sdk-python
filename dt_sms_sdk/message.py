from math import ceil
from typing import Union

from dt_sms_sdk.phone_number import E164PhoneNumber

import logging
logger = logging.getLogger(__name__)

# Reference: http://www.unicode.org/Public/MAPPINGS/ETSI/GSM0338.TXT
GSM_CHAR_FULL_SET = {
    "\u0000",
    "\u000A", "\u000C", "\u000D",
    "\u0020", "\u0021", "\u0022", "\u0023", "\u0024", "\u0025", "\u0026", "\u0027",
    "\u0028", "\u0029", "\u002A", "\u002B", "\u002C", "\u002D", "\u002E", "\u002F",
    "\u0030", "\u0031", "\u0032", "\u0033", "\u0034", "\u0035", "\u0036", "\u0037",
    "\u0038", "\u0039", "\u003A", "\u003B", "\u003C", "\u003D", "\u003E", "\u003F",
    "\u0040", "\u0041", "\u0042", "\u0043", "\u0044", "\u0045", "\u0046", "\u0047",
    "\u0048", "\u0049", "\u004A", "\u004B", "\u004C", "\u004D", "\u004E", "\u004F",
    "\u0050", "\u0051", "\u0052", "\u0053", "\u0054", "\u0055", "\u0056", "\u0057",
    "\u0058", "\u0059", "\u005A", "\u005B", "\u005C", "\u005D", "\u005E", "\u005F",
    "\u0061", "\u0062", "\u0063", "\u0064", "\u0065", "\u0066", "\u0067",
    "\u0068", "\u0069", "\u006A", "\u006B", "\u006C", "\u006D", "\u006E", "\u006F",
    "\u0070", "\u0071", "\u0072", "\u0073", "\u0074", "\u0075", "\u0076", "\u0077",
    "\u0078", "\u0079", "\u007A", "\u007B", "\u007C", "\u007D", "\u007E",
    "\u00A0", "\u00A1", "\u00A3", "\u00A4", "\u00A5", "\u00A7",
    "\u00BF",
    "\u00C4", "\u00C5", "\u00C6", "\u00C7",
    "\u00C9",
    "\u00D1", "\u00D6",
    "\u00D8", "\u00DC", "\u00DF",
    "\u00E0", "\u00E4", "\u00E5", "\u00E6", "\u00E7",
    "\u00E8", "\u00E9", "\u00EC",
    "\u00F1", "\u00F2", "\u00F6",
    "\u00F8", "\u00F9", "\u00FC",
    "\u0391", "\u0392", "\u0393", "\u0394", "\u0395", "\u0396", "\u0397",
    "\u0398", "\u0399", "\u039A", "\u039B", "\u039C", "\u039D", "\u039E", "\u039F",
    "\u03A0", "\u03A1", "\u03A3", "\u03A4", "\u03A5", "\u03A6", "\u03A7",
    "\u03A8", "\u03A9",
    "\u20AC"
}

# removed one option from double mapping which is not supported by API
# checked on 23rd December 2022 / Version 1.1.5
GSM_CHAR_SET = GSM_CHAR_FULL_SET - {
    "\u00E7",  # is treated as non GSM
    # "\u00C7",  # is treated as GSM
    #
    # "\u0041",  # is treated as GSM
    "\u0391",  # is treated as non GSM
    #
    # "\u0042",  # is treated as GSM
    "\u0392",  # is treated as non GSM
    #
    # "\u0045",  # is treated as GSM
    "\u0395",  # is treated as non GSM
    #
    # "\u0048",  # is treated as GSM
    "\u0397",  # is treated as non GSM
    #
    # "\u0049",  # is treated as GSM
    "\u0399",  # is treated as non GSM
    #
    # "\u004B",  # is treated as GSM
    "\u039A",  # is treated as non GSM
    #
    # "\u004D", # is treated as GSM
    "\u039C",  # is treated as non GSM
    #
    # "\u004E", # is treated as GSM
    "\u039D",  # is treated as non GSM
    #
    # "\u004F", # is treated as GSM
    "\u039F",  # is treated as non GSM
    #
    # "\u0050", # is treated as GSM
    "\u03A1",  # is treated as non GSM
    #
    # "\u0054", # is treated as GSM
    "\u03A4",  # is treated as non GSM
    #
    # "\u0058", # is treated as GSM
    "\u03A7",  # is treated as non GSM
    #
    # "\u0059", # is treated as GSM
    "\u03A5",  # is treated as non GSM
    #
    # "\u005A", # is treated as GSM
    "\u0396"  # is treated as non GSM
}


class Message(object):
    """
    A class representing an SMS message to be sent over the DT SMS API


    sender: Union[E164PhoneNumber, str]
        The line sending the SMS
    recipient: E164PhoneNumber
        The line the SMS should be sent to
    body: str
        The text which should be transmitted by the SMS

    Methods
    -------
    number_of_segments -> int
        Returns the number of SMS the Message body has to be split

    gsm_split_count(body: str) -> int
        Returns the number of SMS the string has to be split
    is_gsm_char_set(body: str) -> bool:
        Returns if the string is using only GSM character set as implemented on the API
    """

    sender: Union[E164PhoneNumber, str]
    recipient: E164PhoneNumber
    body: str

    def __init__(self, sender: Union[E164PhoneNumber, str, int], recipient: Union[E164PhoneNumber, str, int], body: str):
        """
        Parameters
        ----------
        sender : Union[E164PhoneNumber, str, int]
            Specified Sender of the SMS, if str is given in E164 notation, it will be stored as E164PhoneNumber
            otherwise str is keept
        recipient : Union[E164PhoneNumber, str, int]
            Receiver of the SMS - might also be given as a str (in E164 notation) or an int,
            which will be automatically transferred to an E164PhoneNumber object, if it can't an Error is raised
        body : str
            The message which should be sent

        Returns
        -------
        Message
            A Message object holding provided data.

        Raises
        ------
        ValueError
            if _to can't be transferred to an E164PhoneNumber
        """
        if isinstance(sender, E164PhoneNumber):
            self.sender = sender
        elif isinstance(sender, str):
            if E164PhoneNumber.basic_number_value_validation(sender):
                logger.debug(f'Message: {sender} is transferred from str to E164PhoneNumber without complex validation.')
                self.sender = E164PhoneNumber(number=sender)
            else:
                logger.debug(f'Message: {sender} is NOT transferred from str to E164PhoneNumber, '
                             f'because basic_number_value_validation failed on it.')
                self.sender = sender
        elif isinstance(sender, int):
            logger.debug(f'Message: {sender} is transferred from int to E164PhoneNumber without complex validation.')
            self.sender = E164PhoneNumber(number=f'+{sender}')

        if isinstance(recipient, E164PhoneNumber):
            self.recipient = recipient
        elif isinstance(recipient, str):
            logger.debug(f'Message: {recipient} is transferred from str to E164PhoneNumber without complex validation.')
            self.recipient = E164PhoneNumber(number=recipient)
        elif isinstance(recipient, int):
            logger.debug(f'Message: {recipient} is transferred from int to E164PhoneNumber without complex validation.')
            self.recipient = E164PhoneNumber(number=f'+{recipient}')
        else:
            logger.error(f'Message: {recipient} is not a datatype, '
                         f'which could be transferred into an E164PhoneNumber object.')
            raise ValueError('Receiver of message is given not a usable value for an E164PhoneNumber.')
        self.body = body

    def number_of_segments(self) -> int:
        """
        Returns the number of segments the body of the Message has to be split

        Returns
        -------
        int
            how many SMS the message text will be split
        """
        return Message.gsm_split_count(self.body)

    @staticmethod
    def is_gsm_char_set(body: str) -> bool:
        """
        Returns if the string is using only GSM character set as implemented on the API

        Parameters
        ----------
        body: str
            representing the message text

        Returns
        -------
        bool
            is true if all characters of the string are from GSM character set
        """
        used_chars = list(body)
        return set(used_chars).issubset(GSM_CHAR_SET)

    @staticmethod
    def _len_non_gsm_char(c) -> int:
        """
        Returns the length of a character if treated as non GSM character set

        Parameters
        ----------
        c
            a character to be checked its length in an SMS

        Returns
        -------
        int
            how many character slots that character would need using non GSM character set
        """
        return 2 if ord(c) > 65535 else 1

    @staticmethod
    def _len_non_gsm_str(s: str) -> int:
        """
        Returns the length of the string if its characters are treated as non GSM character set

        Parameters
        ----------
        s: str
            representing the message text

        Returns
        -------
        int
            how many characters the message would need using non GSM character set
        """
        result = 0
        for c in s:
            result += Message._len_non_gsm_char(c)
        return result

    @staticmethod
    def gsm_split_count(body: str) -> int:
        """
        Returns the number of segments the string has to be split

        Parameters
        ----------
        body: str
            representing the complete message text

        Returns
        -------
        int
            how many SMS the str will be split
        """
        if not body:
            return 0

        if Message.is_gsm_char_set(body):
            single_message_limit = 160
            multi_message_limit = 153
            message_char_count = len(body)
        else:
            single_message_limit = 70
            multi_message_limit = 67
            message_char_count = Message._len_non_gsm_str(body)

        if message_char_count > single_message_limit:
            return ceil(message_char_count / multi_message_limit)
        else:
            return 1

    def data(self) -> dict:
        """
        Getting the Message object in the structure which the SMS API understands.

        Returns
        -------
        dict
            A dict with the keys for the Message object attributes how they are used on the API

        """
        return {
            'From': str(self.sender),
            'To': str(self.recipient),
            'Body': str(self.body)
        }
