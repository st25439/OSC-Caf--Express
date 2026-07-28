from flask import Flask, render_template
import json

app = Flask(__name__)

# Load products from JSON
def load_products():
    with open("data/product.json", "r") as file:
        return json.load(file)

@app.route('/')
def home():
    products = load_products()
    return render_template('index.html', products=products)

if __name__ == "__main__":
    app.run(debug=True)