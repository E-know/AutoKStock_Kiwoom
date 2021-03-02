from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from PyQt5 import QtCore
from PyQt5.QtTest import *
from config.kiwoomType import *


class Kiwoom(QAxWidget):
	def __init__(self):
		super().__init__()
		print("Kiwoom() class Start")
		
		self.realType = RealType()
		
		self.screen_my_info = "2000"
		self.screen_chart_info = "4000"
		self.screen_start_stop_real = "1000"
		self.screen_buy_sell = "5000"
		
		self.event_loop_login = QEventLoop()
		self.event_loop_detail_account_info = QEventLoop()
		self.event_loop_day_chart = QEventLoop()
		
		self.account_num = None
		self.deposit = 0  # 예수금
		self.money_can_buy = 0  # 주문 가능 금액
		self.money_stock = 0  # 총평가금액
		self.profit_money = 0  # 손익금액
		self.profit_rate = 0.0  # 손익비율
		self.account_stock_dict = {}  # 주식 보유
		self.stock_day_chart_dict = {}
		
		self.get_ocx_instance()  # OCX 방식을 파이썬에 사용할 수 있게 변환해 주는 함수
		self.event_slots()  # 키움과 연결하기 위한 시그널 / 슬롯 모음
		self.real_event_slot()
		self.signal_login_commConnect()  # 로그인 요청 함수
		self.get_account_info()
		print("계좌 보유 현황")
		# QTimer.singleShot(3600, self.get_stock_info)
		# QTest.qWait(10000)
		# self.get_day_chart(code="005930") # 삼성전자
		
		# QTest.qWait(5000)
		
		# result = self.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_start_stop_real, ' ', self.realType.REALTYPE['장시작시간']['장운영구분'], "0") # 공백이여야한다. None이 아닌
		# print(result)
		
		self.buyStock("005930", 1, 80000)
	
	def get_ocx_instance(self):
		self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
	
	def event_slots(self):
		self.OnEventConnect.connect(self.login_slot)
		self.OnReceiveTrData.connect(self.trdata_slot)
	
	def real_event_slot(self):
		self.OnReceiveRealData.connect(self.realdata_slot)  # 실시간 이벤트 연결
	
	def signal_login_commConnect(self):
		self.dynamicCall("CommConnect()")
		self.event_loop_login.exec_()
	
	def login_slot(self, err_code):  # err_code : Int
		if err_code == 0:
			print("접속 완료")
		self.event_loop_login.exit()
	
	def trdata_slot(self, sCrNo, sRQName, sTrCode, sRecordName, sPrevNext):
		print("TRDATA : %s" % sRQName)
		if sRQName == "예수금상세현황요청":
			self.get_account_info_detail(sRQName, sTrCode)
		elif sRQName == "계좌평가잔고내역요청":
			self.get_stock_info_detail(sRQName, sTrCode, sPrevNext)
		elif sRQName == "주식일봉차트조회요청":
			self.get_day_chart_detail(sTrCode, sRQName)
	
	def realdata_slot(self, sCode, sRealType, sRealData):
		if sRealType == "장시작시간":
			self.isTime()
		elif sRealType == "주식체결":
			self.stockSigning()
	
	def get_account_info(self):
		account_list = self.dynamicCall("GetLoginInfo(QString)", "ACCNO")
		self.account_num = account_list.split(';')[0]
		print("계좌번호 %s" % self.account_num)
		
		self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
		self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
		self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
		self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
		self.dynamicCall("CommRqData(QString, QString, int, QString)", "예수금상세현황요청", "opw00001", "0", self.screen_my_info)
		self.event_loop_detail_account_info.exec_()
	
	def get_account_info_detail(self, sRQName, sTrCode):
		self.deposit = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "예수금"))
		print("예수금 : %s" % self.deposit)
		self.money_can_buy = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "d+2출금가능금액"))
		print("주문 가능 금액 %s" % self.money_can_buy)
		self.event_loop_detail_account_info.exit()
	
	def get_stock_info(self, sPrevNext="0"):
		self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
		self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
		self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
		self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
		self.dynamicCall("CommRqData(QString, QString, int, QString)", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)
		self.event_loop_detail_account_info.exec_()
	
	def get_stock_info_detail(self, sRQName, sTrCode, sPrevNext="0"):
		self.profit_money = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가손익금액"))
		self.profit_rate = float(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총수익률(%)"))
		self.money_stock = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가금액"))
		
		rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
		for i in range(rows):
			code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호").strip()[1:]
			if code in self.account_stock_dict:
				pass
			name = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
			stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")
			profit = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "평가손익")
			earn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "수익률(%)")
			
			self.account_stock_dict[code] = {}
			self.account_stock_dict[code].update({"종목명": name.strip()})
			self.account_stock_dict[code].update({"보유수량": int(stock_quantity.strip())})
			self.account_stock_dict[code].update({"평가손익": int(profit.strip())})
			self.account_stock_dict[code].update({"수익률(%)": float(earn_rate.strip())})
			print("Code %s : " % code, end='')
			print(self.account_stock_dict[code])
		
		if sPrevNext == "2":
			self.get_stock_info(sPrevNext="2")
		else:
			self.event_loop_detail_account_info.exit()
	
	def get_code_list_by_market(self, market_code):  # [Market Code]	0 : 코스피	10 : 코스닥	3 : ELW	8 : ETF
		code_list = self.dynamicCall("GetCodeListByMarket(QString", market_code)
		return code_list.split(';')[:-1]
	
	def get_day_chart(self, code, date=None, sPrevNext="0"):
		self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
		self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", 1)
		if date is None:
			self.dynamicCall("SetInputValue(QString, QString)", "기준일자", "")
		self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식일봉차트조회요청", "opt10081", sPrevNext, self.screen_chart_info)
		self.event_loop_day_chart.exec_()
	
	def get_day_chart_detail(self, sTrCode, sRQName):
		code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드").strip()
		print(code)
		cnt = int(self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName))
		print(cnt)
		self.stock_day_chart_dict[code] = {}
		if code in self.stock_day_chart_dict.keys():
			for i in range(cnt):
				date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자").strip()
				value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량").strip()
				current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가").strip()  # 사실상 종가
				start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가").strip()
				high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가").strip()
				low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가").strip()
				
				data = {}
				data.update({"거래량": int(value)})
				data.update({"종가": int(current_price)})
				data.update({"시가": int(start_price)})
				data.update({"고가": int(high_price)})
				data.update({"저가": int(low_price)})
				print(data)
				self.stock_day_chart_dict[code][date] = data
		
		self.event_loop_day_chart.exit()
	
	def isTime(self):
		value = value = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE['장시작시간']['장운영구분'])
		if value == '0':
			print("장 시작 전")
		elif value == '3':
			print("장 시작")
		elif value == "2":
			print("장 종료, 동시호가로 넘어감")
		elif value == "4":
			print("3시30분 장 종료")
	
	def stockSigning(self):
		pass
	
	def buyStock(self, sCode, nQty, nPrice, sOrderNum=""):
		if nPrice == 0:
			order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", ["매수", self.screen_buy_sell, self.account_num, 1, sCode, nQty, nPrice, '03', sOrderNum])
		else:
			order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", ["매수", self.screen_buy_sell, self.account_num, 1, sCode, nQty, nPrice, '00', sOrderNum])
		
		if sOrderNum == "":
			order_type = "신규매수"
		else:
			order_type = "매수정정"
		
		if order_success == 0:
			print("[%s %s] 주문 성공" % (order_type, sCode))
		else:
			print("[%s|%s] 주문 실패" % (order_type, sCode))
	
	def sellStock(self, sCode, nQty, nPrice, sOrderNum=""):
		if nPrice == 0:
			order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", ["매도", self.screen_buy_sell, self.account_num, 2, sCode, nQty, nPrice, '03', sOrderNum])  # 시장가 신규 매도
		else:
			order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", ["매도", self.screen_buy_sell, self.account_num, 2, sCode, nQty, nPrice, '00', sOrderNum])  # 지정가 신규 매도
		
		if sOrderNum == "":
			order_type = "신규매도"
		else:
			order_type = "매도정정"
			
		if order_success == 0:
			print("[%s|%s] 주문 성공", order_type, sCode)
		else:
			print("[%s|%s] 주문 실패", order_type, sCode)
