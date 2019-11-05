# -*- coding: utf-8 -*-

import urllib3
import re
import PTN
import xbmc
import unicodedata
import json
from bs4 import BeautifulSoup

from Utilidades import log, normalizeString

class Subtitle:
	def __init__(self, tvShowName, season, episode, text, language, languageIcon, link, version):
		self.season = season
		self.episode = episode
		self.text = text
		self.language = language
		self.languageIcon = languageIcon
		self.tvShowName = tvShowName
		self.link = link
		self.version = version

	def __str__(self):
		return "{ temporada: " + self.season + ", numero: " + self.episode + ", texto: '" + self.text + "'  }"
	def __unicode__(self):
		return u"{ 'temporada': " + self.season + ", 'numero': " + self.episode + ", 'texto': '" + self.text + "' }"


class Buscador:
	def __init__(self):
		self.urlRoot = "https://www.subtitulamos.tv/"
		self.http = urllib3.PoolManager()

	def ParseFile(self, fichero):
		info = PTN.parse(fichero)
		return info

	def GetMatchingSubtitles(self, tvShowName, season, episodeNumber):
		foundSubtitles = []
		response = self.http.request('GET', self.urlRoot + "search/query?q=" + tvShowName + " " + season + "x" + episodeNumber)
		tvShows = json.loads(response.data)
		for tvShow in tvShows:
			for episode in tvShow['episodes']:
				response = self.http.request('GET', self.urlRoot + "episodes/" + str(episode['id']))
				soup = BeautifulSoup(response.data, 'html.parser')
				subtitles = soup.find_all('a', href=re.compile("/subtitles.*/download"))
				for subtitle in subtitles:
					version = subtitle.parent.find_previous_sibling("div", class_="version_name")
					language = version.parent.find_previous_sibling("div", class_="subtitle_language")
					foundSubtitles.append(Subtitle(
						tvShow['name'], 
						season, 
						episodeNumber, 
						episode['name'], 
						language.string, 
						self.TranslateLanguageToIcon(language.string),
						subtitle.get('href'), 
						version.string ))
		return foundSubtitles
		
	def DownloadSubtitle(self, url, path):
		response = self.http.request('GET', self.urlRoot + url)
		with open(path,'wb') as output:
			output.write(response.data)

	def TranslateLanguageToIcon(self, language):
		if language == 'English':
			return 'en'
		if language == u'Español (España)':
			return 'es'
		if language == u'Français':
			return 'fr'
		if language == u'Español (Latinoamérica)':
			return 'es'
		if language == u'Galego':
			return 'es'
		if language == u'Català':
			return 'es'
		return 'en'
