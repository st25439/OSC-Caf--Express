from flask import Flask, redirect, render_template, request
import json

app = Flask(__name__)

cart = []
customer_name = ""

def get_next_order_number():
    """Return the next available order number."""

    try:
        with open("data/orders.json", "r") as file:
            orders = json.load(file)

        if not orders:
            return 1000

        highest_number = max(
            order["order_number"] for order in orders
        )

        return highest_number + 1

    except FileNotFoundError:
        return 1000

@app.route("/set_customer", methods=["POST"])
def set_customer():
    global customer_name

    customer_name = request.form["customer_name"].strip()

    return redirect("/")

# Load products
def load_products():
    with open("data/product.json", "r") as file:
        return json.load(file)

   # Calculate cart total
def calculate_total():
    total = 0

    for item in cart:
        total += item["price"] * item["quantity"]

    return total

def save_order(order):
    """Save a completed order to the orders JSON file."""

    try:
        with open("data/orders.json", "r") as file:
            orders = json.load(file)
    except FileNotFoundError:
        orders = []

    orders.append(order)

    with open("data/orders.json", "w") as file:
        json.dump(orders, file, indent=4)

 # Home page
@app.route("/")
def home():
    products = load_products()

    total = calculate_total() 

    return render_template(
        "index.html",
        products=products,
        cart= cart,
     customer_name=customer_name,
     total=total
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
                cart.append({
                    "name": product["name"],
                    "price": product["price"],
                    "quantity": 1
                })

            break
    return redirect("/")

@app.route("/remove/<product_name>")
def remove_from_cart(product_name):

    for item in cart:

        if item["name"] == product_name:

            cart.remove(item)
            break

    return redirect("/")

@app.route("/checkout", methods=["GET", "POST"])
def checkout():

    total = calculate_total()

    if not cart:
        return redirect("/")

    if request.method == "POST":

        order_type = request.form.get(
            "order_type", "pickup"
        )

        if order_type == "delivery":

            address = request.form.get(
                "address", ""
            ).strip()

            phone = request.form.get(
                "phone", ""
            ).strip()

            if not address:
                return render_template(
                    "checkout.html",
                    cart=cart,
                    customer_name=customer_name,
                    total=total,
                    error="Please enter your delivery address."
                )

            if not phone:
                return render_template(
                    "checkout.html",
                    cart=cart,
                    customer_name=customer_name,
                    total=total,
                    error="Please enter your phone number."
                )

            if not valid_phone(phone):
                return render_template(
                    "checkout.html",
                    cart=cart,
                    customer_name=customer_name,
                    total=total,
                    error="Please enter a valid phone number."
                )

            delivery_charge = 3.00
            final_total = total + delivery_charge

            return render_template(
                "confirm_order.html",
                customer_name=customer_name,
                cart=cart,
                total=total,
                delivery_charge=delivery_charge,
                final_total=final_total,
                order_type=order_type,
                address=address,
                phone=phone
            )

        return render_template(
            "confirm_order.html",
            customer_name=customer_name,
            cart=cart,
            total=total,
            delivery_charge=0.00,
            final_total=total,
            order_type="pickup",
            address="",
            phone=""
        )

    return render_template(
        "checkout.html",
        cart=cart,
        customer_name=customer_name,
        total=total
    )

def valid_phone(phone):
    """Check that the phone number contains valid characters."""
    phone = phone.replace(" ", "")

    if phone.startswith("+64"):
        phone = phone[3:]

    if not phone.isdigit():
        return False

    if len(phone) < 8 or len(phone) > 10:
        return False

    return True

@app.route("/place_order", methods=["POST"])
def place_order():
    global cart

    if not cart:
        return redirect("/")
    
    order_total = calculate_total()

    order_type = request.form.get("order_type", "delivery")
    address = request.form.get("address", "")
    phone = request.form.get("phone", "")

    if order_type == "delivery":
        delivery_charge = 3.00
    else:
        delivery_charge = 0.00

    final_total = order_total + delivery_charge

    order = {
        "order_number": get_next_order_number(),
        "customer_name": customer_name,
        "order_type": order_type,
        "address": address,
        "phone": phone,
        "items": cart.copy(),
        "total": order_total,
        "delivery_charge": delivery_charge,
        "final_total": final_total,
        "status": "Confirmed"
    }

    save_order(order)

    completed_order = order.copy()

    cart.clear()

    return render_template(
        "order_complete.html",
        order=completed_order
    )

@app.route("/cancel_order/<int:order_number>", methods=["POST"])
def cancel_order(order_number):
    """Cancel a confirmed order using its order number."""

    try:
        with open("data/orders.json", "r") as file:
            orders = json.load(file)
    except FileNotFoundError:
        return redirect("/")

    for order in orders:
        if order["order_number"] == order_number:
            order["status"] = "Cancelled"
            break

    with open("data/orders.json", "w") as file:
        json.dump(orders, file, indent=4)

    return redirect("/order_history")

@app.route("/order_history")
def order_history():
    """Display all saved customer orders."""

    try:
        with open("data/orders.json", "r") as file:
            orders = json.load(file)
    except FileNotFoundError:
        orders = []

    return render_template(
        "order_history.html",
        orders=orders
    )

if __name__ == "__main__":
    app.run(debug=True)