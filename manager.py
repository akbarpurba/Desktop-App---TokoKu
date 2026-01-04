import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import sys
import os

username_login = sys.argv[1] if len(sys.argv) > 1 else "MANAGER"

conn = sqlite3.connect("penjualan.db")
cursor = conn.cursor()

class Manager(tk.Tk):
    def __init__(self):
        super().__init__()

        # ===== WINDOW CENTER =====
        width = 700
        height = 450
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)

        self.title("Manager Panel")
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.configure(bg="#f4f6f8")
        self.resizable(False, False)

        self.after(100, self.lift)
        self.after(150, self.focus_force)

        # ===== HEADER =====
        tk.Label(
            self,
            text=f"Manager: {username_login}",
            font=("Segoe UI", 12, "bold"),
            bg="#f4f6f8"
        ).pack(pady=10)

        # ===== FORM =====
        form = tk.Frame(self, bg="#f4f6f8")
        form.pack(pady=5)

        tk.Label(form, text="Username", bg="#f4f6f8").grid(row=0, column=0, sticky="w")
        self.username = tk.Entry(form, width=25)
        self.username.grid(row=0, column=1, padx=10, pady=3)

        tk.Label(form, text="Password", bg="#f4f6f8").grid(row=1, column=0, sticky="w")
        self.password = tk.Entry(form, width=25)
        self.password.grid(row=1, column=1, padx=10, pady=3)

        tk.Label(form, text="Role", bg="#f4f6f8").grid(row=2, column=0, sticky="w")

        # ===== BEAUTIFUL DROPDOWN =====
        self.role_var = tk.StringVar(value="kasir")
        self.role = ttk.Combobox(
            form,
            textvariable=self.role_var,
            values=["manager", "admin", "kasir"],
            state="readonly",
            width=23
        )
        self.role.grid(row=2, column=1, padx=10, pady=3)

        # ===== BUTTONS =====
        btn = tk.Frame(self, bg="#f4f6f8")
        btn.pack(pady=10)

        tk.Button(btn, text="Tambah", width=10, command=self.add).grid(row=0, column=0, padx=5)
        tk.Button(btn, text="Ubah", width=10, command=self.update).grid(row=0, column=1, padx=5)
        tk.Button(btn, text="Hapus", width=10, command=self.delete).grid(row=0, column=2, padx=5)

        # ===== TABLE =====
        self.tree = ttk.Treeview(
            self,
            columns=("u", "p", "r"),
            show="headings",
            height=8
        )
        self.tree.heading("u", text="Username")
        self.tree.heading("p", text="Password")
        self.tree.heading("r", text="Role")

        self.tree.column("u", width=200)
        self.tree.column("p", width=200)
        self.tree.column("r", width=120, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=20)
        self.tree.bind("<<TreeviewSelect>>", self.select)

        # ===== BACK BUTTON =====
        tk.Button(
            self,
            text="Kembali ke Login",
            command=self.back
        ).pack(pady=10)

        self.load()

    # ===== FUNCTIONS =====
    def load(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in cursor.execute("SELECT username, password, role FROM users"):
            self.tree.insert("", tk.END, values=row)

    def select(self, event):
        item = self.tree.selection()
        if not item:
            return
        data = self.tree.item(item)["values"]
        self.username.delete(0, tk.END)
        self.password.delete(0, tk.END)
        self.username.insert(0, data[0])
        self.password.insert(0, data[1])
        self.role_var.set(data[2])

    def add(self):
        try:
            cursor.execute(
                "INSERT INTO users(username,password,role) VALUES(?,?,?)",
                (
                    self.username.get(),
                    self.password.get(),
                    self.role_var.get()
                )
            )
            conn.commit()
            self.load()
        except:
            messagebox.showerror("Error", "Username sudah ada")

    def update(self):
        cursor.execute(
            "UPDATE users SET password=?, role=? WHERE username=?",
            (
                self.password.get(),
                self.role_var.get(),
                self.username.get()
            )
        )
        conn.commit()
        self.load()

    def delete(self):
        cursor.execute(
            "DELETE FROM users WHERE username=?",
            (self.username.get(),)
        )
        conn.commit()
        self.load()

    def back(self):
        self.destroy()
        os.execv(sys.executable, [sys.executable, "login.py"])


Manager().mainloop()
