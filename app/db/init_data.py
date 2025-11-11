from db import *
import csv 

csv_relations_path = 'app/csvfiles/Relations.csv'
csv_items_path = 'app/csvfiles/Items.csv'

def insert_data_from_csv(csv_filepath):
    data = []
    with open(csv_filepath , 'r' , newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
        header = next(csv_reader)
        for row in csv_reader:
            print((row[0] , row[1]))

        return data
#היערות לקוד:
# לא לאפשר להכניס item_id שכבר הוכנס.
#לשים לב שהפרמטרים עכשיו בget_item הם מסוג string





items_data = insert_data_from_csv(csv_items_path)
insert_data_from_csv(csv_relations_path)

relations_data = insert_data_from_csv(csv_relations_path)
add_many_relations(relations_data)
print("success")

