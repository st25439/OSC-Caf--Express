from flask import Flask, redirect, render_template
import json

app = Flask(__name__)

cart = []

# Load products
def load_products():
    with open("data/product.json", "r") as file:
        return json.load(file)

 # Home page
@app.route("/")
def home():
    products = load_products()
    return render_template(
        "index.html",
        products=products,
        cart= cart
    )

# Add product to cart
@app.route("/add/<product_name>")
def add_to_cart(product_name):
    products = load_products()

    for product in products:
        if product["name"] == product_name:

            # Check if product is already in the cart
            found = False

            for item in cart:
                if item["name"] == product_name:
                    item["quantity"] += 1
                    found = True
                    break

            # Add product for the first time
            if not found:
                cart_item = product.copy()
                cart_item["quantity"] = 1
            cart.append(cart_item)

    return redirect("/")
 

if __name__ == "__main__":
    app.run(debug=True)