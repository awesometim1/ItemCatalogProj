from models import User, Category, Item, Base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import datetime as dt

# Connect to Database and create database session
engine = create_engine('sqlite:///itemCatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# List to hold categories
cats = []

# Make Categories
soccer = Category(id = 1, name = "Soccer")
basketball = Category(id = 2, name = "Basketball")
baseball = Category(id = 3, name = "Baseball")
frisbee = Category(id = 4, name = "Frisbee")
snowboarding = Category(id = 5, name = "Snowboarding")
tennis = Category(id = 6, name = "Tennis")
cricket = Category(id = 7, name = "Cricket")
skateboarding = Category(id = 8, name = "Skateboarding")
hockey = Category(id = 9, name = "Hockey")

cats.extend((soccer, basketball, baseball, frisbee, snowboarding,
			tennis, cricket, skateboarding, hockey))

# Add Categories
session.add_all(cats)

# List to hold all items

items = []

# Make Items
hstick = Item(id = 1, name = "Stick", 
			  description = "Used for hitting the hockey puck and scoring goals.",
			  category = hockey)
goggles = Item(id = 2, name = "Goggles",
			   description = "Protective eyewear for snowboarding",
			   category = snowboarding)
snowboard = Item(id = 3, name = "Snowboard",
				 description = "A board that can glide on snow.",
				 category = snowboarding)
frisbeeitem = Item(id = 4, name = "Frisbee",
				   description = "A disc when thrown, glides through the air.",
				   category = frisbee)
jersey = Item(id = 5, name = "Jersey",
			  description = "A T-Shirt used to identify the team of a player.",
			  category = soccer)
bat = Item(id = 6, name = "Baseball",
		   description = "A wooden or metal stick that is used to hit a baseball",
		   category = baseball)

items.extend((hstick, goggles, snowboard, frisbeeitem, bat))

# Add Items

session.add_all(items)

session.commit()

