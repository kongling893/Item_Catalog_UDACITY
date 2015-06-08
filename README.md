##Toy Shop Online Mangement
This is the third project for "Full Stack Web Developer Nanodegree" on Udacity.

You can use this website to manage toy shops.

##Before running this website, make sure all the required python modules have been installed.
Please see Instructions.

##Instructions
1. Clone this project to your local machine at first.
2. use `pip install -r requirements.txt` to install neccessary python modules.
3. Use `python database_setup.py` to create database.
4. Use `python import_fake_data.py` to import fake data if you want to test this website.
5. Use `python website.py` to run this website on your local machine.
6. Open browser and navigate to http://localhost:5000/

##Features
1. Using Flask ( a light Python web framework).
2. Using OAuth 2.0 to Access Google APIs.
	- You can login using your google account.
	- Only the owner can manage his own shop.
3. Using RESRfull APIs, like Post and Get.
4. Providing JSON APIs, which you can exploit to get the information you want.

## We also provide json APIs

	@app.route('/index/<string:shop_ID>/JSON/')
	def shopJSON(shop_ID):
		shops = session.query(ToyShop).filter_by(id=shop_ID).one()
		toys = session.query(ToyItem).filter_by(shop_id = shop_ID).all()
		return jsonify(Shop=shops.serialize, Toys = [g.serialize for g in toys])


	@app.route('/index/<string:shop_ID>/<string:toy_ID>/JSON/')
	def toyJSON(shop_ID,toy_ID):
		toy = session.query(ToyItem).filter_by(id=toy_ID).one()
		return jsonify(Toy = toy.serialize)

You can use url likes `localhost:5000/index/<string:shop_ID>/JSON/` to get the JSON file corresponding to the shop with id = shop_ip; 
You can use url likes `localhost:5000/index/<string:shop_ID>/<string:toy_ID>/JSON/` to get the JSON file corresponding to the toy with id = toy_ID. 

##You will see
The main page looks like:
![1](https://lh5.googleusercontent.com/-qkx6LQ6O9wU/VXRf6QC_P1I/AAAAAAAAAG0/tUHsYB8_b4k/w1212-h682/1.png)

You can use your google account to login:
![2](https://lh4.googleusercontent.com/-d3k5mYac8II/VXRf5Rq-5JI/AAAAAAAAAGw/9IwK94wdilU/w1212-h682-no/2.png)

You can create your own shop:
![4](https://lh6.googleusercontent.com/-_vakljjtW2k/VXRf6aDsoeI/AAAAAAAAAHA/YhKeW63N0Lk/w1212-h682-no/3.png)

You can view the shop:
![6](https://lh4.googleusercontent.com/-CtQJuzp_JFM/VXRgB3Um12I/AAAAAAAAAHM/ZF8KbHyBzMw/w1212-h682-no/4.png)

You can add new toy to your shop:
![7](https://lh6.googleusercontent.com/-iTptXE7dyhk/VXRgHfLVLuI/AAAAAAAAAHY/Vbw9Fa3yCL8/w1212-h682-no/5.png)

You can use JSON APIs like:
![9](https://lh6.googleusercontent.com/-iSpM6UUs1NE/VXRgCL2RRZI/AAAAAAAAAHQ/m1jXVYBpSnY/w1212-h682-no/6.png)
