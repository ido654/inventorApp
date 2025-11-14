from db import get_all_items , get_inventory_summary ,get_active_records
from datetime import datetime
from zoneinfo import ZoneInfo

data = get_active_records()
date = data[0][2]



def get_date(date):
    dt_il = date.astimezone(ZoneInfo("Asia/Jerusalem"))
    formatted = dt_il.strftime("%d-%m-%Y %H:%M")
    return formatted


print(get_date(date))