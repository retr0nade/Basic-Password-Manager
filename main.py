from tkinter import *
from tkinter import messagebox
import sqlite3
from PIL import Image, ImageTk
import pyperclip
import os
from cryptography.fernet import Fernet
import ctypes

#master password integration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
PIN_FILE_PATH = os.path.join(ASSETS_DIR, "master_pin.txt")

if not os.path.exists(PIN_FILE_PATH):
    with open(PIN_FILE_PATH, "w") as f:
        f.write("1234")
    
    
def ask_master_pin():
    window.withdraw()
    pin_window= Toplevel()
    pin_window.title('Enter Master PIN')
    pin_window.geometry('300x150')
    pin_window.resizable(False, False)
    pin_window.grab_set()
    pin_window.protocol("WM_DELETE_WINDOW", window.quit)
    
    Label(pin_window, text='Enter 4 Digit master PIN: ', font=('Arial',12,'bold')).pack(pady=10)
    pin_var = StringVar()
    pin_entry = Entry(pin_window, textvariable=pin_var, font=('Arial', 12), show='*', justify='center')
    pin_entry.pack()
    
    def validate_pin():
        entered_pin = pin_var.get().strip()
        if len(entered_pin)!= 4 or not entered_pin.isdigit():
            messagebox.showwarning("Error", "PIN must be 4 digits.")
            return
        
        with open(PIN_FILE_PATH, 'r') as f:
            correct_pin = f.read().strip()
        
        if entered_pin == correct_pin:
            pin_window.destroy()
            window.deiconify()
            main_frame.grid()
        else:
            messagebox.showerror("Incorrect PIN", "The PIN you entered is Incorrect!")
            
    Button(pin_window, text='Login', font=('Arial', 12), command=validate_pin).pack(pady=10)
    pin_entry.focus()
    
    
window = Tk()
window.withdraw()
window.title("Password Manager")
#disabling window resizing (it ruins the the UI completely)
window.resizable(False, False)
if os.name == 'nt':
    hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
    style = ctypes.windll.user32.GetWindowLongW(hwnd, -16)
    style &= ~0x00010000 
    ctypes.windll.user32.SetWindowLongW(hwnd, -16, style)
#window.config(pady = 50)

#key generation
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
KEY_PATH = os.path.join(ASSETS_DIR, 'key.key')

def load_key():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    if os.path.exists(KEY_PATH):
        with open(KEY_PATH, 'rb') as key_file:
            return key_file.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_PATH, 'wb') as key_file:
            key_file.write(key)
        return key

key = load_key()
fernet = Fernet(key)

#ADD CREDENTIALS PAGE
#creating frames
side_frame = Frame(window, width=150, bg='lightgray')
side_frame.grid(column=0, row=0, sticky='ns')

main_frame = Frame(window, padx=50, pady = 50)
main_frame.grid(column=1, row=0, sticky='nsew')

#sidebar frames
option_label = Label(side_frame, text= 'Options', font=('Arial', 13, 'bold'))
option_label.grid(column=0, row=0,pady=(0, 10))

def show_addcredspage():
    view_frame.grid_remove()
    main_frame.grid()

addcred_button = Button(side_frame, text='Add Credentials',width=20, command=show_addcredspage)
addcred_button.grid(column=0, row=1, pady = 5)



exitcred_button = Button(side_frame, text='Exit', command = window.quit,width=20)
exitcred_button.grid(column=0, row=3, pady=(120, 0), sticky='sw')

#credentials adding 
menu1_label = Label(main_frame, text='Add Credentials', font=('Arial',16,'bold'))
menu1_label.grid(column=0, row=0, columnspan=2, pady=(0,20), padx=(60,0))

website_label = Label(main_frame, text = 'Website: ')
website_label.grid(column = 0, row = 1)
website_entry = Entry(main_frame,width=40, bg= 'lightgray')
website_entry.grid(column=1, row= 1, columnspan=2)
website_entry.focus()

user_label = Label(main_frame,text= 'Username: ')
user_label.grid(column=0, row=2)
user_entry = Entry(main_frame,width=40, bg= 'lightgray')
user_entry.grid(column=1, row=2,columnspan=2)

pass_label = Label(main_frame,text='Password: ')
pass_label.grid(column=0, row=3)
pass_entry = Entry(main_frame,width=40, bg= 'lightgray')
pass_entry.grid(column=1, row=3)


#clear credentials button
def clear_fields():
    is_clear = messagebox.askokcancel(title='Clear Fields?', message='Are you sure you want to clear all fields?' )
    if is_clear:
        website_entry.delete(0, 'end')
        user_entry.delete(0, 'end')
        pass_entry.delete(0, 'end')
    
clear_label = Button(main_frame,text= 'Clear Fields', command = clear_fields)
clear_label.grid(column=0, row=4, pady = 10, padx=(10, 5))

#credentials saving
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
DB_PATH = os.path.join(ASSETS_DIR, 'passwords.db')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS passwords (id INTEGER PRIMARY KEY AUTOINCREMENT, website TEXT NOT NULL, username TEXT NOT NULL, password TEXT NOT NULL)")
conn.commit()



def save_password():
    website = website_entry.get()
    username = user_entry.get()
    raw_password = pass_entry.get()
    password = fernet.encrypt(raw_password.encode()).decode()
    
    if website == '' or username == '' or password == '':
        messagebox.showwarning(title='Error', message="Please don't leave fields empty.")
    else:
        is_ok = messagebox.askokcancel(title='Confirm?', message=f"Entered Detais:\nUsername: {username}\nPassword: {raw_password}")
        if is_ok:
            cursor.execute('INSERT INTO passwords (website, username, password) VALUES (?, ?, ?)',(website,username,password))
            conn.commit()
            
            website_entry.delete(0, 'end')
            user_entry.delete(0, 'end')
            pass_entry.delete(0, 'end')
            
            messagebox.showinfo(title= 'Success',message='Credentials saved successfully')
    

add_button = Button(main_frame,text='Add Credentials',width=20, command= save_password)
add_button.grid(column=1,  row= 4, pady= 10, padx=(5, 10))


#VIEW CREDENTIALS PAGE
view_frame = Frame(window)
view_frame.grid(row=0, column=1, sticky='nsew')
view_frame.grid_remove()

base_path = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(base_path, "assets", "copy_icon.png")
copy_icon = Image.open(icon_path)
copy_icon = copy_icon.resize((18,18), Image.LANCZOS)
copy_photo = ImageTk.PhotoImage(copy_icon)



def show_viewcreds():
    main_frame.grid_remove()
    view_frame.grid()

    # Clear existing widgets
    for widget in view_frame.winfo_children():
        widget.destroy()

    title = Label(view_frame, text='Saved Credentials', font=('Arial', 16, 'bold'))
    title.pack(pady=(10, 10))

    #adding a search option
    search_var = StringVar()
    search_entry = Entry(view_frame, textvariable=search_var, width=40, font=('Arial',12))
    search_entry.pack(pady=(0,10))
    search_entry.insert(0, "Search by website or username...")
    search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, 'end'))
    
    canvas = Canvas(view_frame, height=200)  
    scrollbar = Scrollbar(view_frame, orient='vertical', command=canvas.yview)
    scrollable_frame = Frame(canvas)
    scrollable_frame.copy_photo = copy_photo

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    scrollable_frame.bind_all("<MouseWheel>", _on_mousewheel)


    canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')

    # Fetch and display credentials
    cursor.execute("SELECT id, website, username, password FROM passwords")
    records = cursor.fetchall()

    def display_records(filtered_records):
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
            
        if not filtered_records:
            Label(scrollable_frame, text="No matching records found!", font=("Arial",13)).pack(pady=10)
            
        for record in filtered_records:
            cred_id, website, username, encyrpted_password = record
            try:
                password = fernet.decrypt(encyrpted_password.encode()).decode()
            except Exception:
                password = "Decryption Failed"
        
            cred_frame = Frame(scrollable_frame, bg='lightgray', padx=10, pady=10, bd=1, relief='solid')
            cred_frame.pack(padx=10, pady=5, fill='x')

            Label(cred_frame, text=f'Website: {website}', anchor='w', font=('Arial', 10, 'bold'), bg='lightgray').pack(fill='x')

            user_frame = Frame(cred_frame, bg='lightgray')
            user_frame.pack(fill='x')
            Label(user_frame, text=f'Username: {username}', anchor='w', bg='lightgray').pack(side='left')
            Button(user_frame, image=copy_photo, command=lambda user=username: pyperclip.copy(user), bd=0, bg='lightgray', activebackground='lightgray').pack(side='right', padx=(5, 0))

            pw_frame = Frame(cred_frame, bg='lightgray')
            pw_frame.pack(fill='x')
            Label(pw_frame, text=f'Password: {password}', anchor='w', bg='lightgray').pack(side='left')
            Button(pw_frame, image=copy_photo, command=lambda pw=password: pyperclip.copy(pw), bd=0, bg='lightgray', activebackground='lightgray').pack(side='right', padx=(5, 0))

            btn_frame = Frame(cred_frame, bg='lightgray')
            btn_frame.pack(anchor='e', pady=(5, 0))

            Button(btn_frame, text='Edit', command=lambda id=cred_id, site=website, user=username, pw=password: edit_credential(id, site, user, pw)).pack(side='left', padx=(0, 5))
            Button(btn_frame, text='Delete', command=lambda id=cred_id: delete_credential(id)).pack(side='left')

    def update_search(*args):
        query = search_var.get().lower()
        filtered = [rec for rec in records if query in rec[1].lower() or query in rec[2].lower()]
        display_records(filtered)

    search_var.trace_add("write", update_search)
    display_records(records)
            
    if not records:
        Label(scrollable_frame, text='No passwords saved yet. Go add some.', font=('Arial', 13)).pack(pady=10)
        return

    for record in records:
        cred_id, website, username, encyrpted_password = record
        
        try:
            password = fernet.decrypt(encyrpted_password.encode()).decode()
        except Exception as e:
            password = 'Decryption Failed'

        cred_frame = Frame(scrollable_frame, bg='lightgray', padx=10, pady=10, bd=1, relief='solid')
        cred_frame.pack(padx=10, pady=5, fill='x')

        Label(cred_frame, text=f'Website: {website}', anchor='w', font=('Arial',10, 'bold'), bg='lightgray').pack(fill='x')
        
        user_frame = Frame(cred_frame, bg='lightgray')
        user_frame.pack(fill='x')
        Label(user_frame, text=f'Username: {username}', anchor='w', bg='lightgray').pack(side='left')
        Button(user_frame, image=copy_photo, command=lambda user=username: pyperclip.copy(user), bd=0, bg='lightgray', activebackground='lightgray').pack(side='right', padx=(5,0))
        
        pw_frame =  Frame(cred_frame, bg='lightgray')
        pw_frame.pack(fill='x')
        Label(pw_frame, text=f'Password: {password}', anchor='w', bg='lightgray').pack(side='left')
        Button(pw_frame, image=copy_photo, command=lambda pw=password: pyperclip.copy(pw), bd=0, bg='lightgray',activebackground='lightgray').pack(side='right',padx=(5,0))        
        btn_frame = Frame(cred_frame, bg='lightgray')
        btn_frame.pack(anchor='e', pady=(5, 0))

        Button(btn_frame, text='Edit', command=lambda id=cred_id, site=website, user=username, pw=password: edit_credential(id, site, user, pw)).pack(side='left', padx=(0, 5))
        Button(btn_frame, text='Delete', command=lambda id=cred_id: delete_credential(id)).pack(side='left')

def edit_credential(cred_id, current_website, current_username, current_password):
    edit_win = Toplevel()
    edit_win.title("Edit Credential")
    edit_win.resizable(False, False)
    
    Label(edit_win, text='Website: ').grid(row=0, column=0, padx=10, pady=5, sticky='e')
    website_entry = Entry(edit_win, width=30, bg = 'lightgray')
    website_entry.insert(0, current_website)
    website_entry.grid(row=0, column=1, padx=10, pady=5)
    
    Label(edit_win, text='Username: ').grid(row=1, column=0, padx=10, pady=5, sticky='e')
    username_entry = Entry(edit_win, width=30, bg = 'lightgray')
    username_entry.insert(0, current_username)
    username_entry.grid(row=1, column=1, padx=10, pady=5)
    
    Label(edit_win, text='Password: ').grid(row=2, column=0, padx=10, pady=5, sticky='e')
    password_entry = Entry(edit_win, width=30, bg = 'lightgray')
    password_entry.insert(0, current_password)
    password_entry.grid(row=2, column=1, padx=10, pady=5)
    
    def save_changes():
        new_website = website_entry.get().strip()
        new_username = username_entry.get().strip()
        new_pasword = password_entry.get().strip()
        
        if not new_website or not new_pasword or not new_username:
            messagebox.showerror("Error", "Please don't leave any fields empty.")
            return
        
        encrypted_password =  fernet.encrypt(new_pasword.encode())
        cursor.execute("UPDATE passwords SET website=?, username=?, password=? WHERE id=?",(new_website,new_username,encrypted_password.decode(),cred_id))
        conn.commit()
        messagebox.showinfo("Success", "Credentials updated successfully!")
        edit_win.destroy()
        show_viewcreds()
    
    Button(edit_win, text='Save', command=save_changes).grid(row=3, column=0, columnspan=1, pady=10)

        
def delete_credential(cred_id):
    confirm = messagebox.askyesno('Confirm Delete?', 'Are you sure you want to delete this credential?')
    
    if confirm:
        cursor.execute("DELETE FROM passwords WHERE id = ?", (cred_id,))
        conn.commit()
        show_viewcreds()
        
    
viewcred_button = Button(side_frame, text='View Saved Passwords',width=20, command=show_viewcreds)
viewcred_button.grid(column=0, row=2, pady= 5)

if __name__ == "__main__":
    ask_master_pin()
window.mainloop()

