import time
from config.telegramBot import *
import pandas as pd
import numpy as np
import datetime


class Stock:
	def __init__(self):
		self.jongmok = {}
		self.min_chart = {}
	
	# 현재가 | 5분 이동평균선 | 10분 이동평균선 | 20분 이동평균선 | 30분 이동평균선 | 매수 시도 | 매도 시도 |
	def get_pd_new_iterrow(self, now_price, ave_price5=np.nan, ave_price10=np.nan, ave_price20=np.nan, ave_price30=np.nan, flag_buy=False, flag_sell=False):
		return [now_price, ave_price5, ave_price10, ave_price20, ave_price30, flag_buy, flag_sell]
	
	def get_pd(self):
		result = pd.DataFrame(index=['시간'], columns=['현재가', '5이평', '10이평', '20이평', '30이평', '매수', '매도'])
		return result