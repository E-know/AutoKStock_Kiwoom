import time
from config.telegramBot import *

class Stock:
	def __init__(self):
		self.jongmok = {}
		self.min_chart = {}
		self.average_5min = {}
		self.average_20min = {}
		
		self.date = None
		self.get_date()
		
		self.bot = telegramBot()
	
	def get_date(self):
		t = time.localtime()
		year = int(t.tm_year)
		mon = int(t.tm_mon)
		day = int(t.tm_mday)
		self.date = str(year * 10000 + mon * 100 + day)
		
	def get_time(self):
		t= time.localtime()
		hour = int(t.tm_hour)
		min = int(t.tm_min)
		if hour < 10:
			return "0" + str(hour * 10000 + min * 100)
		else:
			return str(hour * 10000 + min * 100)
	
	def set_average(self, code):
		price = []
		times = []
		for i, oldtime in enumerate(self.min_chart[code]):
			price.append(int(self.min_chart[code][oldtime]['현재가']))
			times.append(oldtime)
			if len(price) < 5:
				continue
			elif len(price) < 20:
				self.min_chart[code][times[-5]].update({'5평가': sum(price[-5:]) / 5, '20평가': None})
			if len(price) == 20:
				self.min_chart[code][times[-5]].update({'5평가': sum(price[-5:]) / 5})
				self.min_chart[code][times[0]].update({'20평가': sum(price) / 20})
				price.pop(0)
				times.pop(0)
	
	
	def when_buy(self, code):
		oldtime = None
		for i, now in enumerate(self.min_chart[code]):
			if oldtime is None:
				oldtime = now
				continue
			if self.min_chart[code][oldtime]['5평가'] is None or self.min_chart[code][oldtime]['20평가'] is None:
				oldtime = now
				continue
			if own:  # SELL
				# if self.min_chart[code][oldtime]['5평가'] > self.min_chart[code][oldtime]['20평가'] and self.min_chart[code][now]['5평가'] < self.min_chart[code][now]['20평가']:
				# if self.min_chart[code][oldtime]['5평가'] - self.min_chart[code][now]['5평가'] > self.min_chart[code][now]['5평가'] * 0.0075:
				if self.min_chart[code][oldtime]['5평가'] > self.min_chart[code][now]['5평가']:
					price += int(self.min_chart[code][now]['현재가'])
					total += price
					print("SELL %s %s %d" % (now, self.min_chart[code][now]['현재가'], price))
					own = False
			else:  # BUY
				if self.min_chart[code][oldtime]['5평가'] < self.min_chart[code][oldtime]['20평가'] and self.min_chart[code][now]['5평가'] > self.min_chart[code][now]['20평가'] and now[-6:] < "150000":
					print("BUY %s %s" % (now, self.min_chart[code][now]['시가']))
					price = int(self.min_chart[code][now]['시가']) * -1
					own = True
			oldtime = now
			
