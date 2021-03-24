import os
from time import sleep
import datetime as dt
import yaml
import ntplib
from urllib import request
from bs4 import BeautifulSoup

def get_ntp_offset(server):
	try:
		c = ntplib.NTPClient()
		response = c.request(server, version=3)
		return response.offset, dt.datetime.fromtimestamp(response.tx_time)
	except Exception as e:
		print(e)

def load_yaml(yamlfile):
	with open(yamlfile, 'r') as f:
		yamlcontent = yaml.safe_load(f)
	return yamlcontent

def read_ews_time(address):
	try:
		with request.urlopen(address) as f:
			htmldoc = f.read()
		soup = BeautifulSoup(htmldoc, 'html.parser')
		s = soup.p.text.split(', ')[1]
		return dt.datetime.strptime(s, '%d %b %Y %H:%M:%S')
	except Exception as e:
		print(e)

# create windows desktop shortcut with something like:
#%windir%\System32\cmd.exe "/K" C:\Users\ftir\Anaconda3\Scripts\activate.bat C:\Users\ftir\Anaconda3 & python fts_ntp_check.py

if __name__ == '__main__':
	print('Starting in 10s ...')
	config = load_yaml('config.yaml')
	while True:
		try:
			sleep(10)
			offset, ntptime = get_ntp_offset(config['ntp']['server'])
			ewstime = read_ews_time('http://'+config['fts']['ip']+'/'+config['fts']['ews_homepage'])
			systime = dt.datetime.now()
			fname = 'ny_ntp_'+systime.strftime('%Y%m%d')+'.log'
			pathfname = os.path.join(config['log']['logpath'], fname)
			if not os.path.exists(pathfname):
				with open(pathfname, 'a') as f:
					f.write('2 5\n ntptime systime ewstime sysoffsettontp ewsoffsettontp\n')
			S = ntptime.strftime('%Y%m%d%H%M%S')+' '+systime.strftime('%Y%m%d%H%M%S')+' '+ewstime.strftime('%Y%m%d%H%M%S')+' '+str((systime-ntptime).total_seconds())+' '+str((ewstime-ntptime).total_seconds())
			with open(pathfname, 'a') as f:
				f.write(S+'\n')
			print(S)
			sleep(int(config['ntp']['check_interval_seconds'])-10)
		except Exception as e:
			print(e)

