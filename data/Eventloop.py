from PyQt5.QtCore import *

class Eventloop:
	def __init__(self):
		self.login = QEventLoop()
		self.account_info = QEventLoop()
		
		self.jongmok = QEventLoop()
		self.min_chart = QEventLoop()
		
		self.buy = {}
		
		self.sell = {}
		
		self.trade = []

		self.sem_buy = {}
		self.sem_sell = {}