import telegram   #텔레그램 모듈을 가져옵니다.

class telegramBot():
	def __init__(self):
		my_token = '1687438841:AAGgSeK0nGH9QsRPxkT-X8iK6Ud0JUsSEEw'  # 토큰을 변수에 저장합니다.
		self.bot = telegram.Bot(token=my_token)
		
	def send(self, text=None):
		self.bot.sendMessage(chat_id= '1656561436', text=text)

	def get(self):
		updates = self.bot.getUpdates
		
		result = []
		for ele in updates:
			result.append(ele)
			
		return result