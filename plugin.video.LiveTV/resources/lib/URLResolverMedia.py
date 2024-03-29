#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2015 xsteal
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json, re, xbmc, urllib, xbmcgui, os, sys, pprint, urlparse, urllib2, base64, math, string
import htmlentitydefs
from cPacker import cPacker
from t0mm0.common.net import Net
from bs4 import BeautifulSoup
import jsunpacker
from AADecoder import AADecoder
from JsParser import JsParser
from JJDecoder import JJDecoder
from png import Reader as PNGReader
from HTMLParser import HTMLParser

def clean(text):
    command={'&#8220;':'"','&#8221;':'"', '&#8211;':'-','&amp;':'&','&#8217;':"'",'&#8216;':"'"}
    regex = re.compile("|".join(map(re.escape, command.keys())))
    return regex.sub(lambda mo: command[mo.group(0)], text)

def __ALERTA__(text1="",text2="",text3=""):
    if text3=="": xbmcgui.Dialog().ok(text1,text2)
    elif text2=="": xbmcgui.Dialog().ok("",text1)
    else: xbmcgui.Dialog().ok(text1,text2,text3)

def log(msg, level=xbmc.LOGNOTICE):
	level = xbmc.LOGNOTICE
	print('[LIVEIT]: %s' % (msg))
	xbmc.log('[LIVEIT]: %s' % (msg), level)
	
	try:
		if isinstance(msg, unicode):
			msg = msg.encode('utf-8')
		xbmc.log('[LIVEIT]: %s' % (msg), level)
	except Exception as e:
		try:
			a=1
		except: pass  

class RapidVideo():
	def __init__(self, url):
		self.url = url
		self.net = Net()
		self.headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3"}
		self.legenda = ''

	def getId(self):
		return urlparse.urlparse(self.url).path.split("/")[-1]

	def getMediaUrl(self):
		try:
			sourceCode = self.net.http_GET(self.url, headers=self.headers).content.decode('unicode_escape')
		except:
			sourceCode = self.net.http_GET(self.url, headers=self.headers).content

		sPattern =  '"file":"([^"]+)","label":"([0-9]+)p.+?"'
		aResult = self.parse(sourceCode, sPattern)
		try:
			self.legenda = "https://www.raptu.com%s"%re.compile('"file":"([^"]+)","label":".+?","kind":"captions"').findall(sourceCode)[0]
			#log(self.legenda)
		except:
			self.legenda = ''
		videoUrl = ''
		if aResult[0]:
			links = []
			qualidades = []
			for aEntry in aResult[1]:
				links.append(aEntry[0])
				if aEntry[1] == '2160':
					qualidades.append('4K')
				else:
					qualidades.append(aEntry[1]+'p')

			if len(links) == 1:
				videoUrl = links[0]
			elif len(links) > 1:
				links.reverse()
				qualidades.reverse()

				qualidade = xbmcgui.Dialog().select('Escolha a qualidade', qualidades)
				videoUrl = links[qualidade]

		return videoUrl
	def getLegenda(self):
		return self.legenda
	def parse(self, sHtmlContent, sPattern, iMinFoundValue = 1):
		sHtmlContent = self.replaceSpecialCharacters(str(sHtmlContent))
		aMatches = re.compile(sPattern, re.IGNORECASE).findall(sHtmlContent)
		if (len(aMatches) >= iMinFoundValue):
			return True, aMatches
		return False, aMatches
	def replaceSpecialCharacters(self, sString):
		return sString.replace('\\/','/').replace('&amp;','&').replace('\xc9','E').replace('&#8211;', '-').replace('&#038;', '&').replace('&rsquo;','\'').replace('\r','').replace('\n','').replace('\t','').replace('&#039;',"'")

class CloudMailRu():
	def __init__(self, url):
		self.url = url
		self.net = Net()
		self.headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3"}

	def getId(self):
		return re.compile('(?:\/\/|\.)cloud\.mail\.ru\/public\/(.+)').findall(self.url)[0]
	def getMediaUrl(self):
		conteudo = self.net.http_GET(self.url).content
		ext = re.compile('<meta name=\"twitter:image\" content=\"(.+?)\"/>').findall(conteudo)[0]
		streamAux = clean(ext.split('/')[-1])
		extensaoStream = clean(streamAux.split('.')[-1])
		token = re.compile('"tokens"\s*:\s*{\s*"download"\s*:\s*"([^"]+)').findall(conteudo)[0]
		mediaLink = re.compile('"weblink_get"\s*:\s*\[.+?"url"\s*:\s*"([^"]+)').findall(conteudo)[0]
		videoUrl = '%s/%s?key=%s' % (mediaLink, self.getId(), token)
		return videoUrl, extensaoStream

class GoogleVideo():
	def __init__(self, url):
		self.url = url
		self.net = Net()
		self.headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3"}
		self.UA = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0'

	def getId(self):
		return urlparse.urlparse(self.url).path.split("/")[-2]

	def getMediaUrl(self):
		req = urllib2.Request(self.url)
		response = urllib2.urlopen(req)  
		sourceCode = response.read()
		Headers = response.headers
		response.close()
		try:
			sourceCode = sourceCode.decode('unicode_escape')
		except:
			pass
		c = Headers['Set-Cookie']
		c2 = re.findall('(?:^|,) *([^;,]+?)=([^;,\/]+?);',c)
		if c2:
			cookies = ''
			for cook in c2:
				cookies = cookies + cook[0] + '=' + cook[1]+ ';'

		formatos = {
		'5': {'ext': 'flv'},
		'6': {'ext': 'flv'},
		'13': {'ext': '3gp'},
		'17': {'ext': '3gp'},
		'18': {'ext': 'mp4'},
		'22': {'ext': 'mp4'},
		'34': {'ext': 'flv'},
		'35': {'ext': 'flv'},
		'36': {'ext': '3gp'},
		'37': {'ext': 'mp4'},
		'38': {'ext': 'mp4'},
		'43': {'ext': 'webm'},
		'44': {'ext': 'webm'},
		'45': {'ext': 'webm'},
		'46': {'ext': 'webm'},
		'59': {'ext': 'mp4'}
		}
		formatosLista = re.search(r'"fmt_list"\s*,\s*"([^"]+)', sourceCode).group(1)
		formatosLista = formatosLista.split(',')
		streamsLista = re.search(r'"fmt_stream_map"\s*,\s*"([^"]+)', sourceCode).group(1)
		streamsLista = streamsLista.split(',')

		videos = []
		qualidades = []
		i = 0
		for stream in streamsLista:
			formatoId, streamUrl = stream.split('|')
			form = formatos.get(formatoId)
			extensao = form['ext']
			resolucao = formatosLista[i].split('/')[1]
			largura, altura = resolucao.split('x')
			if 'mp' in extensao or 'flv' in extensao:
				qualidades.append(altura+'p '+extensao)
				videos.append(streamUrl)
				i+=1
		qualidade = xbmcgui.Dialog().select('Escolha a qualidade', qualidades)
		return videos[qualidade]+'|User-Agent=' + self.UA + '&Cookie=' + cookies, qualidades[qualidade].split('p ')[-1]


class UpToStream():
	def __init__(self, url):
		self.url = url
		self.net = Net()
		self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0', 'Accept-Charset': 'utf-8;q=0.7,*;q=0.7'}

	def getId(self):
		if 'iframe' in self.url:
			return re.compile('http\:\/\/uptostream\.com\/iframe\/(.+)').findall(self.url)[0]
		else:
			return re.compile('http\:\/\/uptostream\.com\/(.+)').findall(self.url)[0]

	def getMediaUrl(self):
		sourceCode = self.net.http_GET(self.url, headers=self.headers).content

		links = re.compile('source\s+src=[\'\"]([^\'\"]+)[\'\"].+?data-res=[\'\"]([^\"\']+)[\'\"]').findall(sourceCode)
		videos = []
		qualidades = []
		for link, qualidade in links:
			if link.startswith('//'):
				link = "http:"+link
			videos.append(link)
			qualidades.append(qualidade)
		videos.reverse()
		qualidades.reverse()
		qualidade = xbmcgui.Dialog().select('Escolha a qualidade', qualidades)
		return videos[qualidade]

class OpenLoad():

	def __init__(self, url):
		self.url = url
		self.net = Net()
		self.id = str(self.getId())
		self.messageOk = xbmcgui.Dialog().ok
		self.site = 'https://openload.co'
		#self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0', 'Accept-Charset': 'utf-8;q=0.7,*;q=0.7'}
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
			'Accept-Encoding': 'none',
			'Accept-Language': 'en-US,en;q=0.8',
			'Referer': url}

	#Código atualizado a partir de: https://gitlab.com/iptvplayer-for-e2 
	def decodeK(self, k, p0, p1, p2):
		y = ord(k[0]);
		e = y - p1
		d = max(2, e)
		e = min(d, len(k) - p0 - 2)
		t = k[e:e + p0]
		h = 0
		g = []
		while h < len(t):
			f = t[h:h+3]
			g.append(int(f, 0x8))
			h += 3
		v = k[0:e] + k[e+p0:]
		p = []
		i = 0
		h = 0
		while h < len(v):
			B = v[h:h + 2]
			C = v[h:h + 3]
			D = v[h:h + 4]
			f = int(B, 0x10)
			h += 0x2

			if (i % 3) == 0:
				f = int(C, 8)
				h += 1
			elif i % 2 == 0 and i != 0 and ord(v[i-1]) < 0x3c:
				f = int(D, 0xa)
				h += 2
			    
			A = g[i % p2]
			f = f ^ 0xd5;
			f = f ^ A;
			p.append( chr(f) )
			i += 1
		return "".join(p)
	
	def getAllItemsBeetwenMarkers(self, data, marker1, marker2, withMarkers=True, caseSensitive=True):
		itemsTab = []
		if caseSensitive:
			sData = data
		else:
			sData = data.lower()
			marker1 = marker1.lower()
			marker2 = marker2.lower()
		idx1 = 0
		while True:
			idx1 = sData.find(marker1, idx1)
			if -1 == idx1: return itemsTab
			idx2 = sData.find(marker2, idx1 + len(marker1))
			if -1 == idx2: return itemsTab
			tmpIdx2 = idx2 + len(marker2) 
			if withMarkers:
				idx2 = tmpIdx2
			else:
				idx1 = idx1 + len(marker1)
			itemsTab.append(data[idx1:idx2])
			idx1 = tmpIdx2
		return itemsTab
	def rgetDataBeetwenMarkers2(self, data, marker1, marker2, withMarkers=True, caseSensitive=True):
		if caseSensitive:
			sData = data
		else:
			sData = data.lower()
			marker1 = marker1.lower()
			marker2 = marker2.lower()
		idx1 = len(data)

		idx1 = sData.rfind(marker1, 0, idx1)
		if -1 == idx1: return False, ''
		idx2 = sData.rfind(marker2, 0, idx1)
		if -1 == idx2: return False, ''

		if withMarkers:
			return True, data[idx2:idx1+len(marker1)]
		else:
			return True, data[idx2+len(marker2):idx1]
	def getSearchGroups(self, data, pattern, grupsNum=1, ignoreCase=False):
		tab = []
		if ignoreCase:
			match = re.search(pattern, data, re.IGNORECASE)
		else:
			match = re.search(pattern, data)

		for idx in range(grupsNum):
			try:    value = match.group(idx + 1)
			except Exception: value = ''
			tab.append(value)
		return tab
	def getDataBeetwenMarkers(self, data, marker1, marker2, withMarkers=True, caseSensitive=True):
		if caseSensitive:
			idx1 = data.find(marker1)
		else:
			idx1 = data.lower().find(marker1.lower())
		if -1 == idx1: return False, ''
		if caseSensitive:
			idx2 = data.find(marker2, idx1 + len(marker1))
		else:
			idx2 = data.lower().find(marker2.lower(), idx1 + len(marker1))
		if -1 == idx2: return False, ''

		if withMarkers:
			idx2 = idx2 + len(marker2)
		else:
			idx1 = idx1 + len(marker1)
		return True, data[idx1:idx2]
	def parserOPENLOADIO(self, urlF):
		try:
			req = urllib2.Request(urlF, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0'})
			response = urllib2.urlopen(req)
			html = response.read()
			response.close()
			try: html = html.encode('utf-8')
			except: pass

			TabUrl = []
			sPattern = '<span id="([^"]+)">([^<>]+)<\/span>'
			aResult = self.parse(html, sPattern)
			if (aResult[0]):
				TabUrl = aResult[1]
			else:
				#log("No Encoded Section Found. Deleted?")
				raise ResolverError('No Encoded Section Found. Deleted?')
			sPattern = '<script src="\/assets\/js\/video-js\/video\.js\.ol\.js"(.+)*'
			aResult = self.parse(html, sPattern)
			if (aResult[0]):
				sHtmlContent2 = aResult[1][0]
			code = ''
			maxboucle = 3
			sHtmlContent3 = sHtmlContent2
			while (('window.r' not in sHtmlContent3) and (maxboucle > 0)):
				sHtmlContent3 = self.CheckCpacker(sHtmlContent3)
				sHtmlContent3 = self.CheckJJDecoder(sHtmlContent3)
				sHtmlContent3 = self.CheckAADecoder(sHtmlContent3)
				maxboucle = maxboucle - 1
			code = sHtmlContent3
			if not (code):
				#log("No Encoded Section Found. Deleted?")
				raise ResolverError('No Encoded Section Found. Deleted?')
			aResult = self.parse(code, "window.r='([^']+)';")
			if(aResult[0]):
				ID = aResult[1][0]

			
			tab = [(0x24, 0x37, 0x7), (0x1e, 0x34, 0x6)]
			orgData = self.getDataBeetwenMarkers(code, '$(document)', '}});')[1].decode('string_escape')
			p0 = self.getDataBeetwenMarkers(orgData, "splice", ';')[1]
			p0 = self.getSearchGroups(p0, "\,(0x[0-9a-fA-F]+?)\)")[0]
			p1 = self.getDataBeetwenMarkers(orgData, "'#'", 'continue;')[1]
			p1 = self.getSearchGroups(p1, "\,(0x[0-9a-fA-F]+?)\)")[0]
			p2 = self.rgetDataBeetwenMarkers2(orgData, '^=0x', 'var ')[1]
			p2 = self.getSearchGroups(p2, "\,(0x[0-9a-fA-F]+?)\)")[0]
			
			tab.insert(0, (int(p0, 16), int(p1, 16), int(p2, 16)))
			dec = ''
			for item in tab:
				dec = self.decodeK(TabUrl[0][1], item[0], item[1], item[2])
				if dec != '': break
			if not(dec):
				#log("No Encoded Section Found. Deleted?")
				raise ResolverError('No Encoded Section Found. Deleted?')

			
	  
			api_call = "https://openload.co/stream/" + dec + "?mime=true" 

			if 'KDA_8nZ2av4/x.mp4' in api_call:
				#log('Openload.co resolve failed')
				raise ResolverError('Openload.co resolve failed')
			if dec == api_call:
				#log('pigeon url : ' + api_call)
				api_call = ''
				raise ResolverError('pigeon url : ' + api_call)
			
			return api_call
		except Exception as e:
			self.messageOk('Live!t-TV', 'Ocorreu um erro a obter o link. Escolha outro servidor.')
		except ResolverError:
			self.messageOk('Live!t-TV', 'Ocorreu um erro a obter o link. Escolha outro servidor.')

	def getId(self):
		#return self.url.split('/')[-1]
		try:
			try:
				return re.compile('https\:\/\/openload\.co\/embed\/(.+?)').findall(self.url)[0]
			except:
				return re.compile('https\:\/\/openload\.co\/embed\/(.+?)\/').findall(self.url)[0]
		except:
			return re.compile('https\:\/\/openload.co\/f\/(.+?)\/').findall(self.url)[0]


	def unescape(self, text):
		def fixup(m):
			text = m.group(0)
			if text[:2] == "&#":
				try:
					if text[:3] == "&#x":
						return unichr(int(text[3:-1], 16))
					else:
						return unichr(int(text[2:-1]))
				except ValueError:
					pass
			else:
				try:
					text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
				except KeyError:
					pass
				return text # leave as is
		return re.sub("&#?\w+;", fixup, text)

	def getMediaUrl(self):

		videoUrl = self.parserOPENLOADIO(self.url)

		return videoUrl

	def getDownloadUrl(self):
		content = self.net.http_GET(self.url, headers=self.headers).content

		url = self.decodeOpenLoad(str(content.encode('utf-8')))

		return url

	def parse(self, sHtmlContent, sPattern, iMinFoundValue = 1):
		sHtmlContent = self.replaceSpecialCharacters(str(sHtmlContent))
		aMatches = re.compile(sPattern, re.IGNORECASE).findall(sHtmlContent)
		if (len(aMatches) >= iMinFoundValue):
			return True, aMatches
		return False, aMatches
	def replaceSpecialCharacters(self, sString):
		return sString.replace('\\/','/').replace('&amp;','&').replace('\xc9','E').replace('&#8211;', '-').replace('&#038;', '&').replace('&rsquo;','\'').replace('\r','').replace('\n','').replace('\t','').replace('&#039;',"'")

	def parseInt(self, sin):
		return int(''.join([c for c in re.split(r'[,.]',str(sin))[0] if c.isdigit()])) if re.match(r'\d+', str(sin), re.M) and not callable(sin) else None

	def GetOpenloadUrl(self, url, referer):
		if 'openload.co/stream' in url:

			headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11', 'Referer':referer }

			req = urllib2.Request(url,None,headers)
			res = urllib2.urlopen(req)
			finalurl = res.geturl()

			if 'KDA_8nZ2av4/x.mp4' in finalurl:
				print('pigeon url : ' + url)
				finalurl = ''
			if 'Content-Length' in res.info():
				if res.info()['Content-Length'] == '33410733':
					print('pigeon url : ' + url)
					finalurl = ''
			if url == finalurl:
				print('Bloquage')
				finalurl = ''

			return finalurl
		return url

	def CheckCpacker(self, str):
		sPattern = '(\s*eval\s*\(\s*function(?:.|\s)+?{}\)\))'
		aResult = self.parse(str, sPattern)
		if (aResult[0]):
			str2 = aResult[1][0]
			if not str2.endswith(';'):
				str2 = str2 + ';'
			try:
				str = cPacker().unpack(str2)
			except:
				pass
		return str
	def CheckJJDecoder(self, str):
		sPattern = '([a-z]=.+?\(\)\)\(\);)'
		aResult = self.parse(str, sPattern)
		if (aResult[0]):
			return JJDecoder(aResult[1][0]).decode()
		return str
	def CheckAADecoder(self, str):
		sPattern = '[>;]\s*(ﾟωﾟ.+?\(\'_\'\);)'
		aResult = re.search(sPattern, str,re.DOTALL | re.UNICODE)
		if (aResult):
			tmp = AADecoder(aResult.group(1)).decode()
			return str[:aResult.start()] + tmp + str[aResult.end():]			
		return str
	def getMediaUrlOld(self):

		try:
			ticket = 'https://api.openload.co/1/file/dlticket?file=%s' % self.id
			result = self.net.http_GET(ticket).content
			jsonResult = json.loads(result)

			if jsonResult['status'] == 200:
				fileUrl = 'https://api.openload.co/1/file/dl?file=%s&ticket=%s' % (self.id, jsonResult['result']['ticket'])
				captcha = jsonResult['result']['captcha_url']

				print "CAPTCHA: "
				print self.id
				captcha.replace('\/', '/')
				print captcha

				if captcha:
					captchaResponse = self.getCaptcha(captcha.replace('\/', '/'))

					if captchaResponse:
						fileUrl += '&captcha_response=%s' % urllib.quote(captchaResponse)

				xbmc.sleep(jsonResult['result']['wait_time'] * 1000)

				result = self.net.http_GET(fileUrl).content
				jsonResult = json.loads(result)

				if jsonResult['status'] == 200:
					return jsonResult['result']['url'] + '?mime=true'  #really?? :facepalm:
				else:
					self.messageOk('Live!t-TV', "FILE: "+jsonResult['msg'])

			else:

				self.messageOk('Live!t-TV', "TICKET: "+jsonResult['msg'])
				return False
		except:
			self.messageOk('Live!t-TV', 'Ocorreu um erro a obter o link. Escolha outro servidor.')

	def getCaptcha(self, image):
		try:
			image = xbmcgui.ControlImage(450, 0, 300, 130, image)
			dialog = xbmcgui.WindowDialog()
			dialog.addControl(image)
			dialog.show()
			xbmc.sleep(3000)

			letters = xbmc.Keyboard('', 'Escreva as letras na imagem', False)
			letters.doModal()

			if(letters.isConfirmed()):
				result = letters.getText()
				if result == '':
					self.messageOk('Live!t-TV', 'Tens de colocar o texto da imagem para aceder ao video.')
				else:
					return result
			else:
				self.messageOk('Live!t-TV', 'Erro no Captcha')
		finally:
			dialog.close()

	def getSubtitle(self):
		pageOpenLoad = self.net.http_GET(self.url, headers=self.headers).content

		try:
			subtitle = re.compile('<track\s+kind="captions"\s+src="(.+?)"').findall(pageOpenLoad)[0]
		except:
			subtitle = ''
		#return self.site + subtitle
		return subtitle


class VideoMega():

	def __init__(self, url):
		self.url = url
		self.net = Net()
		self.id = str(self.getId())
		self.messageOk = xbmcgui.Dialog().ok
		self.site = 'https://videomega.tv'
		self.headers = 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'
		self.headersComplete = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25', 'Referer': self.getNewHost()}

	def getId(self):
		return re.compile('http\:\/\/videomega\.tv\/view\.php\?ref=(.+?)&width=700&height=430').findall(self.url)[0]

	def getNewHost(self):
		return 'http://videomega.tv/cdn.php?ref=%s' % (self.id)

	def getMediaUrl(self):
		sourceCode = self.net.http_GET(self.getNewHost(), headers=self.headersComplete).content
		match = re.search('<source\s+src="([^"]+)"', sourceCode)

		if match:
			return match.group(1) + '|User-Agent=%s' % (self.headers)
		else:
			self.messageOk('MrPiracy.xyz', 'Video nao encontrado.')

class Vidzi():
	def __init__(self, url):
		self.url = url
		self.net = Net()
		self.id = str(self.getId())
		self.messageOk = xbmcgui.Dialog().ok
		self.site = 'https://videomega.tv'
		self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'}
		self.subtitle = ''

	def getId(self):
		return re.compile('http\:\/\/vidzi.tv\/embed-(.+?)-').findall(self.url)[0]

	def getNewHost(self):
		return 'http://vidzi.tv/embed-%s.html' % (self.id)

	def getMediaUrl(self):
		sourceCode = self.net.http_GET(self.getNewHost(), headers=self.headers).content

		if '404 Not Found' in sourceCode:
			self.messageOk('Live!t-TV', 'Ficheiro nao encontrado ou removido. Escolha outro servidor.')

		match = re.search('file\s*:\s*"([^"]+)', sourceCode)
		if match:
			return match.group(1) + '|Referer=http://vidzi.tv/nplayer/jwpayer.flash.swf'
		else:
			for pack in re.finditer('(eval\(function.*?)</script>', sourceCode, re.DOTALL):
				dataJs = jsunpacker.unpack(pack.group(1)) # Unpacker for Dean Edward's p.a.c.k.e.r | THKS

				#print dataJs
				#pprint.pprint(dataJs)

				stream = re.search('file\s*:\s*"([^"]+)', dataJs)
				try:
					subtitle = re.compile('tracks:\[\{file:"(.+?)\.srt"').findall(dataJs)[0]
					subtitle += ".srt"
				except:
					try:
						subtitle = re.compile('tracks:\[\{file:"(.+?)\.vtt"').findall(dataJs)[0]
						subtitle += ".vtt"
					except:
						subtitle = ''
				self.subtitle = subtitle

				if stream:
					return stream.group(1)

		self.messageOk('Live!t-TV', 'Video nao encontrado. Escolha outro servidor')


	def getSubtitle(self):
		return self.subtitle