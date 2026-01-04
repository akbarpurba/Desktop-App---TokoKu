import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import sys
import os

class Kasir(tk.Tk):
    def __init__(self):
        super().__init__()

        self.nama_kasir = sys.argv[1] if len(sys.argv) > 1 else "KASIR"
        self.nama_toko = "MYSHOP MART"
        self.alamat_toko = "Perbaungan, Sumatera Utara, Indonesia"

        w, h = 1040, 600
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.title("Kasir")
        self.configure(bg="#f4f6f8")
        self.resizable(False, False)

        self.lift()
        self.focus_force()
        self.attributes('-topmost', True)
        self.after(200, lambda: self.attributes('-topmost', False))

        self.conn = sqlite3.connect("penjualan.db")
        self.cur = self.conn.cursor()
        self.cart = []
        self.nomor_struk = 1
        self.total_int = 0

        self.build_ui()
        self.load_produk()

    def build_ui(self):
        header = tk.Frame(self, bg="white", height=60)
        header.pack(fill="x")
        tk.Label(header, text=f"Kasir: {self.nama_kasir}", bg="white", font=("Segoe UI", 11)).pack(side="left", padx=20)
        self.lbl_time = tk.Label(header, bg="white", font=("Segoe UI", 11))
        self.lbl_time.pack(side="right", padx=20)
        self.clock()

        main = tk.Frame(self, bg="#f4f6f8")
        main.pack(fill="both", expand=True, padx=20, pady=10)

        self.table_produk = ttk.Treeview(main, columns=("id","nama","harga","stok"), show="headings", height=20)
        for c,t,w in [("id","ID",40),("nama","Nama",200),("harga","Harga",100),("stok","Stok",80)]:
            self.table_produk.heading(c,text=t)
            self.table_produk.column(c,width=w,anchor="center" if c!="nama" else "w")
        self.table_produk.pack(side="left", fill="y")

        tk.Button(main, text="→", bg="#4f46e5", fg="white", width=5, relief="flat", command=self.add_cart).pack(side="left", padx=10)

        right = tk.Frame(main, bg="white")
        right.pack(side="right", fill="both", expand=True)

        self.table_cart = ttk.Treeview(right, columns=("nama","harga","qty","sub"), show="headings", height=14)
        for c,t,w in [("nama","Produk",200),("harga","Harga",80),("qty","Qty",60),("sub","Subtotal",100)]:
            self.table_cart.heading(c,text=t)
            self.table_cart.column(c,width=w,anchor="center" if c!="nama" else "w")
        self.table_cart.pack(fill="both", expand=True, padx=10, pady=10)

        calc = tk.Frame(right, bg="white")
        calc.pack(pady=5)
        tk.Label(calc, text="Diskon %", bg="white").grid(row=0,column=0,sticky="w")
        self.diskon = tk.Entry(calc, width=8); self.diskon.grid(row=0,column=1,padx=5); self.diskon.insert(0,"0")
        tk.Label(calc, text="Pajak %", bg="white").grid(row=1,column=0,sticky="w")
        self.pajak = tk.Entry(calc, width=8); self.pajak.grid(row=1,column=1,padx=5); self.pajak.insert(0,"0")
        tk.Label(calc, text="TOTAL", font=("Segoe UI",14,"bold"), bg="white").grid(row=0,column=2,rowspan=2,padx=20)
        self.total_var = tk.StringVar(value="0")
        tk.Label(calc, textvariable=self.total_var, font=("Segoe UI",16,"bold"), fg="green", bg="white").grid(row=0,column=3,rowspan=2)

        tk.Label(calc, text="Dibayar", bg="white").grid(row=2,column=0,sticky="w", pady=5)
        self.bayar_entry = tk.Entry(calc, width=15)
        self.bayar_entry.grid(row=2,column=1, pady=5)
        tk.Label(calc, text="Kembalian", bg="white").grid(row=3,column=0,sticky="w", pady=5)
        self.kembalian_var = tk.StringVar(value="0")
        tk.Label(calc, textvariable=self.kembalian_var, bg="white").grid(row=3,column=1,sticky="w", pady=5)
        self.bayar_entry.bind("<KeyRelease>", self.hitung_kembalian)

        btn = tk.Frame(right, bg="white")
        btn.pack(pady=10)
        tk.Button(btn, text="Preview Struk", bg="#0ea5e9", fg="white", width=12, relief="flat", command=self.preview).grid(row=0,column=0,padx=5)
        tk.Button(btn, text="Bayar", bg="#16a34a", fg="white", width=12, relief="flat", command=self.konfirmasi_bayar).grid(row=0,column=1,padx=5)
        tk.Button(btn, text="Hapus", bg="#ef4444", fg="white", width=12, relief="flat", command=self.hapus).grid(row=0,column=3,padx=5)
        tk.Button(btn, text="Keluar", width=12, relief="flat", command=self.keluar).grid(row=0,column=4,padx=5)

    def clock(self):
        self.lbl_time.config(text=datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        self.after(1000, self.clock)

    def load_produk(self):
        self.table_produk.delete(*self.table_produk.get_children())
        self.cur.execute("SELECT * FROM products")
        for r in self.cur.fetchall():
            self.table_produk.insert("", tk.END, values=r)

    def add_cart(self):
        if not self.table_produk.selection():
            return
        pid,n,h,s = self.table_produk.item(self.table_produk.selection())["values"]
        for c in self.cart:
            if c["id"] == pid:
                c["qty"] += 1
                self.refresh()
                return
        self.cart.append({"id":pid,"nama":n,"harga":h,"qty":1})
        self.refresh()

    def refresh(self):
        self.table_cart.delete(*self.table_cart.get_children())
        total = 0
        for c in self.cart:
            sub = c["harga"] * c["qty"]
            total += sub
            self.table_cart.insert("",tk.END,values=(c["nama"],c["harga"],c["qty"],sub))
        total -= total * float(self.diskon.get()) / 100
        total += total * float(self.pajak.get()) / 100
        self.total_int = total
        self.total_var.set(int(total))
        self.hitung_kembalian()

    def hapus(self):
        if not self.table_cart.selection():
            return
        self.cart.pop(self.table_cart.index(self.table_cart.selection()))
        self.refresh()

    def hitung_kembalian(self, event=None):
        try:
            bayar = int(self.bayar_entry.get())
            kembalian = bayar - int(self.total_int)
            self.kembalian_var.set(kembalian if kembalian >=0 else 0)
        except:
            self.kembalian_var.set(0)

    def konfirmasi_bayar(self):
        if not self.cart:
            messagebox.showwarning("Peringatan", "Keranjang kosong!")
            return
        try:
            bayar = int(self.bayar_entry.get())
            if bayar < int(self.total_int):
                messagebox.showerror("Error", "Pembayaran kurang!")
                return
            for c in self.cart:
                self.cur.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (c["qty"], c["id"]))
            self.conn.commit()
            self.nomor_struk += 1
            self.pdf()
            messagebox.showinfo("Sukses", f"Transaksi berhasil.\nKembalian: {bayar - int(self.total_int)}")
            self.cart.clear()
            self.refresh()
            self.bayar_entry.delete(0, tk.END)
            self.kembalian_var.set("0")
            self.load_produk()
        except:
            messagebox.showerror("Error", "Input tidak valid!")

    def preview(self):
        w = tk.Toplevel(self)
        w.title("Preview Struk")
        w.geometry("400x500")
        t = tk.Text(w, font=("Courier",10))
        t.pack(fill="both", expand=True)
        t.insert("end", self.struk())
        t.config(state="disabled")

    def struk(self):
        s = f"{self.nama_toko}\n{self.alamat_toko}\n"
        s += "="*35+"\n"
        s += f"Nomor Struk: {self.nomor_struk}\n"
        s += f"Kasir : {self.nama_kasir}\n"
        s += f"Waktu : {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n"
        s += "-"*35+"\n"
        for c in self.cart:
            s += f"{c['nama']:<15} x{c['qty']} {c['harga']*c['qty']:>8}\n"
        s += "-"*35+"\n"
        s += f"TOTAL{'':17}{int(self.total_int)}\n"
        bayar = self.bayar_entry.get()
        if bayar:
            s += f"DIBAYAR{'':14}{bayar}\n"
            s += f"KEMBALIAN{'':11}{self.kembalian_var.get()}\n"
        s += "="*35+"\n"
        s += "Terima kasih banyak telah berbelanja di MYSHOP MART.\n Semoga hari Anda menyenangkan dan kembali lagi.\n"
        return s

    def pdf(self):
        # PDF hanya bisa dicetak setelah bayar
        doc = SimpleDocTemplate(f"struk_{self.nomor_struk}.pdf")
        styles = getSampleStyleSheet()
        doc.build([Paragraph(self.struk().replace("\n","<br/>"), styles["Normal"])])

    def keluar(self):
        self.destroy()
        os.execv(sys.executable, [sys.executable, "login.py"])


if __name__ == "__main__":
    Kasir().mainloop()
