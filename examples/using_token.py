from dt_sms_sdk import SenderNumberNotVerifiedError, NotEnoughMoneyOnTheWalletError, SMSAPIError, InternalSMSAPIError, \
    SMSAPINotReachableError, NotAuthorizedError, NoRouteToRecipientNumberError, SMSAPIClient
from dt_sms_sdk.pricing import Pricing
from dt_sms_sdk.message import Message

API_TOKEN = ""
SENDER_PHONENUMBER = ""

print("This is a demo to sent yourself a quick SMS using the Deutsche Telekom SMS API with the Unofficial Python-SDK")

if not API_TOKEN or not SENDER_PHONENUMBER:
    print("Please set up the API_TOKEN and SENDER_PHONENUMBER variable with your values from the DT developer portal.")
    quit()

print(f'You have entered {SENDER_PHONENUMBER}, which will be used for sending (sender and receiver).')

prices = Pricing.download()
if prices:
    print('Online price list was downloaded successfull.')
else:
    print('Online price list could not be downloaded - offline default price list will be used.')

pricing = Pricing(prices)

try:
    message = Message(SENDER_PHONENUMBER, SENDER_PHONENUMBER, "My first SMS")
except ValueError:
    print("We could not set the receiver number because it can't be transfered to E164 format.")
    quit()

try:
    cost = pricing.message_gross_price(message)
except ValueError:
    print('The receiver number could not be evaluated for an ISO2 code')
    quit()

if cost.is_nan():
    print('The cost for sending the message to the receiver number could not be evaluated.')
else:
    print(f'The cost for Sending a single SMS to your number is {cost} €.')


print("Do you really want to sent the SMS? Type 'yes' and press [enter].")

if input().lower() != 'yes':
    print("Ok, no SMS will be send")
    quit()

sms_client = SMSAPIClient(api_key=API_TOKEN)

try:
    response = sms_client.send(message=message)
except NoRouteToRecipientNumberError:
    # this is a hypothetical path, because in the example we use a registered phone number
    # which was verified by the portal via an SMS
    # but if you make your own input for the receiver number, this path becomes important.
    print('Receiver number not valid for sending your SMS.')
    quit()
except SenderNumberNotVerifiedError:
    # this is a hypothetical path, because in the example we use the registered phone number
    # but if you make your own input for the receiver number, this path becomes important.
    print('Sender number not valid for sending your SMS.')
    quit()
except NotEnoughMoneyOnTheWalletError:
    # we checked the wallet above, but it could already be used in parallel!
    print('The wallet did not cover the sending cost - either prices have riced or balance has been used in parallel.')
    quit()
except (SMSAPIError, InternalSMSAPIError, SMSAPINotReachableError):
    print('The SMS API was not either reachable or terminated with an error.')
    quit()
except NotAuthorizedError:
    print("The token (gained by the login) is not accepted by the DT Developer Portal to send the SMS.")
    quit()

print(f'SMS has been transmitted to the API with version {response.api_version} successfully at {response.date_created}:')
print(f' SID: "{response.sid}"')
print(f' Message: "{response.message}"')
print(f' Number of Message Segments: {response.num_segments}')
print(f' Status: {response.status.value}')

print("Good bye.")
