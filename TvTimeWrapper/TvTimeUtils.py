from Users.UsersManager import TvTimeUser
from time import sleep
from typing import Dict, List, Any
import requests
import logging
from bs4 import BeautifulSoup
from TvTimeWrapper import TvTimeLogin

HEADERS={ 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36' }

def update_tvtime_cookies(auth: dict, cookies: Any) -> None:
    old_session_cookie = auth['symfony']
    old_remember_cookie = auth['tvstRemember']
    auth['symfony'] = cookies.get('symfony', old_session_cookie)
    auth['tvstRemember'] = cookies.get('tvstRemember', old_remember_cookie)

def get(url: str, update_session=True, user: TvTimeLogin = None, throw : bool = False) -> requests.Response:
    try:
        resp = requests.get(url, headers=HEADERS, cookies=user and user.Authorisation)
        ThrowOnError(resp, user, update_session)
        return resp
    except Exception as err:
        CheckForRetry(err, throw, user)
        return get(url=url, update_session=update_session, user=user, throw=True)


def post(url: str, data: Dict[str, Any], update_session=True, user: TvTimeLogin = None, throw : bool = False) -> requests.Response:
    try:
        resp = requests.post(url, data=data, headers=HEADERS, cookies=user and user.Authorisation)
        ThrowOnError(resp, user, update_session)
        return resp
    except Exception as err:
        CheckForRetry(err, throw, user)
        return post(url=url, data=data, update_session=update_session, user=user, throw=True)


def put(url: str, data: Dict[str, Any], update_session=True, user: TvTimeLogin = None, throw : bool = False) -> requests.Response:
    try:
        resp = requests.put(url, data=data, headers=HEADERS, cookies=user and user.Authorisation)
        ThrowOnError(resp, user, update_session)
        return resp
    except Exception as err:
        CheckForRetry(err, throw, user)
        return put(url=url, data=data, update_session=update_session, user=user, throw=True)


def delete(url: str, data: Dict[str, Any], update_session=True, user: TvTimeLogin = None, throw : bool = False) -> requests.Response:
    try:
        resp = requests.delete(url, data=data, headers=HEADERS, cookies=user and user.Authorisation)
        ThrowOnError(resp, user, update_session)
        return resp
    except Exception as err:
        CheckForRetry(err, throw, user)
        return delete(url=url, data=data, update_session=update_session, user=user, throw=True)

def ThrowOnError(resp: requests.Response, user: TvTimeUser, update_session : bool):
    resp.raise_for_status()
    if update_session:
        update_tvtime_cookies(user.Authorisation, resp.cookies)

def CheckForRetry(err: Exception, throw: bool, user: TvTimeUser ):
    logging.error("Exception : {0}. Will throw : ".format(err, throw), exc_info=True)
    if throw:
        raise err
    sleep(4.5)
    TvTimeLogin.Login(user)
    sleep(0.5)
