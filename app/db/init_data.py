from db import *
import csv 

csv_relations_path = 'app/files/Relations.csv'
csv_items_path = 'app/db/insert_data.py'

def insert_data_from_csv(csv_filepath):
    data = []
    with open(csv_filepath , 'r' , newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
        header = next(csv_reader)
        for row in csv_reader:
            data.append(row)

        return data
    

items_data = insert_data_from_csv(csv_items_path)
for row in items_data:
    item_id = int(row[1])
    owner = row[0]
    category = row[2]
    add_item(item_id , owner , category)

relations_data = insert_data_from_csv(csv_relations_path)
for row in relations_data:
    item_id = int(row[0])
    related_id = int(row[1])
    add_relation(item_id , related_id)
