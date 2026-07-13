import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from db import connect


class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("1000x700")
        self.root.configure(bg="#ffffff")
        self.filter_var = tk.StringVar(value="Books")
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        input_frame = tk.LabelFrame(self.root, text="Control Panel", padx=10, pady=10, bg="#ffffff")
        input_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(input_frame, text="Title/Name:", bg="#ffffff").grid(row=0, column=0)
        self.ent_title = tk.Entry(input_frame, width=25)
        self.ent_title.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Author/Email:", bg="#ffffff").grid(row=0, column=2)
        self.ent_author = tk.Entry(input_frame, width=25)
        self.ent_author.grid(row=0, column=3, padx=5)

        tk.Label(input_frame, text="Year/Issuing days:", bg="#ffffff").grid(row=0, column=4)
        self.ent_year = tk.Entry(input_frame, width=10)
        self.ent_year.grid(row=0, column=5, padx=5)

        tk.Label(input_frame, text="User ID:", bg="#ffffff").grid(row=1, column=0)
        self.ent_user_id = tk.Entry(input_frame, width=10)
        self.ent_user_id.grid(row=1, column=1)

        tk.Button(input_frame, text="ADD BOOK", command=self.add_book).grid(row=1, column=2, padx=5)
        tk.Button(input_frame, text="ADD USER", command=self.add_user).grid(row=1, column=3, padx=5)

        tk.Radiobutton(input_frame, text="Books", variable=self.filter_var, value="Books", bg="#ffffff",
                       command=self.refresh_table).grid(row=1, column=4)
        tk.Radiobutton(input_frame, text="Users", variable=self.filter_var, value="Users", bg="#ffffff",
                       command=self.refresh_table).grid(row=1, column=5)

        search_frame = tk.Frame(self.root, bg="#ffffff")
        search_frame.pack(fill="x", padx=20)
        tk.Label(search_frame, text="Search:", bg="#ffffff").pack(side="left")
        self.ent_search = tk.Entry(search_frame, width=40)
        self.ent_search.pack(side="left", padx=5)
        tk.Button(search_frame, text="Find", command=self.search_data).pack(side="left")
        tk.Button(search_frame, text="Reset", command=self.reset_search).pack(side="left")

        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.tree = ttk.Treeview(table_frame, columns=("id", "type", "c1", "c2", "c3"), show="headings")
        self.tree.pack(fill="both", expand=True)

        self.tree.tag_configure('overdue', background='#ffcccc', foreground='#000000')

        b_frame = tk.Frame(self.root, bg="#ffffff")
        b_frame.pack(fill="x", padx=20, pady=10)
        tk.Button(b_frame, text="DELETE", command=self.delete_selected).pack(side="left")
        tk.Button(b_frame, text="ISSUE BOOK", command=self.issue_book).pack(side="left")
        tk.Button(b_frame, text="RETURN BOOK", command=self.return_book).pack(side="left")
        tk.Button(b_frame, text="DEBTORS", command=self.show_debtors).pack(side="right")

    def update_headers(self):
        mode = self.filter_var.get()
        if mode == "Books":
            headers = ("ID", "TYPE", "TITLE", "AUTHOR", "YEAR/STATUS")
        elif mode == "Users":
            headers = ("ID", "TYPE", "NAME", "EMAIL", "-")
        elif mode == "Debtors":
            headers = ("LOAN ID", "TYPE", "USER NAME", "BOOK TITLE", "RETURN DATE")
        for i, col in enumerate(("id", "type", "c1", "c2", "c3")):
            self.tree.heading(col, text=headers[i])

    def refresh_table(self):
        mode = self.filter_var.get()
        if mode == "Debtors":
            self.show_debtors()
            return

        self.update_headers()
        for i in self.tree.get_children():
            self.tree.delete(i)

        with connect() as conn:
            cursor = conn.cursor()
            if mode == "Books":
                cursor.execute("""
                               SELECT b.id,
                                      'Book',
                                      b.title,
                                      b.author,
                                      CASE WHEN l.id IS NULL THEN b.year ELSE 'Issued' END
                               FROM books b
                                        LEFT JOIN loans l ON b.id = l.book_id AND l.returned = 0
                               """)
            else:
                cursor.execute("SELECT id, 'User', name, email, '-' FROM users")
            for r in cursor.fetchall():
                self.tree.insert("", "end", values=r)

    def search_data(self):
        q = f"%{self.ent_search.get()}%"
        mode = self.filter_var.get()
        if mode == "Debtors": return
        for i in self.tree.get_children():
            self.tree.delete(i)
        with connect() as conn:
            cursor = conn.cursor()
            if mode == "Books":
                cursor.execute("SELECT id, 'Book', title, author, year FROM books WHERE title LIKE ? OR author LIKE ?",
                               (q, q))
            else:
                cursor.execute("SELECT id, 'User', name, email, '-' FROM users WHERE name LIKE ? OR email LIKE ?",
                               (q, q))
            for r in cursor.fetchall():
                self.tree.insert("", "end", values=r)

    def reset_search(self):
        self.ent_search.delete(0, 'end')
        self.refresh_table()

    def add_book(self):
        t, a, y = self.ent_title.get().strip(), self.ent_author.get().strip(), self.ent_year.get().strip()
        if not t or not a or not y:
            messagebox.showwarning("Warning", "One of the fields is empty")
            return
        with connect() as conn:
            conn.execute("INSERT INTO books (title, author, year) VALUES (?, ?, ?)", (t, a, y))
        self.refresh_table()
        self.clear_entries()

    def add_user(self):
        n, e = self.ent_title.get().strip(), self.ent_author.get().strip()
        if not n or not e:
            messagebox.showwarning("Warning", "One of the fields is empty")
            return
        if "@" not in e:
            messagebox.showwarning("Warning", "Invalid email address")
            return
        with connect() as conn:
            conn.execute("INSERT INTO users (name, email) VALUES (?, ?)", (n, e))
        self.refresh_table()
        self.clear_entries()

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel: return
        val = self.tree.item(sel[0])['values']
        mode = self.filter_var.get()
        with connect() as conn:
            if mode == "Debtors":
                conn.execute("DELETE FROM loans WHERE id=?", (val[0],))
            else:
                table = "books" if val[1] == "Book" else "users"
                conn.execute(f"DELETE FROM {table} WHERE id=?", (val[0],))
        self.refresh_table()

    def issue_book(self):
        sel = self.tree.selection()
        if not sel: return
        val = self.tree.item(sel[0])['values']
        if val[1] != "Book": return
        book_id, user_id = val[0], self.ent_user_id.get()
        if not user_id: return
        days = self.ent_year.get()
        if not days.isdigit(): days = "7"
        with connect() as conn:
            check = conn.execute("SELECT * FROM loans WHERE book_id=? AND returned=0", (book_id,)).fetchone()
            if check:
                messagebox.showwarning("Error", "Book already issued")
                return
            conn.execute(
                f"INSERT INTO loans (book_id, user_id, issue_date, return_date) VALUES (?, ?, date('now'), date('now','+{days} day'))",
                (book_id, user_id))
        self.refresh_table()
        messagebox.showinfo("Success", "Book issued")

    def return_book(self):
        sel = self.tree.selection()
        if not sel: return
        val = self.tree.item(sel[0])['values']
        mode = self.filter_var.get()
        with connect() as conn:
            if mode == "Debtors":
                conn.execute("UPDATE loans SET returned=1 WHERE id=?", (val[0],))
            elif mode == "Books":
                conn.execute("UPDATE loans SET returned=1 WHERE book_id=? AND returned=0", (val[0],))
        self.refresh_table()
        messagebox.showinfo("Returned", "Book returned")

    def show_debtors(self):
        self.filter_var.set("Debtors")
        self.update_headers()
        for i in self.tree.get_children():
            self.tree.delete(i)
        with connect() as conn:
            data = conn.execute("""
                                SELECT loans.id, 'LOAN', users.name, books.title, loans.return_date
                                FROM loans
                                         JOIN users ON loans.user_id = users.id
                                         JOIN books ON loans.book_id = books.id
                                WHERE returned = 0
                                """).fetchall()

        today = datetime.now().strftime("%Y-%m-%d")
        for r in data:
            if r[4] < today:
                self.tree.insert("", "end", values=r, tags=('overdue',))
            else:
                self.tree.insert("", "end", values=r)

    def clear_entries(self):
        for e in [self.ent_title, self.ent_author, self.ent_year, self.ent_user_id]: e.delete(0, 'end')


if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()