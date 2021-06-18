import os, sys
import json
from typing import Any, List, NamedTuple
from trakt.client import TraktClient
from trakt.core.context_collection import ListCollection

class TraktUser:
    def __init__(self, ClientId: str, ClientSecret: str, Authorisation : dict ):
        self.ClientId = ClientId
        self.ClientSecret = ClientSecret
        self.Authorisation = Authorisation
        self.TraktClientWrapper = None
    def returnCleanDict(self):
        return {k: self.__dict__[k] for k in self.__dict__.keys() - {'TraktClientWrapper'}}
    def IsLoggedIn(self):
        return self.TraktClientWrapper == True

class TvTimeUser:
    def __init__(self, Username: str, Password: str):
        self.Username = Username
        self.Password = Password
        self.Authorisation = None
    def returnCleanDict(self):
        return {k: self.__dict__[k] for k in self.__dict__.keys() - {'Authorisation'}}
    def IsLoggedIn(self):
        return self.Authorisation == True

class User:
    def __init__(self, plexUsername: str, trakt : TraktUser, tvtime : TvTimeUser, lastSync : int = -1):
        self.plexUsername = plexUsername
        self.lastSync = lastSync
        self.trakt = trakt
        self.tvtime = tvtime
    def returnCleanDict(self):
        cleanDict = {k: self.__dict__[k] for k in self.__dict__.keys() - {'trakt', 'tvtime', 'plexUsername'}}
        cleanDict['trakt'] = self.trakt.returnCleanDict()
        cleanDict['tvtime'] = self.tvtime.returnCleanDict()
        return cleanDict

def ReadAllConfig(configFolderPath = os.path.join(sys.path[0], "users")) -> List[User]:
    allusers = []
    for entry in os.scandir(configFolderPath):
        if entry.path.endswith(".json") and entry.is_file():
            user = ReadSingleConfig(os.path.splitext(entry.name)[0], configFolderPath)
            if user:
                allusers.append(user)
    return allusers

def ReadSingleConfig(username, configFolderPath = os.path.join(sys.path[0], "Users")) -> User:
    filepath = os.path.join(configFolderPath, "{}.json".format(username))
    with open(filepath, 'r') as fp_config:
        user = json.load(fp_config)
        newUser = User(
            username,
            TraktUser(
                user["trakt"]["ClientId"],
                user["trakt"]["ClientSecret"],
                user["trakt"]["Authorisation"]),
            TvTimeUser(
                user["tvtime"]["Username"],
                user["tvtime"]["Password"]),
            user["lastSync"])
        if  newUser.plexUsername and \
            newUser.trakt.ClientId and \
            newUser.trakt.ClientSecret and \
            newUser.tvtime.Username and \
            newUser.tvtime.Password :
            return newUser
    return None

def WriteAllConfig(config : List[User], configPath = os.path.join(sys.path[0], "Users")):
    for user in config:
        WriteConfig(user, configPath)


def WriteConfig(user : User, configPath = os.path.join(sys.path[0], "Users")):
    userConfig = user.returnCleanDict()
    plexUsername = user.plexUsername
    filepath = os.path.join(configPath, "{}.json".format(plexUsername))
    with open(filepath, 'w') as fp_config:
        json.dump(userConfig, indent=4, sort_keys=True, default=str, fp=fp_config)
