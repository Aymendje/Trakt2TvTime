from UsersManager import TvTimeUser
import datetime
import logging
from trakt import Trakt
from datetime import timezone
from TvTimeWrapper import TvTimeShows
from TheTVDBWrapper import TVDBSeriesParser

def GetAllWatchedEpisodes(client, lastSyncTime: int = 0, tvTimeUser: TvTimeUser = None):
    episodes = {}
    watched = client['sync/history'].shows(pagination=True, per_page=25)
    logging.info("Trakt total items to analyze : {0}".format(watched.total_items))
    i = 0
    problemsShows = {}
    problemsEpisodes = {}
    validEpisodes = set()
    for episode in watched:
        try:
            i += 1
            logging.debug("Trakt - Going through Episode : {0}, Show : {1}, Episode Key : {2}. Show Key : {3}".format(episode, episode.show, episode.keys, episode.show.keys))
            if i % 500 == 0:
                logging.info("Processing item {0} / {1}".format(i, watched.total_items))
            if episode.is_watched == False:
                logging.debug("Trakt - Skippign episode since not watched yet")
                continue
            watchTime = None
            if episode.last_watched_at:
                watchTime = episode.last_watched_at
            elif episode.watched_at:
                watchTime = episode.watched_at
            else:
                watchTime = datetime.datetime.now() 
            watchTimestamp = int(watchTime.replace(tzinfo=timezone.utc).timestamp())
            if(watchTimestamp <= lastSyncTime):
                logging.debug("Trakt - Skipping episode since last sync already included it")
                continue

            episodeId = [int(id) for (db, id) in episode.keys if str(db) == "tvdb"]
            if(len(episodeId) == 0):
                logging.debug("Unable to find tvdb id for Episode {0}".format(episode))
                problemsEpisodes[[int(id) for (db, id) in episode.keys if str(db) == "trakt"][0]] = episode
                continue
            episodeId = episodeId[0]
            showId = [int(id) for (db, id) in episode.show.keys if str(db) == "tvdb"]
            if(len(showId) == 0):
                showId = [TVDBSeriesParser.GetShowFromEpisodeId(episodeId)]
                if showId[0] == None:
                    logging.debug("Unable to find tvdb id for Episode {0}".format(episode))
                    problemsShows[[int(id) for (db, id) in episode.keys if str(db) == "trakt"][0]] = episode
                    continue
            showId = showId[0]
            logging.debug("Trakt - {0} Was recently watched, adding to episodes to watch later".format(episode))
            validEpisodes.add([int(id) for (db, id) in episode.keys if str(db) == "trakt"][0])
            episodes[episodeId] = showId
        except Exception as err:
            logging.error("Episode : {0}. Exception : {1}".format(episode, err), exc_info=True)
    
    recoverShowsIds = set()
    missingShowEpidosdePair = {}
    tvdbShows = {}
    for trakt, episode in problemsEpisodes.items():
        showId = None
        for db, id in episode.show.keys:
            if str(db) == "tvdb":
                showId = int(id)
                break
        if showId != None:
            recoverShowsIds.add(showId)
            if showId not in missingShowEpidosdePair:
                missingShowEpidosdePair[showId] = []
            missingShowEpidosdePair[showId].append((episode.pk, trakt))

    for showId in recoverShowsIds:
        tvdbShows[showId] = TVDBSeriesParser.GetAllEpisodes(showId)

    for showId, episodeIds in missingShowEpidosdePair.items():
        if showId in tvdbShows:
            for episodeId, traktKey in episodeIds: 
                if episodeId in tvdbShows[showId]:
                    episodes[tvdbShows[showId][episodeId]] = showId
                    del problemsEpisodes[traktKey]
    
    problems = len(problemsShows) + len(problemsEpisodes)
    if(problems > 0):
        logging.warning("Due to nonfatal errors, skipped {0} episodes. Mostly due to invalid tvdb id from trakt.".format(problems))
        for problem in problemsEpisodes:
            logging.warning("Skipped episode {0}.  Mostly due to invalid tvdb id from trakt.".format(problem))
        for problem in problemsShows:
            logging.warning("Skipped episode {0}.  Mostly due to invalid tvdb id from trakt.".format(problem))
    return episodes