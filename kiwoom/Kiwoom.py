from PyQt5.QAxContainer import *
from PyQt5.QtTest import *
from config.kiwoomType import *
from config.log_class import *
from config.telegramBot import *
from data.Account import *
from data.Screen import *
from data.Stock import *
from data.Eventloop import *
import threading
import pandas as pd
import numpy as np

class Kiwoom(QAxWidget):
	def __init__(self):
		super().__init__()
		self.log = Logging().logger
		self.log.debug("Kiwoom() class Start")
		
		self.bot = telegramBot()
		self.bot.send(text="키움 자동화 매매 프로그램이 시작되었습니다.")
		
		self.realType = RealType()
		self.account = Account()
		self.screen = Screen()
		self.stock = Stock()
		self.loop = Eventloop()
		self.isOpen = '3'
		self.oldtime = None
		
		self.get_ocx_instance()  # OCX 방식을 파이썬에 사용할 수 있게 변환해 주는 함수
		self.event_slots()  # 키움과 연결하기 위한 시그널 / 슬롯 모음
		self.real_event_slot()
		self.signal_login_commConnect()  # 로그인 요청 함수
		self.get_account_info()
		self.get_stock_info()
		
		QTest.qWait(1000)
		
		self.running()
		print("MAIN CODE IS END")
	
	def running(self):
		if self.isOpen == '3':
			while self.stock.get_time_with_sec() <= "090000":
				pass
			print("START")
			self.get_jongmok()
			self.dynamicCall("DisconnectRealData(QString)", self.screen.jongmok)
			
			for code in self.stock.jongmok:
				self.min_chart(code)
				self.dynamicCall("DisconnectRealData(QString)", self.screen.min_chart)
				QTest.qWait(1000)
			
			self.dynamicCall("DisconnectRealData(QString)", self.screen.jongmok)
			self.dynamicCall("DisconnectRealData(QString)", self.screen.min_chart)
			self.dynamicCall("SetRealRemove(QString, QString", "ALL", "ALL")
			QTest.qWait(2000)
			print(self.stock.jongmok)
			
			for code in self.stock.jongmok:
				self.dynamicCall("SetRealReg(QString, QString, QString, QString)", [self.screen.realchart, code, self.realType.REALTYPE['주식체결']['현재가'], "1"])
		
		
		elif self.isOpen == '2':
			self.log.debug('동시호가에 진입했습니다.')
			self.isOpen = None
			
			while self.isOpen is None:
				pass
		# 동시호가
		elif self.isOpen == '4':
			self.log.debug('장이 마감되었습니다.')
			self.bot.send("장이 마감되었습니다.")
			self.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen.open, '005930', self.realType.REALTYPE['장시작시간']['장운영구분'], "0")
			while self.isOpen == '4':
				pass
		elif self.isOpen == '0':
			while self.isOpen == '0':
				pass
	
	# 장 마감
	
	def get_ocx_instance(self):
		self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
	
	def event_slots(self):
		self.OnEventConnect.connect(self.login_slot)
		self.OnReceiveTrData.connect(self.trdata_slot)
		self.OnReceiveMsg.connect(self.msg_slot)
	
	def real_event_slot(self):
		self.OnReceiveRealData.connect(self.realdata_slot)  # 실시간 이벤트 연결
		self.OnReceiveChejanData.connect(self.chejan_slot)
	
	def realdata_slot(self, sCode, sRealType, sRealData):
		if sRealType == '주식체결':
			if sCode in self.stock.jongmok.keys():
				self.real_jusikchegul(sCode, sRealType, sRealData)
			else:
				self.dynamicCall("SetRealRemove(QString, QString)", "ALL", sCode)
		elif sRealType == '장시작시간':
			self.real_open(sCode, sRealType, sRealData)
	
	def get_name(self, code):
		return self.dynamicCall("GetMasterCodeName(QString)", code).strip()
	
	def real_open(self, sCode, sRealType, sRealData):
		self.isOpen = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['장운영구분']).strip()
		self.log.debug("장 운영 구분 : " + self.isOpen)
	
	def signal_login_commConnect(self):
		self.dynamicCall("CommConnect()")
		self.loop.login.exec_()
	
	def login_slot(self, err_code):  # err_code : Int
		if err_code == 0:
			self.log.debug("키움 Open API 접속 완료")
		self.loop.login.exit()
	
	def trdata_slot(self, sCrNo, sRQName, sTrCode, sRecordName, sPrevNext):
		print("TRDATA : %s" % sRQName)
		if sRQName == "예수금상세현황요청":
			self.tr_get_account_info(sRQName, sTrCode)
		elif sRQName == "계좌평가잔고내역요청":
			self.tr_get_stock_info(sRQName, sTrCode, sPrevNext)
		elif sRQName == '전일대비등락률상위요청':
			self.tr_get_jongmok(sTrCode, sRQName)
		elif sRQName == '주식분봉차트조회요청':
			self.tr_min_chart(sTrCode, sRQName)
		elif sRQName == '매수':
			pass
		elif sRQName == '매도':
			pass
	
	def msg_slot(self, sCrNo, sRQName, sTrCode, msg):
		self.log.debug("[Screen : %s] %s %s %s" % (sCrNo, sRQName, sTrCode, msg))
	
	def chejan_slot(self, sGubun, nItemCnt, sFidList):
		if int(sGubun) == 0:
			price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결가']).strip()
			if price == '':
				return
			code = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목코드']).strip()[1:]
			name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목명']).strip()
			quantity = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결량']).strip()
			status = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['매도수구분']).strip()
			if status == '2':  # 매수
				self.account.stock_dict[code] = {'종목명': name, '보유수량': int(quantity), '체결가': price}
				msg = "채잔-[매수]" + name + " 체결가 : " + price + " 수량 : " + quantity
				self.bot.send(msg)
				self.log.debug(msg)
			elif status == '1':  # 매도
				# earn = (int(price) - int(self.account.stock_dict[code]['체결가']) * 1.015 - int(price) * 0.315) * int(quantity)
				msg = "채잔-[매도]" + name + " 체결가 : " + price + " 수량 : " + quantity
				self.account.stock_dict.pop(code)
				self.bot.send(msg)
				self.log.debug(msg)
	
	def get_account_info(self):
		account_list = self.dynamicCall("GetLoginInfo(QString)", "ACCNO")
		self.account.account_num = account_list.split(';')[0]
		print("계좌번호 %s" % self.account.account_num)
		
		self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account.account_num)
		self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
		self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
		self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
		self.dynamicCall("CommRqData(QString, QString, int, QString)", "예수금상세현황요청", "opw00001", "0", self.screen.my_info)
		while self.loop.account_info.isRunning():
			pass
		self.loop.account_info.exec_()
	
	def tr_get_account_info(self, sRQName, sTrCode):
		self.account.deposit = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "예수금"))
		self.account.money_can_buy = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "d+2출금가능금액"))
		self.loop.account_info.exit()
	
	def get_stock_info(self, sPrevNext="0"):
		self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account.account_num)
		self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
		self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
		self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
		
		while self.loop.account_info.isRunning():
			pass
		self.dynamicCall("CommRqData(QString, QString, int, QString)", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen.my_info)
		self.loop.account_info.exec_()
	
	def tr_get_stock_info(self, sRQName, sTrCode, sPrevNext="0"):
		self.account.profit_money = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가손익금액"))
		self.account.profit_rate = float(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총수익률(%)"))
		self.account.money_stock = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가금액"))
		
		rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
		if rows == 0:
			self.log.debug("No Stock!")
		for i in range(rows):
			code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호").strip()[1:]
			if code in self.account.stock_dict:
				continue
			name = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
			price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입가").strip()
			stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")
			profit = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "평가손익")
			earn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "수익률(%)")
			
			self.account.stock_dict[code] = {}
			self.account.stock_dict[code].update({"종목명": name.strip()})
			self.account.stock_dict[code].update({'체결가': price})
			self.account.stock_dict[code].update({"보유수량": int(stock_quantity.strip())})
			self.account.stock_dict[code].update({"평가손익": int(profit.strip())})
			self.account.stock_dict[code].update({"수익률(%)": float(earn_rate.strip())})
			
			self.log.debug(self.account.stock_dict[code])
		
		if sPrevNext == "2":
			self.get_stock_info(sPrevNext="2")
		else:
			self.loop.account_info.exit()
	
	def get_jongmok(self):
		self.dynamicCall("SetInputValue(QString, QString)", "시장구분", "000")
		self.dynamicCall("SetInputValue(QString, QString)", "정렬구분", "1")
		self.dynamicCall("SetInputValue(QString, QString)", "거래량조건", "0000")
		self.dynamicCall("SetInputValue(QString, QString)", "종목조건", "4")
		self.dynamicCall("SetInputValue(QString, QString)", "신용조건", "0")
		self.dynamicCall("SetInputValue(QString, QString)", "상하한포함", "0")  # 상하한가 불포함
		self.dynamicCall("SetInputValue(QString, QString)", "가격조건", "0")
		self.dynamicCall("SetInputValue(QString, QString)", "거래대금조건", "0")
		
		self.dynamicCall("CommRqData(QString, QString, int, QString)", "전일대비등락률상위요청", "opt10027", "0", self.screen.jongmok)
		self.loop.jongmok.exec_()
	
	def tr_get_jongmok(self, sTrCode, sRQName):
		self.log.debug("전일대비등략률상위요청[TR]")
		for i in range(100):
			if len(self.stock.jongmok) == 5:
				break
			
			data = {}
			code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드").strip()
			name = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명").strip()
			if name.__contains__('ETN') or name.__contains__('KODEX') or name.__contains__('TIGER'):
				continue
			price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가").strip()[1:]
			
			data.update({"종목명": name, "현재가": price})
			self.stock.jongmok[code] = data
			
			self.stock.min_chart[code] = pd.DataFrame(index=['시간'], columns=['현재가', '5이평', '20이평', '매수', '매도'])
			self.loop.sem_buy[code] = threading.Semaphore(1)
			self.loop.sem_sell[code] = threading.Semaphore(1)
		
		self.loop.jongmok.exit()
	
	def min_chart(self, code):
		
		self.dynamicCall("SetInputValue(QString, QString", "종목코드", code)
		self.dynamicCall("SetInputValue(QString, QString", "틱범위", "1")
		self.dynamicCall("SetInputValue(QString, QString", "수정주가구분", "0")
		
		self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식분봉차트조회요청", "opt10080", "0", self.screen.min_chart)
		while self.loop.min_chart.isRunning():
			pass
		self.loop.min_chart.exec_()
	
	def tr_min_chart(self, sTrCode, sRQName):
		code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드").strip()
		# rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)  # 900
		for i in range(19, -1, -1):
			time = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결시간").strip()
			if time[0:8] != self.stock.date:
				continue
			now_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가").strip()[1:]  # 종가
			self.stock.min_chart[code].loc[time[-6:-2]] = [int(now_price), np.nan, np.nan, False, False]
		
		self.loop.min_chart.exit()
	
	def buy_Stock(self, sCode, nQty, time, nPrice=0, sOrderNum=""):  # sOrderNum 매수정정 때 쓰임
		self.loop.sem_buy[sCode].acquire()
		
		if sCode in self.account.stock_dict or self.stock.min_chart[sCode].loc[time]['매수'] is True or self.stock.min_chart[sCode].loc[time]['매도'] is True:
			self.loop.sem_buy[sCode].release()
			return
		
		if sCode not in self.account.stock_dict:
			status = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", ["매수", self.screen.buy_sell, self.account.account_num, 1, sCode, nQty, nPrice, '00', sOrderNum])
			# 03 시장가 / 00 지정가
			if status == 0:
				self.log.debug("[매수]" + sCode + "주문이 접수되었습니다.")
				self.stock.min_chart[sCode].loc[time]['매수'] = True
			elif status == -308:
				self.log.debug("%s 매수 중에 에러가 발생했습니다. 사유 : 1초에 5회이상 매도/수 시도" % sCode)
			else:
				self.log.debug("%s 구매중에 에러가 발생했습니다." % sCode)
		
		self.loop.sem_buy[sCode].release()
	
	def sell_stock(self, sCode, time, nPrice=0, sOrderNum=""):
		self.loop.sem_sell[sCode].acquire()
		
		if self.stock.min_chart[sCode].loc[time]['매수'] is True or self.stock.min_chart[sCode].loc[time]['매도'] is True:
			self.loop.sem_sell[sCode].release()
			return
		
		if sCode in self.account.stock_dict:
			if '보유수량' in self.account.stock_dict[sCode]:
				status = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", ["매도", self.screen.buy_sell, self.account.account_num, 2, sCode, self.account.stock_dict[sCode]['보유수량'], nPrice, '03', sOrderNum])
				# 03 : 시장가 / 00 : 지정가
				if status == 0:
					self.log.debug("[매도]" + sCode + "주문이 접수되었습니다.")
					self.stock.min_chart[sCode].loc[time]['매도'] = True
				elif status == -308:
					self.log.debug("[%s] 매도 중에 에러가 발생했습니다. 사유 : 1초에 5회이상 매도/수 시도" % (sCode))
				else:
					self.log.debug("%s[%s] 매도중에 알 수 없는 에러가 발생했습니다. ErrorCode %d" % (self.account.stock_dict[sCode]['종목명'], sCode, status))
		
		self.loop.sem_sell[sCode].release()
	
	def have_to_sell(self, sCode, time, price):
		one_m_ago = len(self.stock.min_chart[sCode].index) - 1
		two_m_ago = one_m_ago - 1
		if self.stock.min_chart[sCode].iloc[one_m_ago]['5이평'] < self.stock.min_chart[sCode].iloc[two_m_ago]['5이평'] or self.stock.min_chart[sCode].loc[time]['20이평'] > self.stock.min_chart[sCode].loc[time]['5이평']:
			self.sell_stock(sCode, time)
	
	def have_to_buy(self, sCode, time, price):
		one_m_ago = self.stock.m_ago(time)
		if one_m_ago not in self.stock.min_chart[sCode].index:
			return
		if self.stock.min_chart[sCode].loc[time, '5이평'] > self.stock.min_chart[sCode].loc[time, '20이평'] and \
			self.stock.min_chart[sCode].loc[one_m_ago, '5이평'] < self.stock.min_chart[sCode].loc[one_m_ago, '20이평']:
			self.buy_Stock(sCode, 10, time, price)
	
	def real_jusikchegul(self, sCode, sRealType, sRealData):
		print(sCode)
		time = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['체결시간'])[:4]  # 시 분
		price = int(self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['현재가'])[1:])
		
		if time not in self.stock.min_chart[sCode].index:
			self.stock.min_chart[sCode].loc[time] = [price, np.nan, np.nan, False, False]
		
		if len(self.stock.min_chart[sCode].index) >= 20:
			self.stock.min_chart[sCode].loc[time, '현재가'] = price
			self.stock.min_chart[sCode].loc[time, '5이평'] = self.stock.min_chart[sCode]['현재가'][-5:].mean()
			self.stock.min_chart[sCode].loc[time, '20이평'] = self.stock.min_chart[sCode]['현재가'][-20:].mean()
	
			if sCode in self.account.stock_dict:
				self.have_to_sell(sCode, time, price)
			else:
				self.have_to_buy(sCode, time, price)