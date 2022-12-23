# dt-sms-api-sdk-python

This library is meant as an unofficial SDK (Software Development Kit) for the [Deutsche Telekom Developer SMS API](https://developer.telekom.com/products/sms-api/summary) and give Python developers a quick start to use it withing their code.

Please read the instructions on Deutsche Telekom Developer Portal and set our account there to get the needed credentials for using this SDK.

## SMS - (Short Message Service)

SMS is a base functionality in GSM conform mobile communication. While it was designed to send a short text message of 160 characters from one cellular to another it got some upgrades and special features. The most important you need to know for proper usage of the API is, that nowadays you can send longer text messages and even use special characters like Emojis. But internally that will be split into multiple SMS messages with reduced text capacity - and as a consumer of the API you will have to pay for each of those split part messages, even if in-front of the receiver it is presented just as one message.

### "num_segments"

So the important question for your balance is - how many part messages your account get billed for a message. If you want to understand the splitting you can (interactively) learn it on https://charactercounter.com/sms or use the following helper method:

```
from dt_sms_sdk.message import Message

Message.gsm_split_count("My message to be sent")  # will return 1 for this string
```