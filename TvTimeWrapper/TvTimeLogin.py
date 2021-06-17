from Users.UsersManager import TvTimeUser
from typing import Dict

from bs4 import BeautifulSoup
from TvTimeWrapper import TvTimeUtils as Utils


def Login(user: TvTimeUser) -> bool:
    # Get symfony cookie
    resp_login = Utils.get('https://www.tvtime.com/login', False)
    symfony_cookie = resp_login.cookies['symfony']

    # Try to login
    post_data = {'symfony': symfony_cookie, 'username': user.Username, 'password': user.Password}
    resp_signin = Utils.post('https://www.tvtime.com/signin', post_data, False)

    # Check login answer
    if len(resp_signin.history) == 0 or 'symfony' not in resp_signin.history[0].cookies or 'tvstRemember' not in \
            resp_signin.history[0].cookies:
        return

    # Get user id
    parser = BeautifulSoup(resp_signin.text, 'html.parser')
    user_id = parser.select_one('li.profile > a[href*="user/"]')['href'].split('/')[3]
    if len(user_id) > 0:
        user.Authorisation = {'symfony': resp_signin.history[0].cookies['symfony'],
                            'tvstRemember': resp_signin.history[0].cookies['tvstRemember'],
                            'user_id': user_id}
