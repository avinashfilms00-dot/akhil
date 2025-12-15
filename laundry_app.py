import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import webbrowser
from datetime import datetime
import urllib.parse

# --- 1. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('smart_wash_laundry.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  customer_name TEXT,
                  phone TEXT,
                  items TEXT,
                  total_amount INTEGER,
                  status TEXT,
                  date TEXT)''')
    conn.commit()
    conn.close()

# --- 2. YOUR RATE LIST  ---
RATE_CARD = {
    "T-shirt": 75, "Shirt": 75, "Silk Shirt": 100, "Woolen Shirt": 100,
    "Pants": 75, "Suit (2 Pcs)": 350, "Suit (3 Pcs)": 350, 
    "Kurta": 150, "Kurta Silk": 150, "Sherwani": 450,
    "Dhoti": 250, "Dhoti Silk": 300, "Safari Set": 300, "Achkan": 400,
    "Long Pullover": 200, "Blazer/Coat (Cotton)": 250, "Blazer/Coat (Woolen)": 350,
    "Long Coat": 350, "Jacket Full": 350, "Jacket Half": 250, "Jacket Leather": 500,
    "Kurti Plain": 75, "Kurti Heavy": 150, "Salwar Plain": 90, "Salwar Heavy": 150,
    "Plazo Plain": 120, "Plazo Work": 180, "Dupatta": 60, "Dupatta Work": 135,
    "Saree": 250, "Saree Roll-Press": 150, "Formal Saree": 200,
    "Petticoat": 60, "Blouse": 50, "Blouse Work": 90, "Dress Plain": 180,
    "Dress Heavy": 350, "Lehenga": 500, "Lehenga Heavy": 700, "Poshak Set": 500,
    "Blanket (Single)": 350, "Blanket (Double)": 450, "Sofa Sheet": 350,
    "Leather Shoes": 450, "Sports Shoes": 250
}

# --- 3. MAIN APPLICATION ---
class LaundryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Wash Drycleaners - Billing System")
        self.root.geometry("900x700")

        # Variables
        self.cart = {}
        self.cust_name = tk.StringVar()
        self.cust_phone = tk.StringVar()
        self.total_var = tk.StringVar(value="Total: ₹0")

        # --- Tabs ---
        tabControl = ttk.Notebook(root)
        self.tab1 = ttk.Frame(tabControl)
        self.tab2 = ttk.Frame(tabControl)
        tabControl.add(self.tab1, text='New Bill ')
        tabControl.add(self.tab2, text='Manage Orders ')
        tabControl.pack(expand=1, fill="both")

        self.create_billing_tab()
        self.create_manage_tab()

    def create_billing_tab(self):
        # Customer Details
        frame_cust = tk.LabelFrame(self.tab1, text="Customer Details", padx=10, pady=10)
        frame_cust.pack(fill="x", padx=10, pady=5)
        
        tk.Label(frame_cust, text="Name:").grid(row=0, column=0)
        tk.Entry(frame_cust, textvariable=self.cust_name).grid(row=0, column=1, padx=10)
        
        tk.Label(frame_cust, text="Phone (10 digits):").grid(row=0, column=2)
        tk.Entry(frame_cust, textvariable=self.cust_phone).grid(row=0, column=3, padx=10)

        # Item Selection
        frame_items = tk.LabelFrame(self.tab1, text="Select Items", padx=10, pady=10)
        frame_items.pack(fill="both", expand=True, padx=10, pady=5)

        # Scrollable Canvas for Items
        canvas = tk.Canvas(frame_items)
        scrollbar = ttk.Scrollbar(frame_items, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        row = 0
        col = 0
        self.qty_vars = {} 
        
        for item, price in RATE_CARD.items():
            if col > 3: # 4 columns layout
                col = 0
                row += 1
            
            f = tk.Frame(scrollable_frame, borderwidth=1, relief="solid", padx=5, pady=5)
            f.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            tk.Label(f, text=f"{item}\n₹{price}", font=("Arial", 9, "bold")).pack()
            
            qty_var = tk.IntVar(value=0)
            self.qty_vars[item] = qty_var
            
            spin = tk.Spinbox(f, from_=0, to=50, width=5, textvariable=qty_var, command=self.update_total)
            spin.pack()
            
            col += 1

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Actions
        frame_action = tk.Frame(self.tab1, padx=10, pady=10)
        frame_action.pack(fill="x")
        
        tk.Label(frame_action, textvariable=self.total_var, font=("Arial", 16, "bold"), fg="blue").pack(side="left")
        
        tk.Button(frame_action, text="SAVE & WHATSAPP BILL", bg="green", fg="white", font=("Arial", 10, "bold"), command=self.save_and_send).pack(side="right", padx=5)
        tk.Button(frame_action, text="Reset", command=self.reset_form).pack(side="right")

    def create_manage_tab(self):
        # Search & List
        frame_top = tk.Frame(self.tab2, pady=10)
        frame_top.pack()
        
        tk.Button(frame_top, text="Refresh List", command=self.load_orders).pack()

        # Treeview (Table) - include Items column
        cols = ('ID', 'Name', 'Phone', 'Items', 'Amount', 'Status', 'Date')
        self.tree = ttk.Treeview(self.tab2, columns=cols, show='headings')
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill="both", expand=True, padx=10)
        
        # Action Buttons
        frame_bottom = tk.Frame(self.tab2, pady=10)
        frame_bottom.pack()
        
        tk.Button(frame_bottom, text="Mark as READY & Send WhatsApp", bg="orange", command=self.mark_ready).pack(side="left", padx=10)
        tk.Button(frame_bottom, text="Delete Order", bg="red", fg="white", command=self.delete_order).pack(side="left", padx=10)

    def update_total(self):
        total = 0
        self.cart = {}
        for item, qty_var in self.qty_vars.items():
            try:
                qty = int(qty_var.get())
            except Exception:
                qty = 0
            if qty > 0:
                cost = qty * RATE_CARD[item]
                total += cost
                self.cart[item] = {'qty': qty, 'cost': cost}
        self.total_var.set(f"Total: ₹{total}")
        return total

    def save_and_send(self):
        name = self.cust_name.get().strip()
        phone = self.cust_phone.get().strip()
        total = self.update_total()
        
        if not name or not phone or total == 0:
            messagebox.showerror("Error", "Please fill Name, Phone and select items!")
            return

        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        items_str = ", ".join([f"{k} x{v['qty']}" for k,v in self.cart.items()])
        
        # Save to DB
        conn = sqlite3.connect('smart_wash_laundry.db')
        c = conn.cursor()
        c.execute("INSERT INTO orders (customer_name, phone, items, total_amount, status, date) VALUES (?, ?, ?, ?, ?, ?)",
                  (name, phone, items_str, total, "Pending", date_str))
        conn.commit()
        order_id = c.lastrowid
        conn.close()

        # Generate WhatsApp Message (use plain newlines, then URL-encode)
        bill_lines = [f"{k}: {v['qty']}pcs = ₹{v['cost']}" for k,v in self.cart.items()]
        msg_lines = ["SMART WASH DRYCLEANERS",
                     f"Hello {name}, Thank you for your order!",
                     f"Order ID: #{order_id}",
                     f"Date: {date_str}",
                     "----------------"]
        msg_lines.extend(bill_lines)
        msg_lines.append("----------------")
        msg_lines.append(f"Total Amount: ₹{total}")
        msg_lines.append("Status: Received (Processing)")

        msg = "\n".join(msg_lines)
        self.send_whatsapp(phone, msg)
        self.reset_form()
        self.load_orders()

    def mark_ready(self):
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        order_id = item['values'][0]
        name = item['values'][1]
        phone = str(item['values'][2])
        
        conn = sqlite3.connect('smart_wash_laundry.db')
        c = conn.cursor()
        c.execute("UPDATE orders SET status='Ready' WHERE id=?", (order_id,))
        conn.commit()
        conn.close()
        
        msg_lines = [f"Hello {name}, Good News!",
                     f"Your laundry order #{order_id} is READY for pickup.",
                     "Please collect it from Smart Wash Drycleaners."]
        msg = "\n".join(msg_lines)
        self.send_whatsapp(phone, msg)
        self.load_orders()

    def delete_order(self):
        selected = self.tree.selection()
        if selected:
            order_id = self.tree.item(selected[0])['values'][0]
            conn = sqlite3.connect('smart_wash_laundry.db')
            c = conn.cursor()
            c.execute("DELETE FROM orders WHERE id=?", (order_id,))
            conn.commit()
            conn.close()
            self.load_orders()

    def send_whatsapp(self, phone, message):
        # Keep only digits
        phone_digits = ''.join(ch for ch in phone if ch.isdigit())
        if len(phone_digits) == 10:
            phone_number = '91' + phone_digits
        elif phone_digits.startswith('91'):
            phone_number = phone_digits
        else:
            phone_number = phone_digits
        encoded = urllib.parse.quote_plus(message)
        url = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded}"
        webbrowser.open(url)

    def reset_form(self):
        self.cust_name.set("")
        self.cust_phone.set("")
        self.total_var.set("Total: ₹0")
        for q in self.qty_vars.values():
            q.set(0)

    def load_orders(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = sqlite3.connect('smart_wash_laundry.db')
        c = conn.cursor()
        c.execute("SELECT id, customer_name, phone, items, total_amount, status, date FROM orders ORDER BY id DESC")
        rows = c.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)
        conn.close()

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = LaundryApp(root)
    root.mainloop()
