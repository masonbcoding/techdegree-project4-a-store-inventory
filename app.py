#import all requirements

import csv
import datetime
import os
import re

from collections import OrderedDict
from decimal import Decimal
from peewee import *

# initialize Sqlite database
db = SqliteDatabase('inventory.db')


#create the Product model

class Product(Model):
    product_id = AutoField()
    product_name = CharField(max_length=30, unique=True)
    product_quantity = IntegerField()
    product_price = IntegerField()
    date_updated = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db

# read in the existing CSV data

def create_inventory():
    with open('inventory.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')

        for line in csv_reader:
            line['product_price'] = int(float(line['product_price'].strip("$")) * 100)
            line['product_quantity'] = int(line['product_quantity'])
            line['date_updated'] = datetime.datetime.strptime(line['date_updated'], "%m/%d/%Y")

# add the data from the .csv file into the database

            try:
                Product.create(product_name=line['product_name'],
                           product_price=line['product_price'],
                           product_quantity=line['product_quantity'],
                           date_updated=line['date_updated'])

            except IntegrityError:
                product_record = Product.get(product_name=line['product_name'])
                if product_record.date_updated < line['date_updated']:
                    product_record.product_name = line['product_name']
                    product_record.product_price = line['product_price']
                    product_record.product_quantity = line['product_quantity']
                    product_record.date_updated = line['date_updated']
                    product_record.save()
                else:
                    continue

# create a menu to make selections

def menu_loop():
    choice = None

    while choice != 'q':
        print("Type 'q' to exit.")
        for key, value in menu.items():
            print('{}) {}'.format(key, value.__doc__))
        choice = input('Action: ').lower().strip()
        while choice not in menu:
            if choice == 'q':
                break
            choice = input("That selection is invalid. Please select 'a' to add products; 'b' to backup inventory database; 'v' to view products; or 'q' to quit the application: ")
            
        if choice in menu:
            menu[choice]()
    clear()

# create a function to handle getting and displaying a product by its product_id

def view_products():
    """View products in inventory"""
    try:
        min_id = (Product.select().order_by(Product.product_id.asc()).get()).product_id
        max_id = (Product.select().order_by(Product.product_id.desc()).get()).product_id
        print(f"\nPlease choose product id between {min_id} & {max_id}")
        id = int(input("Choose product id: "))
        while id not in range(min_id, max_id+1):
            print("Your selection must be between {} and {}".format(min_id, max_id))
            id = int(input("Select product id: "))
        print(f"""\n-Product: {Product.get_by_id(id).product_name}
    -Quantity: {Product.get_by_id(id).product_quantity}
    -Price: {Product.get_by_id(id).product_price} cents
    -Date updated: {Product.get_by_id(id).date_updated}\n""")
        input("\nPress ENTER to continue")
        clear()
    except ValueError:
        print("That selection is invalid. Your selection must be an integer between {} and {}\n".format(min_id, max_id))
    
# add a new product to the database with menu option A

def add_product():
    """Add a new product to the inventory"""
    name = input("\nEnter the name of the new product: ")

    quantity = input("Enter the quantity of the new product: ")
    while quantity.isdigit() == False:
        print("Please enter a valid number.")
        quantity = input("Enter the quantity of the new product: ")
    quantity = int(quantity)

    price = input("Enter the price of the new product(in dollars): ").strip("$")
    while True:
        try:
            price = float(price)
            break
        except ValueError:
            print("Please enter a valid price")
            price = input("Enter the price of the new product: ")

    price = price * 100

    try:
        Product.create(product_name=name,
                       product_price=price,
                       product_quantity=quantity)
        latest_item = Product.select().order_by(Product.product_id.desc()).get()
        print(f"{latest_item.product_name.title()} has been added as the {latest_item.product_id}th item in the inventory.\n")

    except IntegrityError:
        to_update = Product.get(product_name=name)
        to_update.product_name = name
        to_update.product_price = price
        to_update.product_quantity = quantity
        to_update.date_updated = datetime.datetime.now()
        to_update.save()
        print(f"You just updated {to_update.product_name}\n")
    input("\nPress ENTER to continue")
    clear()

# backup the database (export new .csv) with menu option B

def create_backup():
    """Create an inventory backup"""
    with open('inventory_backup.csv', 'a') as csvfile:
        fieldnames = ['product_name', 'product_price', 'product_quantity', 'date_updated']
        backupwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)

        backupwriter.writeheader()
        for item in Product.select():
            backupwriter.writerow({
            'product_name': item.product_name,
            'product_price': round(Decimal(item.product_price / 100), 2),
            'product_quantity': item.product_quantity,
            'date_updated': item.date_updated.strftime("%m/%d/%Y")
            })
        print("\nProduct inventory backup file successfully created. \n")
    input("\nPress ENTER to continue")
    clear()

def clear ():
    os.system('cls' if os.name == 'nt' else 'clear')

# connect the database and create tables

def initialize():
    db.connect()
    db.create_tables([Product])
    create_inventory()

menu = OrderedDict([
        ('v', view_products),
        ('a', add_product),
        ('b', create_backup)
 ])


if __name__ == "__main__":
    initialize()
    menu_loop()
