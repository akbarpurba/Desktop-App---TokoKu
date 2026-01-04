import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import sys
import os

class Admin(tk.Tk):
    def __init__(self):
        super().__init__()

        width = 700
        height = 500
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)

        self.title("Admin Panel")
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(False, False)
        self.configure(bg="#f4f6f8")

        self.after(100, self.lift)
        self.after(150, self.focus_force)

        self.conn = sqlite3.connect("penjualan.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            stock INTEGER NOT NULL
        )
        """)
        self.conn.commit()

        card = tk.Frame(self, bg="white")
        card.place(relx=0.5, rely=0.5, anchor="center", width=640, height=400)

        tk.Label(
            card,
            text="Product Management",
            font=("Segoe UI", 16, "bold"),
            bg="white"
        ).pack(pady=15)

        form = tk.Frame(card, bg="white")
        form.pack(pady=5)

        self.name = tk.Entry(form, font=("Segoe UI", 11), bg="#f1f3f5", relief="flat")
        self.price = tk.Entry(form, font=("Segoe UI", 11), bg="#f1f3f5", relief="flat")
        self.stock = tk.Entry(form, font=("Segoe UI", 11), bg="#f1f3f5", relief="flat")

        tk.Label(form, text="Nama Produk", bg="white").grid(row=0, column=0, padx=5, sticky="w")
        tk.Label(form, text="Harga", bg="white").grid(row=0, column=1, padx=5, sticky="w")
        tk.Label(form, text="Stok", bg="white").grid(row=0, column=2, padx=5, sticky="w")

        self.name.grid(row=1, column=0, padx=5, ipady=6)
        self.price.grid(row=1, column=1, padx=5, ipady=6)
        self.stock.grid(row=1, column=2, padx=5, ipady=6)

        btn_frame = tk.Frame(card, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Tambah", bg="#4f46e5", fg="white", relief="flat", width=10, command=self.tambah).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Ubah", bg="#0ea5e9", fg="white", relief="flat", width=10, command=self.ubah).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Hapus", bg="#ef4444", fg="white", relief="flat", width=10, command=self.hapus).grid(row=0, column=2, padx=5)

        table_frame = tk.Frame(card, bg="white")
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.table = ttk.Treeview(
            table_frame,
            columns=("id", "name", "price", "stock"),
            show="headings",
            height=7
        )

        self.table.heading("id", text="ID")
        self.table.heading("name", text="Nama")
        self.table.heading("price", text="Harga")
        self.table.heading("stock", text="Stok")

        self.table.column("id", width=50, anchor="center")
        self.table.column("name", width=220)
        self.table.column("price", width=120, anchor="center")
        self.table.column("stock", width=80, anchor="center")

        self.table.pack(fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.pilih)

        bottom = tk.Frame(card, bg="white")
        bottom.pack(pady=8)

        tk.Button(
            bottom,
            text="Keluar",
            bg="#e5e7eb",
            fg="#333",
            relief="flat",
            width=15,
            command=self.keluar
        ).pack()

        self.selected_id = None
        self.load_data()

    def load_data(self):
        self.table.delete(*self.table.get_children())
        self.cursor.execute("SELECT * FROM products")
        for row in self.cursor.fetchall():
            self.table.insert("", tk.END, values=row)

    def pilih(self, event=None):
        selected = self.table.selection()
        if not selected:
            return
        item = self.table.item(selected[0])
        self.selected_id = item["values"][0]

        self.name.delete(0, tk.END)
        self.price.delete(0, tk.END)
        self.stock.delete(0, tk.END)

        self.name.insert(0, item["values"][1])
        self.price.insert(0, item["values"][2])
        self.stock.insert(0, item["values"][3])

    def tambah(self):
        try:
            name = self.name.get().strip()
            price = int(self.price.get())
            stock = int(self.stock.get())
        except:
            messagebox.showerror("Error", "Harga dan stok harus angka")
            return

        if not name:
            messagebox.showerror("Error", "Nama produk kosong")
            return

        self.cursor.execute(
            "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
            (name, price, stock)
        )
        self.conn.commit()
        self.load_data()
        self.clear()

    def ubah(self):
        if not self.selected_id:
            messagebox.showwarning("Peringatan", "Pilih data terlebih dahulu")
            return

        try:
            price = int(self.price.get())
            stock = int(self.stock.get())
        except:
            messagebox.showerror("Error", "Harga dan stok harus angka")
            return

        self.cursor.execute(
            "UPDATE products SET name=?, price=?, stock=? WHERE id=?",
            (self.name.get(), price, stock, self.selected_id)
        )
        self.conn.commit()
        self.load_data()
        self.clear()

    def hapus(self):
        if not self.selected_id:
            messagebox.showwarning("Peringatan", "Pilih data terlebih dahulu")
            return

        if not messagebox.askyesno("Konfirmasi", "Hapus produk ini?"):
            return

        self.cursor.execute("DELETE FROM products WHERE id=?", (self.selected_id,))
        self.conn.commit()
        self.load_data()
        self.clear()

    def clear(self):
        self.name.delete(0, tk.END)
        self.price.delete(0, tk.END)
        self.stock.delete(0, tk.END)
        self.selected_id = None

    def keluar(self):
        self.conn.close()
        self.destroy()
        os.execv(sys.executable, [sys.executable, "login.py"])

if __name__ == "__main__":
    Admin().mainloop()
