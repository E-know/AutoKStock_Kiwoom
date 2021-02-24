from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtTest

class Kiwoom(QAxWidget):
	def __init__(self):
		super().__init__()
		print("Kiwoom() class Start")
		
		self.login_event_loop = QEventLoop()
		
		self.account_num = None
		
		self.get_ocx_instance()  # OCX 방식을 파이썬에 사용할 수 있게 변환해 주는 함수
		self.event_slots()  # 키움과 연결하기 위한 시그널 / 슬롯 모음
		self.signal_login_commConnect()  # 로그인 요청 함수
	
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
		print("TRDATA %s" % sRQName)