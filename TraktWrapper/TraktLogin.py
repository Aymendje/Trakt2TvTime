from Users.UsersManager import TraktUser
from trakt import TraktClient
import logging

def Login(traktUser : TraktUser):
    traktUser.TraktClientWrapper = TraktClient()
    traktUser.TraktClientWrapper.configuration.defaults.client(
        traktUser.ClientId, traktUser.ClientSecret)
    oath = traktUser.TraktClientWrapper.configuration.defaults.oauth.from_response(
        authenticate(traktUser.Authorisation), refresh=True)
    if(oath != None and oath.data["oauth.token"] != None):
        traktUser.Authorisation["access_token"] = oath.data["oauth.token"]
        traktUser.Authorisation["refresh_token"] = oath.data["oauth.refresh_token"]
        traktUser.Authorisation["created_at"] = oath.data["oauth.created_at"]
        traktUser.Authorisation["expires_in"] = oath.data["oauth.expires_in"]

def authenticate(authorization):
    if authorization:
        return authorization
    else:
        logging.error("Failed to authenticte to trakt. Pleease try to use the ManualUserCreation.py script to recreate the user")
        return None
