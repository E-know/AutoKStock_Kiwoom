import time
from config.telegramBot import *


class Stock:
	def __init__(self):
		self.jongmok = {}
		self.min_chart = {}

	def get_pd_new_iterrow(self, now_price, ave_price5=np.nan, ave_price10=np.nan, ave_price20=np.nan, ave_price30=np.nan, flag_buy=False, flag_sell=False):
		return [now_price, ave_price5, ave_price10, ave_price20, ave_price30, flag_buy, flag_sell]
	