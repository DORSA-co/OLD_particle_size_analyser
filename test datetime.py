from datetime import datetime
start_date = '1396/1/1'
start_date_datetime_obj = datetime.strptime(start_date, "%Y/%m/%d")
print(start_date_datetime_obj)