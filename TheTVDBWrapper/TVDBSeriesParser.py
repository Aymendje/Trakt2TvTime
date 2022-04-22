from bs4 import BeautifulSoup
from time import sleep
from typing import Dict, List, Any
import requests, re, json
import logging


def get(url: str, throw : bool = False) -> requests.Response:
    try:
        resp = requests.get(url, cookies={ 'tvdb': "" })
        resp.raise_for_status()
        return resp
    except Exception as err:
        logging.error("Exception : {0}. Will throw : ".format(err, throw), exc_info=True)
        if throw:
            raise err
        sleep(4)
        return get(url=url,throw=True)

def _GetAllSeasonsLink(showId : int):
    url = "https://www.thetvdb.com/dereferrer/series/{}".format(showId)
    try:
        showPage = get(url).text
        parser = BeautifulSoup(showPage, 'html.parser')
        for element in parser.select('h4.list-group-item-heading'):
            for link in element.select('a'):
                if link.text.strip() == "All Seasons":
                    return link['href']
    except Exception as err:
        logging.error("URL : `{0}`. Exception : {1}. ".format(showId, err), exc_info=True)
    return None
    
def GetShowFromEpisodeId(episodeId : int):
    try:
        url = "https://api.thetvdb.com/episodes/{0}".format(episodeId)
        episodeInfo = get(url).text
        episodeInfo = json.loads(episodeInfo)["data"]
        showId = int(episodeInfo["seriesId"])
        logging.debug("Detected showId {0} for episode {1}".format(showId, episodeId))
        return showId
    except Exception as ex:
        logging.debug("Failed to find showId for episode {0} due to exception : {1}".format(episodeId, ex))
        return None


def GetAllEpisodes(showId : int):
    try:
        link = _GetAllSeasonsLink(showId)
        url = "https://www.thetvdb.com{}".format(link)
        showPage = get(url).text
        parser = BeautifulSoup(showPage, 'html.parser')
        episodes = {}
        for element in parser.select('h4.list-group-item-heading'):
            seasonEpisode = element.select_one('.episode-label').text.strip()
            link = element.select('a')[0]
            id = int(link["href"].split('/')[-1])
            #title = link.text.strip()
            seid = ParseSeasonEpisode(seasonEpisode)
            episodes[seid] = id
        return episodes
    except Exception as ex:
        logging.debug("Failed to find showId for episode {0} due to exception : {1}".format(episodeId, ex))
        return None

def ParseSeasonEpisode(seasonEpisode : str):
    try:
        result = re.match("S(\d+)E(\d+)", seasonEpisode)
        if result == None:
            result = re.match(".*(\d+)x(\d+)", seasonEpisode)
            if result == None:
                return seasonEpisode
        value = (int(result[1]), int(result[2]))
        logging.debug("Detected {0} as {1}".format(seasonEpisode, value))
        return value
    except Exception as err:
        logging.error("Failed to detect version for : {0} with error : {1}".format(seasonEpisode, err))
    return seasonEpisode
