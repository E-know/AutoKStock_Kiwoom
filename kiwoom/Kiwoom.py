from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtTest

class Kiwoom(QAxWidget):
	def __init__(self):
		super().__init__()
		print("Kiwoom() class Start")
		
		self.screen_my_info = "2000"
		
		self.login_event_loop = QEventLoop()
		self.detail_account_info_event_loop = QEventLoop()
		
		self.account_num = None
		self.deposit = 0 # 예수금
		self.money_can_buy = 0 # 주문 가능 금액
		self.money_stock = 0 # 총평가금액
		self.profit_money = 0 # 손익금액
		self.profit_rate = 0.0 # 손익비율
		self.account_stock_dict = {} # 주식 보유
		
		
		self.get_ocx_instance()  # OCX 방식을 파이썬에 사용할 수 있게 변환해 주는 함수
		self.event_slots()  # 키움과 연결하기 위한 시그널 / 슬롯 모음
		self.signal_login_commConnect()  # 로그인 요청 함수
		self.get_account_info()
		print("계좌 보유 현황")
		self.get_stock_info()
	
	def get_ocx_instance(self):
		self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
	
	def event_slots(self):
		self.OnEventConnect.connect(self.login_slot)
		self.OnReceiveTrData.connect(self.trdata_slot)
		
	def signal_login_commConnect(self):
		self.dynamicCall("CommConnect()")
		self.login_event_loop.exec_()
	
	def login_slot(self, err_code): # err_cdoe : Int
		if err_code == 0:
			print("접속 완료")
		self.login_event_loop.exit()
		
	def trdata_slot(self, sCrNo, sRQName, sTrCode, sRecordName, sPrevNext):
		print("TRDATA : %s" % sRQName)
		if sRQName == "예수금상세현황요청":
			self.get_account_info_detail(sRQName, sTrCode)
		elif sRQName == "계좌평가잔고내역요청":
			self.get_stock_info_detail(sRQName, sTrCode, sPrevNext)
			
		
	def get_account_info(self):
		account_list = self.dynamicCall("GetLoginInfo(QString)", "ACCNO")
		self.account_num = account_list.split(';')[0]
		print("계좌번호 %s" % self.account_num)
		
		self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
		self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
		self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
		self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
		self.dynamicCall("CommRqData(QString, QString, int, QString)", "예수금상세현황요청", "opw00001", "0", self.screen_my_info)
		self.detail_account_info_event_loop.exec_()
		
	def get_account_info_detail(self, sRQName, sTrCode):
		self.deposit = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "예수금"))
		print("예수금 : %s" % self.deposit)
		self.money_can_buy = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "d+2출금가능금액"))
		print("주문 가능 금액 %s" % self.money_can_buy)
		self.detail_account_info_event_loop.exit()
		
	def get_stock_info(self, sPrevNext="0"):
		self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
		self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
		self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
		self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
		self.dynamicCall("CommRqData(QString, QString, int, QString)", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)
		self.detail_account_info_event_loop.exec_()
		
	def get_stock_info_detail(self, sRQName, sTrCode, sPrevNext="0"):
		self.profit_money = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가손익금액"))
		self.profit_rate = float(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총수익률(%)"))
		self.money_stock = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가금액"))
		
		rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
		for i in range(rows):
			code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호").strip()
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
			self.detail_account_info_event_loop.exit()