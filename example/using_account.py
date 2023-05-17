from dt_sms_sdk import SenderNumberNotVerifiedError, NotEnoughMoneyOnTheWalletError, SMSAPIError, InternalSMSAPIError, \
    SMSAPINotReachableError, NotAuthorizedError, NoRouteToRecipientNumberError
from dt_sms_sdk.account import Account, DashboardNotReachableError, LoginError, DashboardError, TokenError
from dt_sms_sdk.pricing import Pricing
from dt_sms_sdk.message import Message

ACCOUNT_USER_NAME = ""
ACCOUNT_USER_PASSWORD = ""

print("This is a demo to sent yourself a quick SMS using the Deutsche Telekom SMS API with the Unofficial Python-SDK")

if not ACCOUNT_USER_NAME or not ACCOUNT_USER_PASSWORD:
    print("Please set up the ACCOUNT_USER_xxx variables with your account credentials for the DT developer portal.")
    quit()

try:
    account = Account(ACCOUNT_USER_NAME, ACCOUNT_USER_PASSWORD)
except (DashboardNotReachableError, DashboardError):
    print("While doing a login the DT Developer Portal is currently not reachable or has changed their URL.")
    quit()
except LoginError:
    print("The provided login is not accepted by the DT Developer Portal.")
    quit()

print("Login successfully!")

try:
    wallet = account.wallet()
except (DashboardNotReachableError, DashboardError):
    print("While reading the wallet the DT Developer Portal is currently not reachable or has changed their URL.")
    quit()
except TokenError:
    print("The token (gained by the login) is not accepted by the DT Developer Portal to read the wallet.")
    quit()

if wallet.balance == 0:
    print('Your wallet is currently empty. Please recharge before restarting.')
    quit()
print(f'Your current balance is {wallet.balance} {wallet.currency.value}.')

try:
    phone_numbers = account.phone_numbers_for_sms_sender()
except (DashboardNotReachableError, DashboardError):
    print("While reading the registered phonenumbers the DT Developer Portal is currently not reachable or has "
          "changed their URL.")
    quit()
except TokenError:
    print("The token (gained by the login) is not accepted by the DT Developer Portal to read the phonenumbers.")
    quit()

if len(phone_numbers) == 0:
    print("You do not have registered a phonenumber to send an SMS, please register a phonenumber before restarting.")
    quit()
print(f'You have {len(phone_numbers)} registered and your first one {phone_numbers[0]} will be used for sending'
      f' (sender and receiver).')


prices = Pricing.download()
if prices:
    print('Online price list was downloaded successfull.')
else:
    print('Online price list could not be downloaded - offline default price list will be used.')

pricing = Pricing(prices)

try:
    message = Message(phone_numbers[0], phone_numbers[0], "My first SMS")
except ValueError:
    # this is a hypothetical path, because in the example we use the registered phone number, which is given in E164.
    # but if you make your own input for the receiver number, this path becomes important.
    print("We could not set the receiver number because it can't be transfered to E164 format.")
    quit()

try:
    cost = pricing.message_gross_price(message)
except ValueError:
    # this is a hypothetical path, because in the example we use the registered phone number, which is given in E164.
    # but if you make your own input for the receiver number, this path becomes important.
    print('The receiver number could not be evaluated for an ISO2 code')
    quit()

if cost.is_nan():
    print('The cost for sending the message to the receiver number could not be evaluated.')
    quit()

# TODO: A SDK Message for getting the currency would be nice
# TODO: In the price sum up, we should specify a currency which is summed up
#  (or if different ignored / aboarded based on all_or_none)
# Currently only Euro is supported by the portal - so its save for now:
print(f'The cost for Sending a single SMS to your number is {cost} €.')

if cost > wallet.balance:
    print("Your wallet does not cover the cost for sending the SMS. Please recharge before restarting.")
    quit()

print("Do you really want to sent the SMS? Type 'yes' and press [enter].")

if input().lower() != 'yes':
    print("Ok, no SMS will be send")
    quit()

try:
    sms_client = account.sms_api_client()
except (DashboardNotReachableError, DashboardError):
    print("While trying to send the SMS the DT Developer Portal is currently not reachable or has changed their URL.")
    quit()
except TokenError:
    print("The token (gained by the login) is not accepted by the DT Developer Portal to send the SMS.")
    quit()

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

