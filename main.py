import time, datetime, logging, sys
from logging import handlers
from Users import UsersManager
from TvTimeWrapper import TvTimeLogin
from TvTimeWrapper import TvTimeShows
from TraktWrapper import TraktLogin
from TraktWrapper import TraktShows

DETAILED_LOG = True
DETAILED_LOG = False

log = logging.getLogger('')
log.setLevel(logging.INFO)
format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(format)
log.addHandler(ch)

if DETAILED_LOG == True:
    log.setLevel(logging.DEBUG)
    fh = handlers.RotatingFileHandler("Trakt2TvTime-{}.log".format(datetime.datetime.now().strftime("%Y%m%d-%H%M%S")))
    fh.setFormatter(format)
    log.addHandler(fh)

allUsers = UsersManager.ReadAllConfig()

for user in allUsers:
    try:
        logging.info("Processing user {0} ".format(user.plexUsername))
        TraktLogin.Login(user.trakt)
        TvTimeLogin.Login(user.tvtime)
        currentTime = int(time.time())
        logging.debug("Main - currentTime = {0}".format(currentTime))
        traktEpisodes = TraktShows.GetAllWatchedEpisodes(user.trakt.TraktClientWrapper, user.lastSync, tvTimeUser = user.tvtime)
        logging.debug("Main - traktEpisodes = {0}".format(traktEpisodes))

        allShowsOnDeckTvTime = TvTimeShows.GetAllStartedShows(user.tvtime)
        logging.debug("Main - tvTime allShowsOnDeckTvTime = {0}".format(allShowsOnDeckTvTime))
        allCompletedShows = set([x["id"] for x in allShowsOnDeckTvTime if int(x["progress"].strip('%').split('.')[0]) >= 100])
        logging.debug("Main - tvTime allCompletedShows = {0}".format(allCompletedShows))
        traktEpisodes = {key:val for key, val in traktEpisodes.items() if val not in allCompletedShows}

        tvTimeAllEpisodes = TvTimeShows.GetAllEpisodesFromShows(set(traktEpisodes.values()), user.tvtime)
        tvTimeWatchedEpisodes = set([x[0] for x in tvTimeAllEpisodes if x[1] == True])
        logging.debug("Main - tvTimeWatchedEpisodes = {0}".format(tvTimeWatchedEpisodes))
        logging.debug("Main - traktEpisodes = {0}".format(traktEpisodes.keys()))
        missingEpisodesFromTvTime = set(traktEpisodes.keys()) - tvTimeWatchedEpisodes
        scrubbedMissingEpisodesFromTvTime = missingEpisodesFromTvTime.intersection(set([x[0] for x in tvTimeAllEpisodes]))
        logging.debug("Main - scrubbedMissingEpisodesFromTvTime = {0}".format(scrubbedMissingEpisodesFromTvTime))
        i = 0
        for id in scrubbedMissingEpisodesFromTvTime:
            i += 1
            logging.info("{0}\t{1} / {2} : Marking as watched https://www.tvtime.com/en/show/{3}/episode/{4}".format(user.plexUsername, i, len(scrubbedMissingEpisodesFromTvTime), traktEpisodes[id], id ))
            TvTimeShows.MarkAsWatched(id, user.tvtime)
        user.lastSync = currentTime - 24 * 3600 # In case stuff didnt sync properly, we have a 24h backoff
        logging.info("New time {0} for user {1} ".format(user.lastSync, user.plexUsername))
        UsersManager.WriteConfig(user)
    except Exception as err:
        logging.error("Exception : {0}".format(err), exc_info=True)
