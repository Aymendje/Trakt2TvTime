# Trakt2TvTime
 Periodically sync Tract shows to TvTime


## Purpose

This project's goal is tu help automatically sync your Trakt.tv Tv Show (no support for moveis yet) into your TvTime account.  

## Requirements

* You need python 3.9+ for this project to run
* Works on both Windows and Linux
* You need a username/password account (not Facebook) for TvTime. You can either create a new one or request a password enabled account via their support
* You need to create an API on [Trakt.tv](https://trakt.tv/oauth/applications). Mandatory fields are ``Name``, ``Description`` and set `Redirect uri` to  `urn:ietf:wg:oauth:2.0:oob`. The rest can stay empty.

## Usage

* You will need to install all the python dependancy first  
  Depending on your OS and python, something like :

```
python3.9 -m pip install -r requirements.txt
```

* You will need to provide your credentials to create a profile.  
  Simply run the python command and follow the scripts inputs
```
python3.9 CreateNewUser.py
```
**_NOTE:_**  The credentials are *NOT* encrypted. Please make sure your machine is secure

* Now to do a sync, simply run 
```
python3.9 main.py
```

# Configuration Details
In the ``Users`` folder, there are the profiles you will load.
Here is an example :
```
{
    "lastSync": 0,
    "trakt": {
        "Authorisation": {
            "access_token": "",
            "created_at": 0,
            "expires_in": 0,
            "refresh_token": "",
            "scope": "",
            "token_type": ""
        },
        "ClientId": "",
        "ClientSecret": ""
    },
    "tvtime": {
        "Password": "",
        "Username": ""
    }
}
```
* _lastSync_ : The unix timestamp of the last successfull script sync run. This way, we only need to sync the shows after that value
** Note that this value is always successfullTime - 24h, so shows that got synced with a delay might still get synced to TvTime properly (ex: if you are using a Plex scrobber to sync with Trakt, Plex have a delay with the Trakt sync, but will push the real watch time, meaning it could tell Trakt at 6 PM that you watched a show at 4 PM)
* _trakt.Authorisation_ : This is automatically generated and you should not need to edit that. It is an oauth token derived from your API + Authorisation code
* _trakt.ClientId_ : Api public ClientId
* _trakt.ClientId_ : Api secret ClientSecret
* _tvtime.Username_ : Username to access TvTime
* _tvtime.Password_ : Password to access TvTime

# Debug
For debugging, you need to enable detailed logs.
For that, in the main, change `DETAILED_LOG = false` to `DETAILED_LOG = true` in the `main.py` file.  

# Final note
* This is only a hobby project and is in no way secure, complete or even reliable.
* I personally use it everyday on an hourly cron task, and it works for _most_ of my shows.
* If you have any issue, you can always create an issue on github, and provide detailed logs and username for Trakt and TvTime, and I will try to help on my spare time
* The code is a huge mess, I tried multiple methods to get the episode details and didnt always clean properly the previous tries, but all contributions are appreciated and encouraged !