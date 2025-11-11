
from prettytable import PrettyTable
import psycopg


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


try:
    connection_url = "postgresql://bot_postgresql_ido_user:M9ZovEWuYki6dnJ97RNH4tAb1CxsQtPJ@dpg-d495kaqdbo4c7388sog0-a.oregon-postgres.render.com/bot_postgresql_ido"
    conn = psycopg.connect(connection_url)
    print("Connection to PostgreSQL successful!")

except psycopg.Error as e:
    print(f"Error connecting to PostgreSQL: {e}")




