from Users.UsersManager import TraktUser
from trakt import TraktClient
import logging

def Login(traktUser : TraktUser):
    traktUser.TraktClientWrapper = TraktClient()
    traktUser.TraktClientWrapper.configuration.defaults.client(
        traktUser.ClientId, traktUser.ClientSecret)
    traktUser.TraktClientWrapper.configuration.defaults.oauth.from_response(
        authenticate(traktUser.Authorisation), refresh=True)

def authenticate(authorization):
    if authorization:
        return authorization
    else:
        logging.error("Failed to authenticte to trakt. Pleease try to use the ManualUserCreation.py script to recreate the user")
        return None
