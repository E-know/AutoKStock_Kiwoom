import time
from config.telegramBot import *


class Stock:
	def __init__(self):
		self.jongmok = {}
		self.min_chart = {}
		self.average_5min = {}
		self.average_20min = {}
		
		self.date = None
		self.set_date()
		
		self.bot = telegramBot()
		
		self.prices = {}
		# 시간 ## 현재가 # 5이평 # 20이평
		self.time = []
	
	def set_date(self):
		t = time.localtime()
		year = int(t.tm_year)
		mon = int(t.tm_mon)
		day = int(t.tm_mday)
		self.date = str(year * 10000 + mon * 100 + day)
	
	def get_time_with_sec(self):
		t = time.localtime()
		hour = int(t.tm_hour)
		min = int(t.tm_min)
		sec = int(t.tm_sec)
		if hour < 10:
			return "0" + str(hour * 10000 + min * 100 + sec)
		else:
			return str(hour * 10000 + min * 100 + sec)
	
	def get_time(self):
		t = time.localtime()
		hour = int(t.tm_hour)
		min = int(t.tm_min)
		sec = int(t.tm_sec)
		if hour < 10:
			return "0" + str(hour * 100 + min * 100)
		else:
			return str(hour * 100 + min)
	
	def m_ago(self, time, min=1):
		h = int(time[:2])
		m = int(time[-2:])
		
		m -= min
		if m < 0:
			h -= 1
			m = 60 - min
		
		return '{0:02d}'.format(h) + '{0:02d}'.format(m)
