class Account:
	def __init__(self):
		self.account_num = None
		self.deposit = 0  # 예수금
		self.money_can_buy = 0  # 주문 가능 금액
		self.money_stock = 0  # 총평가금액
		self.profit_money = 0  # 손익금액
		self.profit_rate = 0.0  # 손익비율
		
		self.stock_dict = {}  # 주식 보유
		