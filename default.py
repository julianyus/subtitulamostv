
import os
import xbmcaddon
import xbmcgui
import xbmcplugin
import sys
import xbmc
import uuid
import xbmcvfs
import shutil

__addon__ = xbmcaddon.Addon()
__scriptid__   = __addon__.getAddonInfo('id')
__name__ = "subtitulamostv"
__cwd__        = xbmc.translatePath( __addon__.getAddonInfo('path') ).decode("utf-8")
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) ).decode("utf-8")
__profile__    = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
__temp__       = xbmc.translatePath( os.path.join( __profile__, 'temp', '') ).decode("utf-8")

sys.path.append (__resource__)

from Utilidades import log
from buscadorsubtitulamos import Buscador

if xbmcvfs.exists(__temp__):
    shutil.rmtree(__temp__)
xbmcvfs.mkdirs(__temp__)

def get_params(string=""):
    param = []
    if string == "":
        paramstring = sys.argv[2]
    else:
        paramstring = string
    if len(paramstring) >= 2:
        params = paramstring
        cleanedparams = params.replace('?', '')
        if (params[len(params)-1] == '/'):
            params = params[0:len(params)-2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param


def Search(item):
    buscador = Buscador()
    fileInfo = buscador.ParseFile(item['title'])
    if item['mansearch'] == False:
        subtitles = buscador.GetMatchingSubtitles(fileInfo['title'],str(fileInfo["season"]), '{:02d}'.format(fileInfo['episode']))
    else:
        subtitles = buscador.GetMatchingSubtitles(item['mansearchstr'],str(fileInfo["season"]), '{:02d}'.format(fileInfo['episode']))

    for subtitle in subtitles:
        url = "plugin://%s/?action=download&link=%s" % (__scriptid__,subtitle.link)
        listitem = xbmcgui.ListItem(label=subtitle.language,
                            label2=subtitle.tvShowName + " - " +subtitle.text + " " + subtitle.season + "x" + subtitle.episode + " - " + subtitle.version,
                            thumbnailImage = subtitle.languageIcon
                            )
        xbmcplugin.addDirectoryItem(handle=int(
            sys.argv[1]), url=url, listitem=listitem, isFolder=False)


params = get_params()

if params['action'] == 'search' or params['action'] == 'manualsearch':
    log(__name__, "Buscar")

    item = {}
    item['temp'] = False
    item['rar'] = False
    item['mansearch'] = False
    item['year'] = xbmc.getInfoLabel(
        "VideoPlayer.Year")                         # Year
    item['season'] = str(xbmc.getInfoLabel(
        "VideoPlayer.Season"))                  # Season
    item['episode'] = str(xbmc.getInfoLabel(
        "VideoPlayer.Episode"))                 # Episode
    item['tvshow'] = xbmc.getInfoLabel("VideoPlayer.TVshowtitle")  # Show
    item['title'] = xbmc.getInfoLabel(
        "VideoPlayer.OriginalTitle")  # try to get original title
    item['file_original_path'] = xbmc.Player().getPlayingFile().decode(
        'utf-8')                 # Full path of a playing file
    item['3let_language'] = []  # ['scc','eng']

    if item['title'] == "":
        item['title']  = xbmc.getInfoLabel("VideoPlayer.Title")
    if 'searchstring' in params:
        item['mansearch'] = True
        item['mansearchstr'] = params['searchstring']

    Search(item)
elif params['action'] == 'download':
    buscador = Buscador()
    path =  os.path.join( __temp__, "%s.%s" %(str(uuid.uuid4()), "srt"))
    buscador.DownloadSubtitle(params['link'], path)
    listitem = xbmcgui.ListItem(label=path)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=path,listitem=listitem,isFolder=False)


xbmcplugin.endOfDirectory(int(sys.argv[1]))
