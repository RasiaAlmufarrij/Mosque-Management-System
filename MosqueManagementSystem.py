from tkinter import *
from tkinter import messagebox
import sqlite3
import folium
import webbrowser
import os
import difflib
class Mosque:
    
    def __init__(self, mosque_id, name, mosque_type, address, coord_var, imam_name):
        self.mosque_id = mosque_id
        self.name = name
        self.mosque_type = mosque_type
        self.address = address
        self.coordinates = coord_var
        self.imam_name = imam_name
    
    def __str__(self):
        return f"{self.mosque_id} | {self.name} | {self.mosque_type} | {self.address} | {self.coordinates} | {self.imam_name}"
    
class Database:
    
    def __init__(self, db_name="mosques.db"):
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS Mosques (
            ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Type TEXT,
            Address TEXT,
            Coordinates TEXT,
            Imam_Name TEXT
        )''')
        self.conn.commit()
    
    def Display(self):
        self.cur.execute("SELECT * FROM Mosques")
        return self.cur.fetchall()
    
    def Search(self, name):
        self.cur.execute("SELECT * FROM Mosques WHERE LOWER(Name)=LOWER(?)", (name,))
        return self.cur.fetchone()
    
    def Insert(self, ID, name, mosque_type, address, coordinates, imam_name):
        self.cur.execute("INSERT INTO Mosques VALUES (?, ?, ?, ?, ?, ?)", (ID, name, mosque_type, address, coordinates, imam_name))
        self.conn.commit()
    def UpdateImam(self, ID, new_imam_name):
         self.cur.execute("UPDATE Mosques SET Imam_Name=? WHERE ID=?", (new_imam_name, ID))
         self.conn.commit()

    def Delete(self, ID):
        self.cur.execute("DELETE FROM Mosques WHERE ID=?", (ID,))
        self.conn.commit()
    
    def __del__(self):
        self.conn.close()

def display_all_mosques():
    listbox1.delete(0, END)
    all_records = db.Display()
    for record in all_records:
        listbox1.insert(END, f"{record[0]} | {record[1]} | {record[2]} | {record[3]} | {record[4]} | {record[5]}")
    clearEverything()

def search():
    global cm_id,imamPre
    if name_var.get() == "":
        messagebox.showwarning("Warning", "Please enter a mosque name!")
        return
    listbox1.delete(0, END)
    record = db.Search(name_var.get())
    if record:
        id_var.set(record[0])
        name_var.set(record[1])
        type_var.set(record[2])
        address_var.set(record[3])
        coord_var.set(record[4])
        imam_var.set(record[5])
        imamPre=record[5]
        listbox1.insert(END, f"{record[0]} | {record[1]} | {record[2]} | {record[3]} | {record[4]} | {record[5]}")
        cm_id=record[0]
    else:
        sim_mos(name_var.get())

def add_entry():
    if name_var.get() == "" or id_var.get() == ""  or type_var.get() == "" or address_var.get() == "" or coord_var.get() == "" or imam_var.get() == "":
        messagebox.showwarning("Warning", "Please fill all fields! ")
        return
    
    if not id_var.get().isdigit():
          messagebox.showwarning("Warning", "ID must be a number!")
          return
    if type_var.get() == "":
          messagebox.showwarning("Warning", "Please select a Type!")
          return
    new_mosque = Mosque(int(id_var.get()),name_var.get(),type_var.get(),address_var.get(),coord_var.get(),imam_var.get())
    try:
       db.Insert(new_mosque.mosque_id,new_mosque.name,new_mosque.mosque_type,new_mosque.address,new_mosque.coordinates,new_mosque.imam_name)
       messagebox.showinfo("Success", f"Mosque '{name_var.get()}' added successfully!")
       clearEverything()
    except sqlite3.IntegrityError:
       messagebox.showerror("Error", "ID already exists!")
    

def delete_entry():
    if id_var.get() == "":
        messagebox.showwarning("Warning", "Please fill the ID field!")
        return
    
    if not id_var.get().isdigit():
        messagebox.showwarning("Warning", "ID must be a number!")
        return
    
    all_mosques = db.Display()
    mosque_exists = False
    for record in all_mosques:
        if record[0] == int(id_var.get()): 
            mosque_exists = True
            break
    
    if not mosque_exists:
        messagebox.showwarning("Warning", f"No mosque found with ID: {id_var.get()}")
        return
    
    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete mosque with ID {id_var.get()}?")
    
    if confirm:
        db.Delete(int(id_var.get()))
        messagebox.showinfo("Success", f"Mosque with ID {id_var.get()} deleted successfully!")
        listbox1.delete(0, END)
        id_var.set("")
    else:
        messagebox.showinfo("Cancelled", "Delete operation cancelled")   
    
def update_imam():
    global cm_id,imamPre
    if cm_id is None:
        messagebox.showwarning("Warning", "Please search for a mosque first before updating!")
        return
    
    if imam_var.get()=="":
         messagebox.showwarning("Warning", f"Please fill the Imam Name field with the new name!")
         return
    if imamPre.lower()==imam_var.get().lower():
        messagebox.showwarning("Duplicate Name","The entered Imam Name is the same as the current one.\nPlease enter a different Imam Name.")
        return
    confirm = messagebox.askyesno("Confirm Update", f"Update Imam Name to '{imam_var.get()}'?")
    if confirm:
        db.UpdateImam(cm_id, imam_var.get())
        messagebox.showinfo("Success", "Imam Name updated successfully.")
        record = db.Search(name_var.get())
        listbox1.delete(0, END)
        listbox1.insert(END, f"{record[0]} | {record[1]} | {record[2]} | {record[3]} | {record[4]} | {record[5]}")
    clearEverything()
    cm_id=None

def display_on_map():
    global cm_id

    if os.path.exists("mosque_map.html"):
        os.remove("mosque_map.html")
    if cm_id is None:
        messagebox.showwarning("Warning", "Please search for a mosque first!")
        return

    if coord_var.get() == "":
        messagebox.showwarning("Warning", "Please fill the coordinates field!")
        return
    
    try:
        parts = coord_var.get().split(",")
        lat = float(parts[0].strip())  
        lon = float(parts[1].strip())   
    except:
        messagebox.showwarning("Warning", "Invalid coord_var.get() format! Please use: latitude,longitude (e.g., 24.7136,46.6753)")
        return
    
    mosque_map = folium.Map(location=[lat, lon], zoom_start=15)
    folium.Marker([lat, lon],popup=name_var.get(),tooltip=name_var.get(),icon=folium.Icon(color="green", icon="mosque", prefix='fa')).add_to(mosque_map)
    
    folium.TileLayer('OpenStreetMap').add_to(mosque_map)
    
    map_file = "mosque_map.html"
    mosque_map.save(map_file)
    
    webbrowser.open(map_file)
    messagebox.showinfo("Map", f"Opening map for {name_var.get()}")

def sim_mos(misName): 
    all_mosques = db.Display()
    if not all_mosques:
        messagebox.showinfo("No Data", "No mosques in database!")
        return
    
    mosName = [record[1] for record in all_mosques]
    
    sug = difflib.get_close_matches(misName, mosName, cutoff=0.4, n=5)
    
    if sug:
        sugDialog(misName, sug)
    else:
        messagebox.showinfo("Not Found", f"No mosque found with name: '{misName} in the database.")


def sugDialog(misName, suggestions):
    
    sugWin = Toplevel(root)
    sugWin.title("Did you mean?")
    sugWin.geometry("400x300")
    sugWin.resizable(False, False)
    
    Label(sugWin,text=f"No exact match for: '{misName}'",font=("Arial", 10, "bold")).pack(pady=10)
    
    Label(sugWin, text="Did you mean one of these?",font=("Arial", 10)).pack(pady=5)
    
    sugListbox = Listbox(sugWin, height=5, font=("Arial", 11))
    sugListbox.pack(pady=10, padx=20, fill=BOTH, expand=True)
    
    for suggestion in suggestions:
        sugListbox.insert(END, suggestion)
    
    def on_select():
        selected = sugListbox.curselection()
        if selected:
            chosenname = sugListbox.get(selected[0])
            name_var.set(chosenname)
            sugWin.destroy()
            search()
    
    def on_cancel():
        sugWin.destroy()
        messagebox.showinfo("Search Cancelled", "Search was cancelled.")
    
    bFrame = Frame(sugWin)
    bFrame.pack(pady=10)
    
    Button(bFrame, text="Select This", command=on_select, width=12).pack(side=LEFT, padx=5)
    Button(bFrame, text="Cancel", command=on_cancel, width=12).pack(side=LEFT, padx=5)
    
    sugListbox.bind("<Double-Button-1>", lambda e: on_select())


def clearEverything():
       id_var.set("")
       name_var.set("")
       type_var.set("")
       address_var.set("")
       coord_var.set("")
       imam_var.set("")


root = Tk()
db = Database()
root.title("Mosques Management System")
root.geometry("850x400")



id_var = StringVar()
name_var = StringVar()
type_var = StringVar()
address_var = StringVar()
coord_var = StringVar()
imam_var = StringVar()
cm_id = None

l1 = Label(root, text="ID")
l1.grid(row=0, column=0, padx=5, pady=5)

l2 = Label(root, text="Name")
l2.grid(row=0, column=2, padx=5, pady=5)

l3 = Label(root, text="Type")
l3.grid(row=1, column=0, padx=5, pady=5)

l4 = Label(root, text="Address")
l4.grid(row=1, column=2, padx=5, pady=5)

l5 = Label(root, text="Coordinate")
l5.grid(row=2, column=0, padx=5, pady=5)

l6 = Label(root, text="Imam Name")
l6.grid(row=2, column=2, padx=5, pady=5)

t1 = Entry(root, textvariable=id_var, width=20)
t1.grid(row=0, column=1, padx=5, pady=5)

t2 = Entry(root, textvariable=name_var, width=20)
t2.grid(row=0, column=3, padx=5, pady=5)

type_options = ["Masjid", "Al-Jamie", "Musalla Al-Eid"] 
t3 = OptionMenu(root, type_var, *type_options)
t3.config(width=15)
t3.grid(row=1, column=1, padx=5, pady=5)

t4 = Entry(root, textvariable=address_var, width=20)
t4.grid(row=1, column=3, padx=5, pady=5)

t5 = Entry(root, textvariable=coord_var, width=20)
t5.grid(row=2, column=1, padx=5, pady=5)

t6 = Entry(root, textvariable=imam_var, width=20)
t6.grid(row=2, column=3, padx=5, pady=5)

b1 = Button(root, height=1, width=12, text="Display All",command=display_all_mosques)
b1.grid(row=3, column=1, padx=5, pady=5)

b2 = Button(root, height=1, width=12, text="Search By Name",command=search)
b2.grid(row=3, column=2, padx=5, pady=5)

b3 = Button(root, height=1, width=12, text="Update Entry",command=update_imam)
b3.grid(row=3, column=3, padx=5, pady=5)

b4 = Button(root, height=1, width=12, text="Add Entry",command=add_entry)
b4.grid(row=4, column=1, padx=5, pady=5)

b5 = Button(root, height=1, width=12, text="Delete entry",command=delete_entry)
b5.grid(row=4, column=2, padx=5, pady=5)

b6 = Button(root, height=1, width=12, text="Display on Map",command=display_on_map)
b6.grid(row=4, column=3, padx=5, pady=5)

listbox1 = Listbox(root, height=10, width=60)
listbox1.grid(row=0, column=4, columnspan=3, rowspan=5, padx=5, pady=5, sticky="nsew")

scrollbar = Scrollbar(root, orient=VERTICAL, command=listbox1.yview)
scrollbar.grid(row=0, column=7, rowspan=5, sticky="ns", padx=(0, 5), pady=5)

listbox1.config(yscrollcommand=scrollbar.set)

root.mainloop()