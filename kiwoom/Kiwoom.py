from PyQt5.QAxContainer import *
from PyQt5.QtTest import *
from config.kiwoomType import *
from config.log_class import *
from config.telegramBot import *
from data.Account import *
from data.Screen import *
from data.Stock import *
from data.Eventloop import *


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
		self.isOpen = 4
		
		self.get_ocx_instance()  # OCX 방식을 파이썬에 사용할 수 있게 변환해 주는 함수
		self.event_slots()  # 키움과 연결하기 위한 시그널 / 슬롯 모음
		self.real_event_slot()
		self.signal_login_commConnect()  # 로그인 요청 함수
		# self.get_account_info()
		# self.get_stock_info()
		
		# QTest.qWait(1000)
		self.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen.isOpen, ' ', self.realType.REALTYPE['장시작시간']['장운영구분'], "0")
		
		self.running()
	
		# self.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen.realData, '005880', self.realType.REALTYPE['주식체결']['현재가'], "0")
	
	def running(self):
		while True:
			if self.isOpen == 3:
				# 장 중
				self.bot.send("장이 열렸습니다.")
				while self.stock.get_time() > "092000":
					pass
				self.get_jongmok()
				self.bot.send("프로그램 매매를 본격적으로 시작합니다")
				while self.isOpen == 3:
					for code in self.stock.jongmok.keys():
						if code in self.account.stock_dict.keys():
							self.have_to_sell(code)
					for code in self.account.stock_dict.keys():
						self.have_to_buy(code)
						
			elif self.isOpen == 4:
				pass # 장 종료
			elif self.isOpen == 0:
				print(self.stock.get_time())
			elif self.isOpen == 2:
				pass # 장 종료 10분전 동시호가
	
	def get_ocx_instance(self):
		self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
	
	def event_slots(self):
		self.OnEventConnect.connect(self.login_slot)
		self.OnReceiveTrData.connect(self.trdata_slot)
		self.OnReceiveMsg.connect(self.msg_slot)
	
	def real_event_slot(self):
		self.OnReceiveRealData.connect(self.realdata_slot)  # 실시간 이벤트 연결
	
	def realdata_slot(self, sCode, sRealType, sRealData):
		if sRealType == '주식체결':
			self.real_chegul(sCode, sRealType, sRealData)
		elif sRealType == '장시작시간':
			self.real_isOpen(sCode, sRealType, sRealData)
	
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
	
	def msg_slot(self, sCrNo, sRQName, sTrCode, msg):
		self.log.debug("[Screen : %s] %s %s %s" % (sCrNo, sRQName, sTrCode, msg))
	
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
			if code in self.account_stock_dict:
				continue
			name = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
			stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")
			profit = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "평가손익")
			earn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "수익률(%)")
			
			self.account.stock_dict[code] = {}
			self.account.stock_dict[code].update({"종목명": name.strip()})
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
		for i in range(5):
			data = {}
			code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드").strip()
			name = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명").strip()
			price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가").strip()[1:]
			
			data.update({"종목명": name, "현재가": price})
			self.stock.jongmok[code] = data
		self.loop.jongmok.exit()
	
	def min_chart(self, code):
		self.dynamicCall("SetInputValue(QString, QString", "종목코드", code)
		self.dynamicCall("SetInputValue(QString, QString", "틱범위", "1")
		self.dynamicCall("SetInputValue(QString, QString", "수정주가구분", "0")
		
		while self.loop.min_chart.isRunning():
			pass
		self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식분봉차트조회요청", "opt10080", "0", self.screen.min_chart)
		self.loop.min_chart.exec_()
	
	def tr_min_chart(self, sTrCode, sRQName):
		self.dynamicCall("DisconnectRealData(QString)", self.screen.min_chart)
		code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드").strip()
		rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)  # 900
		self.stock.min_chart[code] = {}
		for i in range(378):
			data = {}
			time = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결시간").strip()
			if time[0:8] != self.stock.date:
				break
			start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가").strip()[1:]
			now_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가").strip()[1:]  # 종가
			high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가").strip()[1:]
			low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가").strip()[1:]
			
			data.update({'시가': start_price, '현재가': now_price, '고가': high_price, '저가': low_price})
			self.stock.min_chart[code].update({time: data})
		
		self.stock.min_chart[code] = dict(sorted(self.stock.min_chart[code].items()))
		self.loop.min_chart.exit()
		
		self.stock.set_average(code)
	
	def real_chegul(self, sCode, sRealType, sRealData):
		time = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['체결시간'])
		price = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['현재가'])
	
	def buy_Stock(self, sCode, nQty, nPrice, sOrderNum=""):
		status = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", "매수", self.screen_buy_sell, self.account_num, 1, sCode, nQty, nPrice, '00', sOrderNum)
		if status == 0:
			self.get_account_info()
			msg = "[매수] " + self.stock.min_chart[sCode]['종목명'] + "[" + sCode + "]" + " Price : " + str(nPrice) + " Quantity : " + nQty
			self.log.debug(msg)
			self.bot.send(msg)
			self.account.stock_dict[sCode] = self.stock.jongmok[sCode]
			self.account.stock_dict[sCode].update({'보유수량' : str(nQty)})
		elif status == -308:
			self.log.debug("%s 매수 중에 에러가 발생했습니다. 사유 : 1초에 5회이상 구매시도" % sCode)
		else:
			self.log.debug("%s 구매중에 에러가 발생했습니다." % sCode)
			
	def sell_stock(self, sCode, nPrice, sOrderNum=""):
		status = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", "매도", self.screen_buy_sell, self.account_num, 2, sCode, int(self.account.stock_dict[sCode]['보유수량']), nPrice, '00', sOrderNum)
		if status == 0:
			self.get_account_info()
			msg = "[매도] " + self.account[sCode]['종목명'] + "[" + sCode + "]" + " Price : " + str(nPrice) + " Quantity : " + str(self.account.stock_dict[sCode]['보유수량'])
			self.log.debug(msg)
			self.bot.send(msg)
			self.account.stock_dict.pop(sCode)
		elif status == -308:
			self.log.debug("%s[%s] 매도 중에 에러가 발생했습니다. 사유 : 1초에 5회이상 구매시도" % (self.account.stock_dict[sCode]['종목명'], sCode))
		else:
			self.log.debug("%s[%s] 매도중에 알 수 없는 에러가 발생했습니다. ErrorCode %d" % (self.account.stock_dict[sCode]['종목명'], sCode, status))
		
	def real_isOpen(self, sCode, sRealType, sRealData):
		self.isOpen = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['장운영구분']).strip()
		
	def have_to_sell(self, code):
		now = None
		for oldtime in self.stock.min_chart[code]:
			if now is None:
				now = oldtime
				continue
			if self.stock.min_chart[code][oldtime]['5평가'] is None or self.stock.min_chart[code][now]['5평가'] is None:
				self.log.debug("5평가 구분에서 실수가 있습니다.")
				
			if self.stock.min_chart[code][oldtime]['5평가'] > self.stock.min_chart[code][now]['5평가']:
				self.sell_stock(code, int(self.stock.min_chart[code][now]['시가']))
			
			return
	
	def have_to_buy(self, code):
		now = None
		for oldtime in self.stock.min_chart[code]:
			if now is None:
				now = oldtime
				continue
			if self.stock.min_chart[code][oldtime]['5평가'] is None or self.stock.min_chart[code][now]['5평가'] is None:
				self.log.debug("5평가 구분에서 실수가 있습니다.")
				
			if self.stock.min_chart[code][oldtime]['5평가'] < self.stock.min_chart[code]['20평가'] and self.stock.min_chart[code][now]['5평가'] > self.stock.min_chart[code][now]['20평가'] :
				self.buy_Stock(code, self.account.money_can_buy / 5 / int(self.stock.min_chart[code][now]['현재가']), int(self.stock.min_chart[code][now]['현재가']))
				