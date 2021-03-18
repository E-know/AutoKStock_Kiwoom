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
		
		self.oldtime = {}
		self.time = []
	
		self.flag = {}
		
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
		t= time.localtime()
		hour = int(t.tm_hour)
		min = int(t.tm_min)
		sec = int(t.tm_sec)
		if hour < 10:
			return "0" + str(hour * 100 + min * 100)
		else:
			return str(hour * 100 + min )
		
	def get_minustime(self):
		t = time.localtime()
		hour = int(t.tm_hour)
		min = int(t.tm_min)
		
		if min > 0:
			min -= 1
		else:
			hour -= 1
			min = 59
			
		if hour < 10:
			return "0" + str(hour * 10000 + min)
		else:
			return str(hour * 10000 + min)