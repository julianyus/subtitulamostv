# -*- coding: utf-8 -*-

import xbmc
import unicodedata


def log(module, msg):
    xbmc.log((u"### [%s] - %s" % (module, msg)
              ).encode('utf-8'), level=xbmc.LOGERROR)


def normalizeString(str):
    return unicodedata.normalize('NFKD', unicode(unicode(str, 'utf-8'))).encode('ascii', 'ignore')
