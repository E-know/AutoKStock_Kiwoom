import telegram   #텔레그램 모듈을 가져옵니다.

class telegramBot():
	def __init__(self):
		my_token = 'Please Type Token Here'  # 토큰을 변수에 저장합니다.
		if my_token == ''Please Type Token Here'
			print("TOKEN ERROR")
		self.bot = telegram.Bot(token=my_token)
		
	def send(self, text=None):
		self.bot.sendMessage(chat_id= '1656561436', text=text)

	def get(self):
		updates = self.bot.getUpdates
		
		result = []
		for ele in updates:
			result.append(ele)
			
		return result
