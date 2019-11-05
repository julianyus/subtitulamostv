import urllib3
import re
import PTN
import xbmc
import unicodedata
import json
from bs4 import BeautifulSoup

from Utilidades import log, normalizeString

class Capitulo:
	def __init__(self, nombreSerie, temporada, numero, texto, idioma, enlace, version):
		self.temporada = temporada
		self.numero = numero
		self.texto = texto
		self.idioma = idioma
		self.nombreSerie = nombreSerie
		self.enlace = enlace
		self.version = version

	def __str__(self):
		return "{ temporada: " + self.temporada + ", numero: " + self.numero + ", texto: '" + self.texto + "'  }"
	def __unicode__(self):
		return u"{ 'temporada': " + self.temporada + ", 'numero': " + self.numero + ", 'texto': '" + self.texto + "' }"


class Buscador:
	def __init__(self):
		self.urlRoot = "https://www.subtitulamos.tv/"
		self.http = urllib3.PoolManager()

	def ParsearFichero(self, fichero):
		info = PTN.parse(fichero)
		return info

	def ObtenerCapitulosCoincidentes(self, nombreSerie, temporada, capitulo):
		capitulos = []
		response = self.http.request('GET', self.urlRoot + "search/query?q=" + nombreSerie + " " + temporada + "x" + capitulo)
		series = json.loads(response.data)
		for serie in series:
			for episodio in serie['episodes']:
				response = self.http.request('GET', self.urlRoot + "episodes/" + str(episodio['id']))
				soup = BeautifulSoup(response.data, 'html.parser')
				subtitulos = soup.find_all('a', href=re.compile("/subtitles.*/download"))
				for subtitulo in subtitulos:
					version = subtitulo.parent.find_previous_sibling("div", class_="version_name")
					idioma = version.parent.find_previous_sibling("div", class_="subtitle_language")
					capitulos.append(Capitulo(serie['name'], temporada, capitulo, episodio['name'], idioma.string, subtitulo.get('href'), version.string ))
		return capitulos
		
	def DescargarCapitulo(self, url, path):
		response = self.http.request('GET', self.urlRoot + url)
		with open(path,'wb') as output:
			output.write(response.data)

