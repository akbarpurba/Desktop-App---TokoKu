import tkinter as tk
from tkinter import messagebox
import sqlite3
import sys
import os

conn = sqlite3.connect("penjualan.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

data_users = [
    ("manager", "manager123", "manager"),
    ("admin", "admin123", "admin"),
    ("kasir", "kasir123", "kasir")
]

for u in data_users:
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (u[0],))
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            u
        )

conn.commit()
conn.close()


class Login(tk.Tk):
    def __init__(self):
        super().__init__()

        width = 700
        height = 450
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)

        self.title("Myshop Login")
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(False, False)
        self.configure(bg="#f4f6f8")

        card = tk.Frame(self, bg="white")
        card.place(relx=0.5, rely=0.5, anchor="center", width=450, height=360)

        tk.Label(card, text="Welcome Back", font=("Segoe UI", 16, "bold"), bg="white", fg="#333").pack(pady=(25, 5))
        tk.Label(card, text="Please login to your account", font=("Segoe UI", 10), bg="white", fg="#777").pack(pady=(0, 20))

        tk.Label(card, text="Username", font=("Segoe UI", 10), bg="white", fg="#555").pack(anchor="w", padx=40)
        self.username_entry = tk.Entry(card, font=("Segoe UI", 11), relief="flat", bg="#f1f3f5")
        self.username_entry.pack(fill="x", padx=40, pady=(0, 12), ipady=6)

        tk.Label(card, text="Password", font=("Segoe UI", 10), bg="white", fg="#555").pack(anchor="w", padx=40)
        self.password_entry = tk.Entry(card, font=("Segoe UI", 11), relief="flat", bg="#f1f3f5", show="*")
        self.password_entry.pack(fill="x", padx=40, pady=(0, 18), ipady=6)

        tk.Button(
            card,
            text="Login",
            font=("Segoe UI", 11, "bold"),
            bg="#4f46e5",
            fg="white",
            activebackground="#4338ca",
            relief="flat",
            cursor="hand2",
            command=self.proses_login
        ).pack(fill="x", padx=40, ipady=8)

        tk.Button(
            card,
            text="Exit",
            font=("Segoe UI", 10),
            bg="white",
            fg="#777",
            relief="flat",
            cursor="hand2",
            command=self.quit
        ).pack(pady=12)

    def proses_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        conn = sqlite3.connect("penjualan.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        result = cursor.fetchone()
        conn.close()

        if not result:
            messagebox.showerror("Login Failed", "Username or password incorrect")
            return

        role = result[0]

        messagebox.showinfo("Login Berhasil", f"Selamat datang {username} ({role.capitalize()})")

        role_map = {
            "manager": "manager.py",
            "admin": "admin.py",
            "kasir": "kasir.py"
        }

        self.destroy()

        if role == "kasir":
            os.execv(sys.executable, [sys.executable, role_map[role], username])
        else:
            os.execv(sys.executable, [sys.executable, role_map[role]])


if __name__ == "__main__":
    Login().mainloop()
