class Time:
	
	hour = None
	minute = None
	
	@staticmethod
	def get_modified_time(time, minutes=0, hours=0):
		ex_min = time[-2:]
		ex_hour = time[:2]
		
		if minutes != 0:
			ex_min = int(ex_min) + minutes
			if ex_min < 0:
				ex_min = str(60 - ex_min)
				ex_hour = str(int(ex_hour) - 1)
			elif ex_min >= 60:
				ex_min = str(ex_min - 60)
				ex_hour = str(int(ex_hour) + 1)
			else:
				ex_min = str(ex_min)
		
		return ex_hour + ex_min
		