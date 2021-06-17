from UsersManager import TraktUser
from trakt import TraktClient

def Login(traktUser : TraktUser):
    traktUser.TraktClientWrapper = TraktClient()
    traktUser.TraktClientWrapper.configuration.defaults.client(
        traktUser.ClientId, traktUser.ClientSecret)
    traktUser.TraktClientWrapper.configuration.defaults.oauth.from_response(
        authenticate(traktUser.Authorisation))

def authenticate(authorization):
    if authorization:
        return authorization
    else:
        return None # or manualLogin(traktClient)

def manualLogin(traktClient):
    import six
    print('Navigate to: %s' % traktClient['oauth'].authorize_url('urn:ietf:wg:oauth:2.0:oob'))

    code = six.moves.input('Authorization code:')
    if not code:
        exit(1)

    authorization = traktClient['oauth'].token(code, 'urn:ietf:wg:oauth:2.0:oob')
    if not authorization:
        exit(1)

    print('Authorization: %r' % authorization)
    return authorization