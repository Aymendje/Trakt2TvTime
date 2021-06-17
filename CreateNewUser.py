from trakt import TraktClient
import stdiomask
import six
from Users import UsersManager

def ManualTraktLogin(ClientId, ClientSecret):
    TraktClientWrapper = TraktClient()
    TraktClientWrapper.configuration.defaults.client(
        ClientId, ClientSecret)

    print('Navigate to: %s' % TraktClientWrapper['oauth'].authorize_url('urn:ietf:wg:oauth:2.0:oob'))

    code = six.moves.input('Authorization code : ')
    if not code:
        return None

    authorization = TraktClientWrapper['oauth'].token_exchange(code, 'urn:ietf:wg:oauth:2.0:oob')
    if not authorization:
        return None

    TraktClientWrapper.configuration.defaults.oauth.from_response(authorization)
    return authorization


print("=== Welcoem to the user creation wizard ===")
masterUsername = six.moves.input('Please choose a profile name : ')

print("")
print("")

print("=== Creating TvTime profile ===")
print("___ Note that we do not support Facebook or Google login for now, only username/email ___")
print("___ you can add a username/password to your account in the settings, or by emailing support ___")
tvTimeLogin = six.moves.input('TvTime username (or email) : ')
tvTimePassword = stdiomask.getpass('TvTime password : ')


print("")
print("")

print("=== Creating Trakt profile ===")
traktClient = six.moves.input('Trakt ClientId : ')
traktSecret = stdiomask.getpass('Trakt ClientSecret : ')
traktAuthorisation = ManualTraktLogin(traktClient, traktSecret)
if traktAuthorisation == None:
    print("Failed to authenticate to trakt. Please make sure the API ClientId and ClientSecret are correct.")
    print("For more information on how to create an API key : https://trakt.tv/oauth/applications")


newUser = UsersManager.User(
    masterUsername,
    UsersManager.TraktUser(
        traktClient,
        traktSecret,
        traktAuthorisation),
    UsersManager.TvTimeUser(
        tvTimeLogin,
        tvTimePassword),
    0)

UsersManager.WriteConfig(newUser)