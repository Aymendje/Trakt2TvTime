from UsersManager import TvTimeUser
from typing import Dict, List, Any
import logging
from bs4 import BeautifulSoup
from TvTimeWrapper import TvTimeUtils as Utils


def GetAllStartedShows(user : TvTimeUser) -> Dict[str, any]:
    resp = Utils.get('https://www.tvtime.com/en/user/{}/profile'.format(user.Authorisation['user_id']),
                     user=user)
    series = parse_series_list(resp.text)
    return series


def parse_series_list(shows_page: str) -> List[any]:
    parser = BeautifulSoup(shows_page, 'html.parser')
    series = list()
    for element in parser.select('div#all-shows ul.shows-list.posters-list div.show'):
        show_name = element.select_one('div.poster-details > h2 > a').text.strip()
        if show_name == '':
            continue
        show_id = element.select_one('a.show-link')['href'].split('/')[3]
        progress = element.select_one('a.show-link div.progress-bar')['style'].split(':')[1].strip()
        time = element.select_one('div.poster-details > h3').text.strip()
        show = {'id': int(show_id), 'progress': progress, 'name': show_name, 'time': time}
        series.append(show)
        logging.debug("TvTime - Parsing show on deck : {0}".format(show))
    return series

def GetAllEpisodesFromShows(show_ids : set[int], user : TvTimeUser) -> set[int]:
    episodes = []
    logging.info("Scanning {0} shows from TvTime".format(len(show_ids)))
    i = 0
    for show_id in show_ids:
        try:
            i += 1
            url = 'https://www.tvtime.com/en/show/{}'.format(show_id)
            logging.info("{0} / {1} : Getting url {2}".format(i, len(show_ids), url))
            resp = Utils.get(url, user=user)
            seasons = parse_season_list(resp.text)
            for season in seasons:
                for episode in season["episodes"]:
                    logging.debug("TvTime - Parsing episode {0}".format(episode))
                    episodeNb = (int(episode["id"]), episode["watched"])
                    episodes.append(episodeNb)
        except Exception as err:
            logging.error("Exception : {0}".format(err), exc_info=True)
    return episodes

def MarkAsWatched(id : int, user : TvTimeUser) -> set[int]:
    try:
        Utils.put("https://www.tvtime.com/watched_episodes", data={"episode_id" : id}, user=user)
    except Exception as err:
        logging.error("Failed to mark episode {0} as watched due to Exception:{1}".format(id, err), exc_info=True)

def parse_season_list(show_page: str) -> List[Any]:
    parser = BeautifulSoup(show_page, 'html.parser')
    seasons = list()
    for season_element in parser.select("div#show-seasons > div.seasons > div.season-content"):
        season_name = season_element.select_one("span[itemprop='name']").text.strip()
        num_episodes = season_element.select_one("span[itemprop='numberOfEpisodes']").text.strip()
        episodes = list()
        for episode_element in season_element.select("ul.episode-list > li.episode-wrapper > div.infos > div.row"):
            episode_id = episode_element.select_one('a')['href'].split('/')[5]
            episode_number = episode_element.select_one('span.episode-nb-label').text.strip()
            episode_name = episode_element.select_one('span.episode-name').text.strip()
            episode_air_date = episode_element.select_one('span.episode-air-date').text.strip()
            watched = 'active' in episode_element.parent.parent.select_one('div.actions > div.row > a')['class']
            episodes.append(
                {"id": episode_id, "number": episode_number, "name": episode_name, "air_date": episode_air_date,
                "watched": watched})
        if(len(episodes) > 0):
            seasons.append({"name": season_name, "number_of_episodes": num_episodes, "episodes": episodes})
    return seasons

"""
def GetEpisodeKeyFromTvTimes(showkey : int, seasonNb : int, episodeNb : int, user : TvTimeUser) -> int:
    url = 'https://www.tvtime.com/en/show/{}'.format(showkey)
    logging.info("Getting url {0} for Season {1} Episode {2}".format(url, seasonNb, episodeNb))
    resp = Utils.get(url, user=user)
    parser = BeautifulSoup(resp.text, 'html.parser')
    element = parser.select_one('div#season{0}-content'.format(seasonNb))
    for episode in element.select('li'):
        if episode.select_one('span.episode-nb-label').text.strip() == str(episodeNb):
            ret = episode.get('id').strip()
            return int(ret.split("-")[-1])
    return None
"""