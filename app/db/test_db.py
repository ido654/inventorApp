from db.db import (get_history_by_time )
from prettytable import PrettyTable

def create_table(items):
    if items:
        table = PrettyTable()
        table.field_names = items[0].keys()  # keys() כן עובד על sqlite3.Row

        for row in items:
            table.add_row([row[key] for key in row.keys()])  # ניגשים לפי המפתחות

        return(table.get_string())
    else:
        return("No items found.")



def make_table(fiels_names, rows ):
    table = PrettyTable()
    table.field_names = fiels_names
    for row in rows:
        table.add_row(row)
    return table.get_string()





