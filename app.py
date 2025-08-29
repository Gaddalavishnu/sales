from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# ---------- Database Setup ----------
def init_db():
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS sales (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        customerName TEXT NOT NULL,
                        phoneNumber TEXT NOT NULL,
                        productName TEXT NOT NULL,
                        quantity INTEGER,
                        amount REAL NOT NULL,
                        cashGiven REAL,
                        due REAL)''')
    conn.commit()
    conn.close()

init_db()

# ---------- Routes ----------
@app.route("/", methods=["GET", "POST"])
def home():
    error = None
    query = request.args.get("q", "").lower()
    sales = []

    if request.method == "POST":
        # Insert new record
        customerName = request.form.get("customerName").strip()
        phoneNumber = request.form.get("phoneNumber").strip()
        productName = request.form.get("productName").strip()
        quantity = request.form.get("quantity", 0)
        amount = request.form.get("amount", 0)
        cashGiven = request.form.get("cashGiven", 0)

        if not customerName or not phoneNumber or not productName or not amount:
            error = "Please fill all required fields."
        else:
            amount = float(amount)
            cashGiven = float(cashGiven) if cashGiven else 0
            due = amount - cashGiven

            conn = sqlite3.connect("sales.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO sales (customerName, phoneNumber, productName, quantity, amount, cashGiven, due) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (customerName, phoneNumber, productName, quantity, amount, cashGiven, due))
            conn.commit()
            conn.close()

            return redirect(url_for("home"))

    # Fetch records ONLY if query given
    if query:
        conn = sqlite3.connect("sales.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sales WHERE LOWER(customerName) LIKE ? OR phoneNumber LIKE ?", 
                       ('%' + query + '%', '%' + query + '%'))
        sales = cursor.fetchall()
        conn.close()

    return render_template("index.html", sales=sales, error=error, query=query)


# ---------- Update Route ----------
@app.route("/update/<int:sale_id>", methods=["POST"])
def update_sale(sale_id):
    customerName = request.form.get("customerName").strip()
    phoneNumber = request.form.get("phoneNumber").strip()
    productName = request.form.get("productName").strip()
    quantity = request.form.get("quantity", 0)
    amount = float(request.form.get("amount", 0))
    cashGiven = float(request.form.get("cashGiven", 0))
    due = amount - cashGiven

    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    cursor.execute("""UPDATE sales SET 
                        customerName=?, phoneNumber=?, productName=?, 
                        quantity=?, amount=?, cashGiven=?, due=? 
                      WHERE id=?""",
                   (customerName, phoneNumber, productName, quantity, amount, cashGiven, due, sale_id))
    conn.commit()
    conn.close()

    return redirect(url_for("home", q=customerName))  # return to search view


if __name__ == "__main__":
    app.run(debug=True)
