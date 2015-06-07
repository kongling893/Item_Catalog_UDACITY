from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, ToyShop, ToyItem, User

engine = create_engine('sqlite:///toyshop.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

picture = "https://lh3.googleusercontent.com/-XdUIqdMkCWA/AAAAAAAAAAI/AAAAAAAAAAA/4252rscbv5M/photo.jpg"

user1 = User(name="Wei", email="engineer@gmai.com", picture = picture)
session.add(user1)
session.commit()

user2 = User(name="Jun", email="coder@gmai.com", picture = picture)
session.add(user2)
session.commit()



shop1 = ToyShop(name="Lego Shop",description = "First shop", user_id = user1.id )
session.add(shop1)
session.commit()

shop2 = ToyShop(name="SuperHero Shop",description = "Second shop", user_id = user2.id )
session.add(shop2)
session.commit()


toy1 = ToyItem(name="Lego 1 ",description = "plastic toys.", user_id = user1.id, price = "11", shop_id = shop1.id)
session.add(toy1)
session.commit()

toy2 = ToyItem(name="Lego 2 ",description = "plastic toys.", user_id = user1.id, price = "33", shop_id = shop1.id)
session.add(toy2)
session.commit()

toy3 = ToyItem(name="Superman",description = "1st super hero.", user_id = user2.id, price = "22", shop_id = shop2.id)
session.add(toy3)
session.commit()

toy4 = ToyItem(name="Spiderman",description = "2rd super hero.", user_id = user2.id, price = "33", shop_id = shop2.id)
session.add(toy4)
session.commit()
