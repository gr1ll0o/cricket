import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from tkinter import ttk
from PIL import Image, ImageTk
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import threading
import time

'''
#TODO - Hacer consola de logs de envios de mails [✅]
#TODO - Importar mails a través de un archivo [✅]
#TODO - Eliminar el CC [✅]
#TODO - Importar mails manualmente [✅]
#TODO - Enviar a un solo mail (envío rápido) [✅]
#TODO - Eliminar un mail de una lista [✅]
#TODO - Enviar a toda la base de datos [✅]
#TODO - Detectar si el mail ya existe en la lista [✅]
#TODO - Añadir imagenes [✅]
#TODO - Permitir estilizado de texto [✅]
#TODO - Corregir invisibiliad de "Email de ..." al presionar en cualquier parte de la pantalla
#TODO - Añadir botones de estilizado de texto
#TODO - Añadir "Firmas"
#TODO - Aviso de un email inválido/no enviado y borrado automatico de base de datos 
#TODO - Hacer ventana "Creditos" al apretar logo cricket

#TODO - Preparar inicio de la base de datos (creación del data.json)
'''

root = tk.Tk()
root.overrideredirect(True)
root.geometry("1000x600")
root.update_idletasks()
w = root.winfo_width();h = root.winfo_height();ws = root.winfo_screenwidth();hs = root.winfo_screenheight()
x = (ws // 2) - (w // 2)
y = (hs // 2) - (h // 2)
root.geometry(f"{w}x{h}+{x}+{y}")

# Cargar la imagen
img = Image.open("assets/img2.png")  # ejemplo: "logo.png"

json_global = ""
list_selected = ""

imgs = []
len_imgs = 0

def show_del_menu(event):
    try:
        listbox.get(listbox.curselection())
        dellist_menu.post(event.x_root, event.y_root)
    except:
        pass

def show_import_menu(event):
    try:
        listbox.get(listbox.curselection())
        addlist_menu.post(event.x_root, event.y_root)
    except:
        pass

def show_send_menu(event):
    send_menu.post(event.x_root, event.y_root)

def attach_img():
    global msg, len_imgs
    img_path = filedialog.askopenfilename(title="Seleccionar imagen para incrustar (opcional)", filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.gif")])
    if img_path:
        try:
            len_imgs += 1
            imgs.append((img_path, f'imagen{len_imgs}'))
            body_text.insert(tk.END, f'\n<img src="cid:imagen{len_imgs}">')
        except Exception as e: messagebox.showerror("Error", f"Hubo un error al adjuntar la imagen ({e})");return

def send_email(mail):
    global msg, imgs
    transmitter = 'thiagotobias.grillo@gmail.com'
    email_destiny = mail
    title_msg = subject_text.get("1.0", tk.END).strip()
    body_msg = body_text.get("1.0", tk.END).strip()

    # Configuración del servidor SMTP (Gmail en este caso)
    try:
        log("> Secuencia de Envío Iniciada")
        root.after(3000, log(f"Iniciando sesión en {transmitter}..."))
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)  # Conexión SSL
        server.login(transmitter, 'bffd paku mepd xake') # Iniciar sesión
        log("Iniciando envíos...\n")

        msg = MIMEMultipart('related')
        msg['Subject'] = title_msg
        msg['From'] = transmitter
        msg['To'] = email_destiny
        
        html = f"""
        <html>
          <body>
            <p>{body_msg.replace('\n', '<br>')}</p>
          </body>
        </html>
        """
        msg.attach(MIMEText(html, 'html'))
        if (imgs != []):
            for path, cid in imgs:
                with open(path, 'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-ID', f'<{cid}>')
                    msg.attach(img)
        
        server.sendmail(transmitter, mail, msg.as_string())
        log(f"Enviando mail a {mail}...")  
        server.quit()
        log("", False)
        log(f"Email a {mail} enviado con éxito.")
        messagebox.showinfo("Emails enviados", "Se han enviado todos los emails exitosamente.")
        imgs = []
        print("Correo enviado con éxito!")
    except Exception as e:
        messagebox.showerror("Error", f"Error al enviar los emails: {e}")
        print(f"Error al enviar el correo: {e}")

def fast_send():
    if (subject_text.get("1.0", tk.END).strip() == "" or body_text.get("1.0", tk.END).strip() == ""):messagebox.showerror("Error", "Escribe un asunto y un mensaje.");return
    mail = simpledialog.askstring("Envío rápido", " Ingrese el e-mail particular de destino. ", parent=root)
    if mail == None: return # Cancel
    elif mail == "": messagebox.showerror("Mail inválido", "Introduzca un mail válido"); return
    elif mail != "": 
        if "@" not in mail or "." not in mail: 
            messagebox.showerror("Mail inválido", "Introduce un mail válido");return
        else:
            start_sending_emails(2, mail)

def send_all_database():
    if (subject_text.get("1.0", tk.END).strip() == "" or body_text.get("1.0", tk.END).strip() == ""): messagebox.showerror("Error", "Escribe un asunto y un mensaje.");return
    all = []
    for list in data:
            for mail in data[list]:
                all.append(mail)
    c = messagebox.askokcancel("Advertencia", f"Está a punto de enviar un email a TODA la base de datos ({len(all)}), ¿Está seguro?")
    if (c): start_sending_emails(3)

def add_list_imports(name):
    try:
        file = filedialog.askopenfile(mode='r', title="Selecciona archivo para importar mails", filetypes=[("Archivos de texto", "*.txt")])
    except Exception as e: messagebox.showerror("Error", f"Ha ocurrido un error al leer el archivo ({e})")
    if file:
        content = file.readlines()
        file.close()
        emails = [line.strip() for line in content]  # Elimina saltos de línea
        json_global[name] = emails
        try: update_display_emails(name);write_json_lists('data.json');read_json_lists('data.json')
        except: messagebox.showerror("Error", "Ha ocurrido un error al actualizar la lista de emails");return
        messagebox.showinfo("Importación exitosa", f"Se han importado {len(emails)} mails a {name}")

def log(msg, showtime=True):
    console_text.config(state=tk.NORMAL)
    if(showtime): console_text.insert(tk.END, "<" + time.strftime("%H:%M") + "> " + msg + "\n")
    else: console_text.insert(tk.END, msg + "\n")
    console_text.see(tk.END) 
    console_text.config(state=tk.DISABLED)

def del_email():
    selected_list = listbox.get(listbox.curselection())
    key = selected_list.split(" (")[0]
    e_mails = data[key]
    text = "";i=0
    for mail in e_mails:
        i+=1
        text += f"{i}) {mail}\n"
    try:
        try: mail = simpledialog.askinteger("Eliminar mail", f"Selecciona email a eliminar\n{text}", parent=root)
        except: return;
        erased = json_global[key].pop(mail-1)
        write_json_lists('data.json')
        update_display_emails(key)
        read_json_lists('data.json')
        messagebox.showinfo("Email eliminado", f"Se ha eliminado el mail {erased}de la lista {key} con éxito")
    except Exception as e: messagebox.showerror("Error", "Seleccione un número válido");return
    

def add_email():
    selected_list = listbox.get(listbox.curselection())
    key = selected_list.split(" (")[0]
    mails = []
    mail = "X"
    while (mail != ""):
        root.lift()
        root.focus_force()
        mail = simpledialog.askstring("Importar email", "Ingrese un e-mail y presione OK para añadir otro (Deje vacio para finalizar la asignación de correos)", parent=root)
        if mail == None: return # Cancel
        elif mail == "" and mails == []: messagebox.showerror("Error", "Debe añadir por lo menos un e-mail a la nueva lista."); return
        elif mail != "": 
            if "@" not in mail or "." not in mail: 
                messagebox.showerror("Mail inválido", "Introduce un mail válido")
            elif mail in data[key] or mail in mails: messagebox.showerror("Mail duplicado", "Ya existe esta dirección en la lista.")
            else:
                mails.append(mail)
        
    data[key] += mails
    try: update_display_emails(key);write_json_lists('data.json');read_json_lists('data.json')
    except: messagebox.showerror("Error", "Ha ocurrido un error al actualizar la lista de emails");return
    messagebox.showinfo("Importación exitosa", f"Se han importado {len(mails)} mails a {key}")

def import_file():
    global json_global, list_selected

    try:
        selected_list = listbox.get(listbox.curselection())
        key = selected_list.split(" (")[0]
        c = messagebox.askyesnocancel("Atención", message=f'Está por importar mails a {selected_list}, pulse "No" para crear una nueva lista de importación o "Si" para proseguir')
        print(c)
        if c:
            print(json_global)
            try:
                file = filedialog.askopenfile(mode='r', title="Selecciona archivo para importar mails", filetypes=[("Archivos de texto", "*.txt")])
            except Exception as e: messagebox.showerror("Error", f"Ha ocurrido un error al leer el archivo ({e})")
            if file:
                content = file.readlines()
                file.close()
                emails = [line.strip() for line in content]  # Elimina saltos de línea
                new_emails = [email for email in emails if email not in json_global[key]]
                json_global[key] += new_emails
                try: update_display_emails(key);write_json_lists('data.json');read_json_lists('data.json')
                except: messagebox.showerror("Error", "Ha ocurrido un error al actualizar la lista de emails");return
                messagebox.showinfo("Importación exitosa", f"Se han importado {len(new_emails)} mails a {key}")
        elif c == False: 
            print(json_global)
            name = simpledialog.askstring("Crear lista de importación", "Ingrese el nombre de la nueva lista", parent=root)
            if name == '': messagebox.showinfo("Nombre inválido", "Debes añadir un nombre a la lista");return
            if (json_global != {}):
                for list in lists:
                    if (name == list):
                        messagebox.showerror("Lista duplicada", "Ya existe una lista con este nombre");return
            if (not name): return
            add_list_imports(name)
        else: return
    except Exception as e:
        print(e)
        name = simpledialog.askstring("Crear lista de importación", "Ingrese el nombre de la nueva lista", parent=root)
        if name == '': messagebox.showinfo("Nombre inválido", "Debes añadir un nombre a la lista");return
        if (json_global != {}):
            for list in lists:
                if (name == list):
                    messagebox.showerror("Lista duplicada", "Ya existe una lista con este nombre");return
        if (not name): return
        add_list_imports(name)

def start_sending_emails(mode=1, mail_from_mode_2=None):
    if mode == 1: # Multi emails (default)
        try:
            selected_list = listbox.get(listbox.curselection())
            key = selected_list.split(" (")[0]
        except:
            messagebox.showerror("Error", "Selecciona una lista de e-mails");return
        
        if (subject_text.get("1.0", tk.END).strip() == "" or body_text.get("1.0", tk.END).strip() == ""):
            messagebox.showerror("Error", "Escribe un asunto y un mensaje.");return

        print(f'LISTA SELECCIONADA: {key}')
        print(f"EMAILS: {data[key]}")
        print(f'ASUNTO: {subject_text.get("1.0", tk.END)}')
        print(f'MENSAJE: {body_text.get("1.0", tk.END)}')
        threading.Thread(target=send_emails).start()
    elif mode == 2: # Fast Mode
        print(f"EMAIL: {mail_from_mode_2}")
        print(f'ASUNTO: {subject_text.get("1.0", tk.END)}')
        print(f'MENSAJE: {body_text.get("1.0", tk.END)}')
        threading.Thread(target=send_email, args=(mail_from_mode_2,)).start()
    elif mode == 3: # ALL DATABASE
        all = []
        for list in data:
            for mail in data[list]:
                all.append(mail)
        print(all)
        print(f"ENVIO A TODA LA BASE")
        print(f'ASUNTO: {subject_text.get("1.0", tk.END)}')
        print(f'MENSAJE: {body_text.get("1.0", tk.END)}')
        threading.Thread(target=send_all_emails, args=(all,)).start()
    else: # Error
        raise Exception("Modo no válido")

def send_emails():
    transmitter = 'thiagotobias.grillo@gmail.com'
    selected_list = listbox.get(listbox.curselection())
    key = selected_list.split(" (")[0]
    emails_destiny = data[key]
    title_msg = subject_text.get("1.0", tk.END)
    body_msg = body_text.get("1.0", tk.END)

    # Configuración del servidor SMTP (Gmail en este caso)
    try:
        log("> Secuencia de Envío Iniciada")
        root.after(3000, log(f"Iniciando sesión en {transmitter}..."))
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)  # Conexión SSL
        server.login(transmitter, 'bffd paku mepd xake') # Iniciar sesión
        log("Iniciando envíos...\n")
        i=1
        for recipient in emails_destiny:
            msg = MIMEMultipart('related')
            msg['Subject'] = title_msg
            msg['From'] = transmitter
            msg['To'] = recipient

            html = f"""
            <html>
              <body>
                <p>{body_msg.replace('\n', '<br>')}</p>
              </body>
            </html>
            """
            msg.attach(MIMEText(html, 'html'))
            if (imgs != []):
                for path, cid in imgs:
                    with open(path, 'rb') as f:
                        img = MIMEImage(f.read())
                        img.add_header('Content-ID', f'<{cid}>')
                        msg.attach(img)

            server.sendmail(transmitter, recipient, msg.as_string())
            log(f"Enviando mail a {recipient} ({i}/{len(emails_destiny)})")
            i+=1
            
        server.quit()
        log("", False)
        log(f"{i-1} de {len(emails_destiny)} emails enviados con éxito.")
        messagebox.showinfo("Emails enviados", "Se han enviado todos los emails exitosamente.")
        print("Correo enviado con éxito!")
    except Exception as e:
        messagebox.showerror("Error", f"Error al enviar los emails: {e}")
        print(f"Error al enviar el correo: {e}")

def send_all_emails(list):
    transmitter = 'thiagotobias.grillo@gmail.com'
    emails_destiny = list
    title_msg = subject_text.get("1.0", tk.END)
    body_msg = body_text.get("1.0", tk.END)

    # Configuración del servidor SMTP (Gmail en este caso)
    try:
        log("======================", False)
        log("     CRICKET v1.0     ", False)
        log("  by Grillo Software  ", False)
        log("======================\n", False)
        root.after(3000, log(f"Iniciando sesión en {transmitter}..."))
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)  # Conexión SSL
        server.login(transmitter, 'bffd paku mepd xake') # Iniciar sesión
        log("Iniciando envíos...\n")
        i=1
        for recipient in emails_destiny:
            msg = MIMEText(body_msg) # CUERPO/MENSAJE
            msg['Subject'] = title_msg # ASUNTO
            msg['From'] = transmitter # EMISOR
            msg['To'] = recipient #RECEPTOR

            server.sendmail(transmitter, recipient, msg.as_string())
            log(f"Enviando mail a {recipient} ({i}/{len(emails_destiny)})")
            i+=1
            
        server.quit()
        log("", False)
        log(f"{i-1} de {len(emails_destiny)} emails enviados con éxito.")
        messagebox.showinfo("Emails enviados", "Se han enviado todos los emails exitosamente.")
        print("Correo enviado con éxito!")
    except Exception as e:
        messagebox.showerror("Error", f"Error al enviar los emails: {e}")
        print(f"Error al enviar el correo: {e}")

def on_click_list(event):
    try:
        widget = event.widget
        selection = widget.curselection()
        if selection: selected_item = widget.get(selection[0])
        list_selected = selected_item
        email_selected_label.configure(text=f'Enviar a {list_selected}')
        update_display_emails(selected_item)
    except:
        update_display_emails("")

def update_display_emails(selected_item):
    t=""
    key = selected_item.split(" (")[0]
    list_emails_label.config(text=f"E-mails de {key}")
    try:
        for mail in data[key]:
            t += f'{mail}\n'
        emails_display.config(state=tk.NORMAL)
        emails_display.delete('1.0', tk.END)
        emails_display.insert(tk.END, t)
        emails_display.config(state=tk.NORMAL)
    except:
        list_emails_label.config(text="")

def read_json_lists(dir):
    global listbox, json_global, data, lists_mails, lists
    try:
        with open(dir, 'r') as file:
            data = json.load(file)
            json_global = data
            lists = list(data.keys()) # LISTAS
            lists_mails = list(data.values()) # MAILS DE LAS LISTAS

        listbox.delete(0, tk.END)
        for lista in lists:
            listbox.insert(tk.END, f'{lista} ({len(data[lista])})')
    except:
        with open(dir, 'w') as file:
            file.write('')
        json_global = {}
    list_selected = listbox.get(tk.END).split(" (")[0]
    # print(json_global)

def write_json_lists(dir):
    global json_global
    with open(dir, 'w') as file:
        json.dump(json_global, file, ensure_ascii=False, indent=4)

def add_list():
    name = simpledialog.askstring("Crear lista", "Ingrese el nombre de la nueva lista", parent=root)
    if name == '': messagebox.showinfo("Nombre inválido", "Debes añadir un nombre a la lista");return
    if (json_global != {}):
        for list in lists:
            if (name == list):
                messagebox.showerror("Lista duplicada", "Ya existe una lista con este nombre");return
    if (not name): return
    mails = []
    mail = "X"
    while (mail != ""):
        root.lift()
        root.focus_force()
        mail = simpledialog.askstring("Crear lista", "Ingrese un e-mail y presione OK para añadir otro (Deje vacio para finalizar la asignación de correos)", parent=root)
        if mail == None: return # Cancel
        elif mail == "" and mails == []: messagebox.showerror("Error", "Debe añadir por lo menos un e-mail a la nueva lista."); return
        elif mail != "": 
            if "@" not in mail or "." not in mail: messagebox.showerror("Mail inválido", "Introduce un mail válido")
            elif mail in mails: messagebox.showerror("Mail duplicado", "Ya existe esta dirección en la lista.")
            else:
                mails.append(mail)
        
    json_global[name] = mails

    write_json_lists('data.json')
    read_json_lists('data.json')
    messagebox.showinfo("Lista creada", f"La lista {name} ha sido creada con éxito.")

def del_list():
    global json_global
    try:
        selected_list = listbox.get(listbox.curselection())
    except Exception as e:
        messagebox.showinfo("Eliminar lista", "Selecciona una lista para eliminar");return
    confirm = messagebox.askyesno("Eliminar lista", f"¿Desea eliminar la lista {selected_list}?")
    try:
        if confirm:
            key = selected_list.split(" (")[0]
            json_global.pop(key)
            write_json_lists('data.json')
            read_json_lists('data.json')
            messagebox.showinfo("Lista eliminada", f"Se eliminó la lista {selected_list}")
            emails_display.config(text="")
            email_selected_label.config(text="")
            list_emails_label.config(text="")
        else: pass
    except:
        emails_display.delete("1.0", tk.END)
        email_selected_label.config(text="")
        list_emails_label.config(text="")

def start_move(event): root.x = event.x; root.y = event.y

def do_move(event):
    x = event.x_root - root.x
    y = event.y_root - root.y
    root.geometry(f'+{x}+{y}')

def refresh():
    read_json_lists('data.json')

def close_window(): root.destroy()

#SECTION - Setup
title_bar = tk.Frame(root, bg="#000d21", relief='raised', bd=0, height=30)
title_bar.pack(fill=tk.X)
img = img.resize((50, 50), Image.LANCZOS).convert("RGBA")  # opcional, ajustar tamaño
photo = ImageTk.PhotoImage(img)
logo_img = tk.Label(title_bar, image=photo, bg="#000d21")
logo_img.place(x=7)
title = tk.Label(title_bar, text="cricket", bg="#000d21", fg="white", font=('Arial', 22, "italic bold"), pady=7)
title.place(x=64, y=3)
close_btn = tk.Button(title_bar, text=" X ",activebackground="#f00", activeforeground="#fff", command=close_window, bg="#000d21", fg="white", bd=0, padx=10, font=('Arial', 20, "bold"))
close_btn.pack(side=tk.RIGHT)
refresh_btn = tk.Button(title_bar, text="🔄",activebackground="#000c1e", activeforeground="#fff", command=refresh, bg="#000d21", fg="white", bd=0, padx=10, font=('Arial', 20, "bold"))
refresh_btn.pack(side=tk.RIGHT)
title_bar.bind('<Button-1>', start_move)
title_bar.bind('<B1-Motion>', do_move)
title.bind('<Button-1>', start_move)
title.bind('<B1-Motion>', do_move)
close_btn.bind('<Enter>', lambda e: close_btn.config(bg="#011d47"))
close_btn.bind('<Leave>', lambda e: close_btn.config(bg="#000d21"))
refresh_btn.bind('<Enter>', lambda e: refresh_btn.config(bg="#011d47"))
refresh_btn.bind('<Leave>', lambda e: refresh_btn.config(bg="#000d21"))
main_content = tk.Frame(root, bg="#001536")
main_content.pack(expand=True, fill=tk.BOTH)
#!SECTION

#SECTION - Elements

list_label = tk.Label(main_content, bg="#001536", fg="#fff", text="Listas de e-mails", font=('Arial', 16, "bold"))
list_label.place(x=15, y=10)

listbox = tk.Listbox(main_content, border=0)
listbox.config(font=('Arial', 20),background="#061E44", foreground="#fff", bd=0)
listbox.place(x=20, y=40, width=300, height=428)
listbox.bind("<<ListboxSelect>>", on_click_list)

addlist_btn = tk.Button(main_content, activebackground="#011330", activeforeground="#fff", text="Añadir", command=add_list, font=('Arial', 17), bg="#061E44", fg="#fff", bd=0)
addlist_btn.place(x=20, y=480)
addlist_btn.bind('<Button-3>', show_import_menu)
addlist_btn.bind('<Enter>', lambda e: addlist_btn.config(bg="#012965"))
addlist_btn.bind('<Leave>', lambda e: addlist_btn.config(bg="#061E44"))

dellist_btn = tk.Button(main_content, activebackground="#011330", activeforeground="#fff", command=del_list,text="Eliminar", font=('Arial', 17), bg="#061E44", fg="#fff", bd=0)
dellist_btn.place(x=113, y=480)
dellist_btn.bind('<Button-3>', show_del_menu)
dellist_btn.bind('<Enter>', lambda e: dellist_btn.config(bg="#012965"))
dellist_btn.bind('<Leave>', lambda e: dellist_btn.config(bg="#061E44"))

import_btn = tk.Button(main_content, activebackground="#011330", activeforeground="#fff",command=import_file, text="Importar", font=('Arial', 17), bg="#061E44", fg="#fff", bd=0)
import_btn.place(x=220, y=480)
import_btn.bind('<Enter>', lambda e: import_btn.config(bg="#012965"))
import_btn.bind('<Leave>', lambda e: import_btn.config(bg="#061E44"))

list_emails_label = tk.Label(main_content, bg="#001536", fg="#fff", text="", font=('Arial', 16, "bold"))
list_emails_label.place(x=332, y=10)

emails_frame = tk.Frame(main_content, bg="#001536")
emails_frame.place(x=335, y=40, width=300, height=410)
emails_display = tk.Text(emails_frame, bg="#001536", fg="#ffffff", font=('Arial', 9), wrap=tk.WORD, state=tk.DISABLED, relief=tk.FLAT, bd=0)
emails_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
emails_scrollbar = tk.Scrollbar(emails_frame, command=emails_display.yview)
emails_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
emails_display.config(yscrollcommand=emails_scrollbar.set)

separator = tk.Frame(root, bg="#082350", height=3, width=290)
separator.place(x=335, y=505)

subject_label = tk.Label(main_content, bg="#001536", fg="#fff", text="Asunto", font=('Arial', 12, "bold"))
subject_label.place(x=638, y=12)

subject_text = tk.Text(main_content, padx=5, pady=5, font=('Arial', 13), bg="#082350", fg="#fff", bd=0, height=1, width=37)
subject_text.configure(insertbackground="#fff")
subject_text.place(x=640, y=35)

body_label = tk.Label(main_content, bg="#001536", fg="#fff", text="Mensaje", font=('Arial', 12, "bold"))
body_label.place(x=638, y=76)

body_text = tk.Text(main_content, padx=5, pady=5, font=('Arial', 13), bg="#082350", fg="#fff", bd=0, width=37, height=18)
body_text.configure(insertbackground='#fff')
body_text.place(x=640, y=100)

email_selected_label = tk.Label(main_content, bg="#001536", fg="#fff", text="", font=('Arial', 10))
email_selected_label.place(x=842, y=460)

console_frame = tk.Frame(root, bg="#001536")
console_frame.place(x=332, y=515, width=509, height=85)
console_text = tk.Text(console_frame, bd=0, font=('Arial', 9), bg="#001536", fg="#ffffff", wrap=tk.WORD, state=tk.DISABLED, relief=tk.FLAT)
console_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar = tk.Scrollbar(console_frame, command=console_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
console_text.config(yscrollcommand=scrollbar.set)

attach_btn = tk.Button(main_content, command=attach_img, activebackground="#011330", activeforeground="#fff", text="📎", font=('Arial', 20), bg="#061E44", fg="#fff", bd=0)
attach_btn.place(x=925, y=395)
attach_btn.bind('<Enter>', lambda e: attach_btn.config(bg="#012965"))
attach_btn.bind('<Leave>', lambda e: attach_btn.config(bg="#061E44")) 

send_btn = tk.Button(main_content, command=start_sending_emails, activebackground="#011330", activeforeground="#fff", text="   Enviar   ", font=('Arial', 18), bg="#061E44", fg="#fff", bd=0)
send_btn.place(x=845, y=483)
send_btn.bind('<Button-3>', show_send_menu)
send_btn.bind('<Enter>', lambda e: send_btn.config(bg="#012965"))
send_btn.bind('<Leave>', lambda e: send_btn.config(bg="#061E44")) 

#!SECTION

#SECTION - Menues
dellist_menu = tk.Menu(root, tearoff=0, bg="#001536", fg="#ffffff")
dellist_menu.add_command(label="Eliminar un email", command=del_email)

addlist_menu = tk.Menu(root, tearoff=0, bg="#001536", fg="#ffffff")
addlist_menu.add_command(label="Añadir un email", command=add_email)

send_menu = tk.Menu(root, tearoff=0, bg="#001536", fg="#ffffff")
send_menu.add_command(label="Enviar a toda la base de datos", command=send_all_database)
send_menu.add_command(label="Envío rápido", command=fast_send)
#!SECTION

read_json_lists('data.json')
root.mainloop()