#!/usr/bin/env python
# -*- coding: UTF-8 -*-
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


##############BIBLIOTECAS A IMPORTAR E DEFINICOES####################

import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmcaddon,xbmc,os,json,threading,xbmcvfs,cookielib
from t0mm0.common.net import Net
import xml.etree.ElementTree as ET

####################################################### CONSTANTES #####################################################

__ADDON_ID__   = xbmcaddon.Addon().getAddonInfo("id")
__ADDON__	= xbmcaddon.Addon(__ADDON_ID__)
__ADDON_FOLDER__	= __ADDON__.getAddonInfo('path')
__SETTING__	= xbmcaddon.Addon().getSetting
__ART_FOLDER__	= os.path.join(__ADDON_FOLDER__,'resources','img')
__FANART__ 		= os.path.join(__ADDON_FOLDER__,'fanart.jpg')
__SKIN__ = 'v1'
__SITE__ = 'http://www.pcteckserv.com/GrupoKodi/PHP/'
__SITEAddon__ = 'http://www.pcteckserv.com/GrupoKodi/Addon/'
__ALERTA__ = xbmcgui.Dialog().ok

__COOKIE_FILE__ = os.path.join(xbmc.translatePath('special://userdata/addon_data/plugin.video.LiveTV-2.1.12/').decode('utf-8'), 'cookie.mrpiracy')
__HEADERS__ = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'}

###################################################################################
#                              Iniciar Addon		                                  #
###################################################################################
def menu():
	check_login = login()
	if check_login['sucesso']['resultado'] == 'yes':
		Menu_inicial(check_login)
		addDir('Definições', 'url', None, 1000, __SITEAddon__+"Imagens/definicoes.png", 0)
		vista_menu()
	else:
		addDir('Alterar Definições', 'url', None, 1000, __SITEAddon__+"Imagens/definicoes.png", 0)
		addDir('Entrar novamente', 'url', None, None, __SITEAddon__+"Imagens/retroceder.png", 0)
        vista_menu()
###################################################################################
#                              Login Addon		                                  #
###################################################################################

def mac_for_ip():
	print "Macs 1"
	macadresses = ""
	if xbmc.getInfoLabel('Network.MacAddress') != None:
		macadresses = xbmc.getInfoLabel('Network.MacAddress')
		print macadresses
	print "Macs 4"
	return macadresses
	
def login():
	informacoes = {
		'user' : {
			'nome': '',
			'email': '',
			'senhaadulto': ''
		},
		'sucesso' :{
			'resultado': ''
		},
		'info' : {
			'epg': '',
			'logo': ''
		},
		'menus': []
	} # 
	
	if __ADDON__.getSetting("login_name") == '' or __ADDON__.getSetting('login_password') == '':
		__ALERTA__('Live!t TV', 'Precisa de definir o seu Utilizador e Senha')
		return informacoes
	else:
		try:
			macs = mac_for_ip()
			print "reideus"
			net = Net()
			net.set_cookies(__COOKIE_FILE__)
			dados = {'username': __ADDON__.getSetting("login_name"), 'password': __ADDON__.getSetting("login_password"), 'lembrar_senha': 'lembrar'}
			codigo_fonte = net.http_POST(__SITE__+'LoginAddon.php',form_data=dados,headers=__HEADERS__).content
	
			elems = ET.fromstring(codigo_fonte)
			for child in elems:
				if(child.tag == 'sucesso'):
					informacoes['sucesso']['resultado'] = child.text
				elif(child.tag == 'user'):
					for d in child:
						if(d.tag == 'Nome'):
							informacoes['user']['nome'] = d.text
						elif(d.tag == 'Email'):
							informacoes['user']['email'] = d.text
						elif(d.tag == 'SenhaAdultos'):
							informacoes['user']['senhaadulto'] = d.text		
				elif(child.tag == 'info'):
					for e in child:
						if(e.tag == 'Epg'):
							informacoes['info']['epg'] = e.text
						elif(e.tag == 'Logos'):
							informacoes['info']['logos'] = e.text
				elif(child.tag == 'menus'):
					menu = {
							'nome': '',
							'logo': '',
							'link': '',
							'tipo': '',
							'senha': ''
						}
					for g in child:
						if(g.tag == 'nome'):
							menu['nome'] = g.text
						elif(g.tag == 'logo'):
							menu['logo'] = g.text
						elif(g.tag == 'link'):
							menu['link'] = g.text
						elif(g.tag == 'tipo'):
							menu['tipo'] = g.text
						elif(g.tag == 'senha'):
							menu['senha'] = informacoes['user']['senhaadulto']
					informacoes['menus'].append(menu)
				else: 
					print("Não sei o que estou a ler")
		except:
			__ALERTA__('Live!t TV', 'Não foi possível abrir a página. Por favor tente novamente.')
			return informacoes

		if informacoes['sucesso']['resultado'] != '':
			if informacoes['sucesso']['resultado'] == 'no':
				__ALERTA__('Live!t TV', 'Utilizador e/ou Senha incorretos.')
				return informacoes
			else:
				xbmc.executebuiltin("XBMC.Notification(Live!t TV, Sessão iniciada: "+ informacoes['user']['nome'] +", '10000', "+__ADDON_FOLDER__+"/icon.png)")
				return informacoes
		else:
			net.save_cookies(__COOKIE_FILE__)
			xbmc.executebuiltin("XBMC.Notification(Live!t TV, Sessão iniciada: "+ informacoes['user']['nome'] +", '10000', "+__ADDON_FOLDER__+"/icon.png)")
			return informacoes	

###############################################################################################################
#                                                   Menus                                                     #
###############################################################################################################

def Menu_inicial(men):
	for menu in men['menus']:
		nome = menu['nome']
		logo = menu['logo']
		link = menu['link']
		tipo = menu['tipo']
		senha = menu['senha']
		if(tipo == 'adulto'):
			addDir(nome,link,senha,3,logo)
		else:
			addDir(nome,link,None,1,logo)

def listar_grupos_adultos(url,senha):
	if(__ADDON__.getSetting("login_adultos") == ''):
		__ALERTA__('Live!t TV', 'Preencha o campo senha para adultos.')
	elif(__ADDON__.getSetting("login_adultos") != senha):
		__ALERTA__('Live!t TV', 'Senha para adultos incorrecta. Verifique e tente de novo.')
	else:
		listar_grupos(url)
	
def listar_grupos(url):
	page_with_xml = urllib2.urlopen(url).readlines()
	for line in page_with_xml:
		params = line.split(',')
		try:
			nomee = params[0]
			imag = params[1]
			urlll = params[2]
			addDir(nomee,urlll,None,2,imag)
		except:
			pass
		
def listar_canais_url(nome,url):
	page_with_xml = urllib2.urlopen(url).readlines()
	for line in page_with_xml:
		params = line.split(',')
		try:
			  nomee = params[0]
			  img = params[1].replace(' rtmp','rtmp').replace(' rtsp','rtsp').replace(' http','http')
			  rtmp = params[2].replace(' rtmp','rtmp').replace(' rtsp','rtsp').replace(' http','http')
			  grup = params[3]
			  id_it = params[4]
			  if(grup == nome):
				addLink(nomee,rtmp,img)
		except:
			  pass
###################################################################################
#                              DEFININCOES		                                  #
###################################################################################		
def abrirDefinincoes():
	__ADDON__.openSettings()
	addDir('Entrar novamente', 'url', None, None, __SITEAddon__+"Imagens/retroceder.png", 0)
	vista_menu()
	# xbmcplugin.endOfDirectory(int(sys.argv[1]))

def vista_menu():
	opcao = __ADDON__.getSetting('menuView')
	if opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
	elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51")
	
def addDir(name,url,senha,mode,iconimage,pasta=True,total=1):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&senha="+str(senha)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setProperty('fanart_image', iconimage)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=pasta,totalItems=total)
	return ok
	
def addFolder(name,url,mode,iconimage,folder):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setProperty('fanart_image', iconimage)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=folder)
	return ok

def abrir_url(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link
	
def addLink(name,url,iconimage):
	ok=True
	liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setProperty('fanart_image', iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
	return ok
############################################################################################################
#                                               GET PARAMS                                                 #
############################################################################################################          
def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'): params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2: param[splitparams[0]]=splitparams[1]
	return param


params=get_params()
url=None
name=None
mode=None
iconimage=None
link=None
senha=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass
try:        
        iconimage=urllib.unquote_plus(params["iconimage"])
except:
        pass
try:        
        senha=urllib.unquote_plus(params["senha"])
except:
        pass

###############################################################################################################
#                                                   MODOS                                                     #
###############################################################################################################

if mode==None or url==None or len(url)<1: menu()
elif mode==1: listar_grupos(str(url))
elif mode==2: listar_canais_url(str(name),str(url))
elif mode==3: listar_grupos_adultos(str(url),str(senha))
elif mode==10: minhaConta()
elif mode==1000: abrirDefinincoes()
xbmcplugin.endOfDirectory(int(sys.argv[1]))
