import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from tkinter import ttk
from PIL import Image, ImageTk
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
import threading
import time
import os
import sys
import shutil
from webbrowser import open_new

root = tk.Tk()
root.withdraw()
root.title("Cricket")
root.geometry("1000x600")
root.resizable(0, 0)
root.minsize(1000, 600)
root.maxsize(1000, 600)
root.update_idletasks()
w = root.winfo_width();h = root.winfo_height();ws = root.winfo_screenwidth();hs = root.winfo_screenheight()
x = (ws // 2) - (w // 2)
y = (hs // 2) - (h // 2)
root.geometry(f"{w}x{h}+{x}+{y}")

def show_splash():
    splash = tk.Toplevel()
    splash.overrideredirect(True)
    splash.geometry("500x300") 

    ws = splash.winfo_screenwidth()
    hs = splash.winfo_screenheight()
    x = (ws // 2) - (500 // 2)
    y = (hs // 2) - (300 // 2)
    splash.geometry(f"500x300+{x}+{y}")

    splash.configure(bg="#000d21")

    splash_img = Image.open(get_resource_path("assets/logo.png")).resize((250, 250))
    splash_photo = ImageTk.PhotoImage(splash_img)
    img_label = tk.Label(splash, image=splash_photo, bg="#000d21")
    img_label.image = splash_photo
    img_label.pack(pady=10)

    label = tk.Label(splash, text=f"Cricket v.{str(VERSION)}", font=('Courier New', 13), fg="#fff", bg="#000d21")
    label.place(y=257, x=178)

    def close_splash():
        splash.destroy()
        root.deiconify() 

    root.withdraw()
    splash.after(3000, close_splash)

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Images
img = Image.open(get_resource_path('assets/logo.png'))
img2 = Image.open(get_resource_path('assets/credits-image.png'))
img3 = Image.open(get_resource_path('assets/credits-image2.png'))
root.iconbitmap(get_resource_path("assets/icon.ico"))

font = "Arial"

user = ""
passw = ""
smtp_host = ""
smtp_port = 0

DATADIR = 'data.json'
CONFIGDIR = 'config.json'
after = ""

VERSION = 1.3
DATE = "23/07/2025"

json_global = {}
configs = {}

list_selected = ""
signature_path = ""

imgs = []
attachments = []
len_imgs = 0
onsending = False

def show_credits():
    credits = tk.Toplevel(root)
    credits.geometry("300x300")
    credits.title("Creditos")
    credits.overrideredirect(False)
    credits.resizable(False, False)
    credits.maxsize(300, 300)
    credits.minsize(300, 300)
    credits.config(bg="#001536")
    credits.iconbitmap(get_resource_path("assets/icon.ico"))

    label = tk.Label(credits, text="-- cricket --", font=('Arial', 26, 'bold italic'), bg="#001536", fg="#fff")
    label.place(relx=0.5, y=28, anchor="center")

    image = img2.resize((180, 180), Image.LANCZOS).convert("RGBA")  # opcional, ajustar tamaño
    photo = ImageTk.PhotoImage(image)
    image2 = img3.resize((180, 180), Image.LANCZOS).convert("RGBA")  # opcional, ajustar tamaño
    photo2 = ImageTk.PhotoImage(image2)
    logo_img = tk.Label(credits, image=photo, bg="#001536")
    logo_img.bind('<ButtonPress>', lambda e: logo_img.config(image=photo2))
    logo_img.bind('<ButtonRelease>', lambda e: logo_img.config(image=photo))
    logo_img.place(relx=0.5, y=131, anchor="center")

    ver = tk.Label(credits, text=f"Version {str(VERSION)} | Builded on {str(DATE)}", font=('Arial', 12), bg="#001536", fg="#fff")
    ver.place(relx=0.5, y=226, anchor="center")

    label2 = tk.Label(credits, text="Developed by Grillo", font=('Arial', 11), bg="#001536", fg="#fff")
    label2.place(relx=0.5, y=245, anchor="center")

    github = tk.Label(credits, text="GitHub", font=('Arial', 11, 'underline'), bg="#001536", fg="#2772E9", cursor="hand2")
    github.place(relx=0.5, y=270, anchor="center")
    github.bind("<Button-1>", lambda e: open_new("https://github.com/gr1ll0o/cricket"))

    credits.mainloop()

def show_settings_menu(event):
    if (onsending == True): return
    settings_menu.post(event.x_root, event.y_root)

def show_del_menu(event):
    try:
        if (onsending == True): return
        listbox.get(listbox.curselection())
        dellist_menu.post(event.x_root, event.y_root)
    except:
        pass

def show_import_menu(event):
    try:
        if (onsending == True): return
        listbox.get(listbox.curselection())
        addlist_menu.post(event.x_root, event.y_root)
    except:
        pass

def host_traduction(string):
    global smtp_port
    if string.lower() == "gmail.com": smtp_port = 465;return "smtp.gmail.com"
    if string.lower() == "yahoo.com": smtp_port = 587;return "smtp.mail.yahoo.com"
    if string.lower() == "outlook.com" or string.lower() == "hotmail": smtp_port = 587;return "smtp.office365.com"
    if not any(ext in string for ext in [".com", ".net", ".org", ".gov"]): return "Invalido"
    else: return string

def check_account():
    global passw, user, smtp_host, smtp_port
    hidden_pw = ""
    for i in list(passw):
        hidden_pw += "*"
    if (user != "" or passw != ""): 
        q = messagebox.askokcancel('Cuenta vinculada', f'Cuenta vinculada\n\nEMAIL: {user}\nPASSW: {hidden_pw}\nHOST: {smtp_host}\nPORT: {smtp_port}\n\nPresione "Cancelar" para cerrar sesión')
        if q == None or q == True: return
        else:
            q = messagebox.askyesno("Confirmar cierre de sesion", f"¿Estás seguro que queres cerrar sesión en {user}?")
            if (not q): return
            user = ""
            passw = ""
            smtp_host = ""
            smtp_port = 0
            configs['Email'] = user
            configs['Password'] = passw
            configs['Host'] = smtp_host
            configs['Port'] = smtp_port
            write_json_configs()
            read_json_configs()
            messagebox.showinfo("Sesión cerrada", "Se ha cerrado su sesión con éxito")
    else: vinculate_account()

def vinculate_account():
    global smtp_host, smtp_port, user, passw   
    c = messagebox.askokcancel("Vincular una cuenta", "Debe vincular su cuenta de servicio de mensajería para enviar correos electronicos. Siga a continuación las instrucciones para configurar su perfil.")
    if (c == False): return
    u = simpledialog.askstring("Vincular una cuenta", "Introduce el correo electrónico de envío")
    if u == None or u == "": return
    elif u != "": 
        if "@" not in u or "." not in u: 
            messagebox.showerror("Mail inválido", "Introduce un mail válido");return
    pw = simpledialog.askstring("Vincular una cuenta", "Introduce la contraseña del email (es posible que necesite utilizar una contraseña de aplicacion)")
    if pw == None or pw == "":return
    email_domain = u.split('@')[-1].lower().strip()
    print(email_domain)
    if (email_domain not in ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]):
        print("dominio inválido")
        q = simpledialog.askstring("Vincular una cuenta", "Introduce el host del servicio de mensajería (si su proveedor es Microsoft/Outlook, utilice smtp.office365.com)")
    else:
        q = email_domain
    if (q.strip().lower() not in ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]):
        p = simpledialog.askstring("Vincular una cuenta", "Parece que estás usando un dominio propio, introduzca el puerto de su conexión.")
        if (p == ""): messagebox.showerror("Error", "Debe especificar el puerto de la conexión a su dominio.");return
        else: smtp_port = p
    else: 
        email_domain = u.split('@')[-1].lower().strip()  # ejemplo: gmail.com
        service = q.lower().strip()
        if service not in email_domain: messagebox.showwarning("Error", f"El servicio ingresado {service} no coincide con el del mail {u} ingresado");return
    h = host_traduction(q)
    if (q == "Invalido"): messagebox.showerror("Error", "No es un host válido");return
    smtp_host = h
    messagebox.showinfo("Resumen de la cuenta", f"EMAIL: {u}\nPASSW: {pw}\nHOST: {smtp_host}\nPORT: {smtp_port}\n\nPresione aceptar para hacer la comprobación de conexión")
    request = try_to_connect(u, pw, h, smtp_port)
    print(request)
    if (request == "ConnectionError"): messagebox.showerror("Error", "No se ha podido conectar con el host. Verifique servicio ingresado y puerto de haber sido ingresado");return
    if (request == "LoginError"): messagebox.showerror("Error", "No se ha podido iniciar sesión. Verifique correo electrónico y contraseña. Pruebe generar una contraseña de aplicación desde su panel de control para usarla.");return
    if (request == "SendEmailError"): messagebox.showerror("Error", f"Su cuenta {u} parece no estar habilitada para enviar correos electrónicos desde aplicaciones de tercero. Verifique configuración y permisos de su dominio o email.");return
    user = u
    passw = pw
    smtp_host = h
    print(smtp_port)
    configs['Email'] = user
    configs['Password'] = passw
    configs['Host'] = smtp_host
    configs['Port'] = smtp_port
    write_json_configs()
    read_json_configs()
    messagebox.showinfo("Cuenta conectada", "La cuenta ha sido vinculada con éxito. Recibió un email de diagnóstico a su casilla.")

def try_to_connect(user, password, host, port):
    try:
        if (host == "smtp.office365.com"):
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(host, port)
    except Exception as e:
        print(f"ERROR AL CONECTAR: {e}")
        return "ConnectionError"   
    
    try:
        server.login(user, password)
    except Exception as e:
        print(f"ERROR AL INICIAR SESIÓN: {e}")
        return "LoginError"
    
    try:
        msg = MIMEMultipart('related')
        msg["Subject"] = "CRICKET - Conexión exitosa! ✅"
        msg["From"] = user
        msg["To"] = user
        html_test = f"""
            <html>
            <body style="background: #000d21;color: #fff;">
                <div style="margin: 25px;"><br>
                    <center><img src="cid:bannerimg" width=535 height=230></center>
                    <h1>Bienvenido a cricket, {user}</h1>
                    <p style="font-size: 12px;">Su cuenta ha sido vinculada con éxito a cricket. Este correo confirma que su configuración de envío ha sido establecida correctamente y que los mensajes están saliendo sin inconvenientes desde nuestro sistema. Cricket es más que un simple gestor de correos: es una herramienta pensada para brindarle eficiencia, control y estilo a sus comunicaciones. Ya sea que envíe correos individuales o campañas completas, Cricket está optimizado para que el proceso sea rápido, visualmente atractivo y sin complicaciones. Le agradecemos por confiar en nosotros. ¡Estamos comprometidos en brindarle la mejor experiencia posible!<br>Si tiene sugerencias, ideas o necesita soporte, no dude en contactarnos.</p>
                    <p style="font-size: 20px;"><b>Atentamente, el equipo de desarrollo.</b></p>
                    <a href="https://github.com/gr1ll0o/cricket">GitHub</a><br><br>
                </div>
            </body>
            </html>
        """
        msg.attach(MIMEText(html_test, 'html'))

        banner_path = get_resource_path('assets/banner.png')
        with open(banner_path, 'rb') as f:
            img_banner = MIMEImage(f.read())
        img_banner.add_header('Content-ID', f'<bannerimg>')
        img_banner.add_header('Content-Disposition', 'inline', filename=banner_path)
        msg.attach(img_banner)

        server.sendmail(user, user, msg.as_string())
        server.quit()
        return "ENVÍO EXITOSO"
    except Exception as e:
        print(f"ERROR AL ENVIAR CORREO: {e}")
        return "SendEmailError"

def get_install_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def signatures():
    global signature_path
    print(configs['Signature'])
    print(signature_path)
    install_dir = get_install_dir()
    signature_path = configs.get('Signature', "")

    if not signature_path or not os.path.isfile(signature_path):
        try:
            q = messagebox.askyesno("Firmas", "No tenes ninguna firma registrada, ¿Queres regristrar una?")
            if q: origin_path = filedialog.askopenfilename(title="Seleccioná un archivo", filetypes=[('Archivos JPG', '*.jpg')])
            else: return
            if origin_path:
                dest_path = os.path.join(install_dir, "signature.jpg")
                shutil.copy(origin_path, dest_path)
            else: return
        except: messagebox.showerror("Error", "Ha ocurrido un error al abrir el archivo");return
        configs['Signature'] = dest_path
        write_json_configs()
        read_json_configs()
        messagebox.showinfo("Firmas", "Se ha registrado su firma con éxito. Será añadida al final de un mensaje a partir de ahora")    
    else:
        c = messagebox.askokcancel("Firmas", f"Firma registrada:\n{configs['Signature']}\n\nPresione Cancelar para eliminarla")
        if (not c): 
            configs['Signature'] = ''
            os.remove(signature_path)
            write_json_configs()
            read_json_configs()
            messagebox.showinfo("Firmas", "Se ha eliminado la firma registrada")

def show_send_menu(event):
    if (onsending == True): return
    send_menu.post(event.x_root, event.y_root)

def attach_img():
    global msg, len_imgs, attachments
    file_path = filedialog.askopenfilename(title="Seleccionar archivo para adjuntar", filetypes=[("Imagenes", "*.png;*.jpg;*.jpeg;"), ("Archivos adjuntables", "*.pdf;*.xlsx;*.docx;*.doc;*.xls;*.csv")])
    if file_path:
        try:
            ext = os.path.splitext(file_path)[1].lower()

            if (ext in ['.png', '.jpg', '.jpeg']):
                len_imgs += 1
                imgs.append((file_path, f'imagen{len_imgs}'))
                body_text.insert(tk.END, f'\n<img src="cid:imagen{len_imgs}">')
            elif (ext in ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.csv']):
                attachments.append(file_path)
                messagebox.showinfo("Archivo adjuntado", f"Se adjuntó el archivo correctamente (Actualmente {len(attachments)} PDFs adjuntos)")
            else:
                messagebox.showwarning("Archivo soportado", "El archivo seleccionado no es compatible")
        except Exception as e: 
            messagebox.showerror("Error", f"Hubo un error al adjuntar la imagen ({e})");return

# /// [SEND EMAILS]
def send_emails(ids=False):
    global imgs, len_imgs, onsending, alls, data, attachments, body_text
    transmitter = user
    if not ids: 
        selected_list = listbox.get(listbox.curselection())
        key = selected_list.split(" (")[0]
        emails_destiny = data[key]
    else: emails_destiny = alls
    title_msg = subject_text.get("1.0", tk.END)
    body_msg = body_text.get("1.0", tk.END)

    try:
        log("> Secuencia de Envío Iniciada")
        root.after(3000, log(f"Iniciando sesión en {transmitter}..."))
        if smtp_host in "smtp.office365.com":
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.ehlo()
            server.starttls()
            server.ehlo()
        else: server = smtplib.SMTP_SSL(smtp_host, smtp_port)  #SSL
        server.login(transmitter, passw) # Iniciar sesión
        log("Iniciando envíos...\n")
        i=1
        for recipient in emails_destiny:
            try:
                msg = MIMEMultipart('related')
                msg['Subject'] = title_msg
                msg['From'] = transmitter
                msg['To'] = recipient
                if (signature_path == ""):
                    html = f"""
                    <html>
                    <body>
                        <p style="font-family: {font}">{body_msg.replace('\n', '<br>')}</p>
                    </body>
                    </html>
                    """
                    print("FIRMA NO REGISTRADA")
                else:
                    html = f"""
                    <html>
                    <body>
                        <p style="font-family: {font}">{body_msg.replace('\n', '<br>')}</p><br>
                        <img src="cid:firma_img" width="450" height="120">
                    </body>
                    </html>
                    """
                    print(f"FIRMA REGISTRADA: {signature_path}")
                msg.attach(MIMEText(html, 'html'))
                body_all = body_msg + subject_text.get("1.0", tk.END)
                imgs = [pair for pair in imgs if f'cid:{pair[1]}' in body_all]
                if len(imgs) == 0: len_imgs = 0
                print(attachments)
                if (attachments != []):
                    for path in attachments:
                        with open(path, 'rb') as f:
                            part = MIMEApplication(f.read(), _subtype="pdf")
                            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(path))
                            msg.attach(part)
                if (imgs != []):
                    for path, cid in imgs:
                        with open(path, 'rb') as f:
                            img = MIMEImage(f.read())
                            img.add_header('Content-ID', f'<{cid}>')
                            msg.attach(img)
                        print(cid)
                if (signature_path != ""):
                    print("Insertando firma...")
                    with open(signature_path, 'rb') as f:
                        img = MIMEImage(f.read())
                        img.add_header('Content-ID', f'<firma_img>')
                        img.add_header('Content-Disposition', 'inline', filename=os.path.basename(signature_path))
                        msg.attach(img)

                server.sendmail(transmitter, recipient, msg.as_string())
                log(f"Enviando mail a {recipient} ({i}/{len(emails_destiny)})")
                i+=1
            except Exception as e:
                messagebox.showerror("Error", f"Error al enviar email a {recipient}: {e}")
                log(f"ERROR: Eliminando automaticamente {recipient}")
                # print(f"Error al enviar el correo {e}.")
                for list in data:
                    if (recipient in data[list]):
                        data[list].remove(recipient)
                write_json_lists()
                read_json_lists()
            
        server.quit()
        log("", False)
        log(f"{i-1} de {len(emails_destiny)} emails enviados con éxito.")
        
        imgs = []
        len_imgs = 0
        attachments = []
        body_text.delete("1.0", tk.END)
        messagebox.showinfo("Emails enviados", "Se han enviado todos los emails")
        print("Correo enviado con éxito!")
    except Exception as e:
        messagebox.showerror("Error", f"Error al iniciar secuencia de emails: {e}")
        log(f"ERROR: {e}")
        print(f"Error al enviar el correo: {e}")
    
    addlist_btn.config(state=tk.NORMAL)
    dellist_btn.config(state=tk.NORMAL)
    import_btn.config(state=tk.NORMAL)
    send_btn.config(state=tk.NORMAL)
    onsending = False

# /// [SEND EMAIL]
def send_email(mail):
    global msg, imgs, len_imgs, onsending, attachments, body_text
    transmitter = user
    print(transmitter)
    email_destiny = mail
    title_msg = subject_text.get("1.0", tk.END).strip()
    body_msg = body_text.get("1.0", tk.END).strip()

    try:
        log("> Secuencia de Envío Iniciada")
        root.after(3000, log(f"Iniciando sesión en {transmitter}..."))
        if smtp_host in "smtp.office365.com":
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.ehlo()
            server.starttls()
            server.ehlo()
        else: server = smtplib.SMTP_SSL(smtp_host, smtp_port)  #SSL
        server.login(transmitter, passw) # Iniciar sesión
        log("Iniciando envíos...\n")

        msg = MIMEMultipart('related')
        msg['Subject'] = title_msg
        msg['From'] = transmitter
        msg['To'] = email_destiny
        if (signature_path == ""):
            html = f"""
            <html>
            <body>
                <p style="font-family: {font}">{body_msg.replace('\n', '<br>')}</p>
            </body>
            </html>
            """
            print("FIRMA NO REGISTRADA")
        else:
            html = f"""
            <html>
            <body>
                <p style="font-family: {font}">{body_msg.replace('\n', '<br>')}</p><br>
                <img src="cid:firma_img" width="450" height="120">
            </body>
            </html>
            """
            print(f"FIRMA REGISTRADA: {signature_path}")
        msg.attach(MIMEText(html, 'html'))

        body_all = body_msg + subject_text.get("1.0", tk.END)
        imgs = [pair for pair in imgs if f'cid:{pair[1]}' in body_all]
        if len(imgs) == 0: len_imgs = 0
        print(attachments)
        if (attachments != []):
            for path in attachments:
                with open(path, 'rb') as f:
                    part = MIMEApplication(f.read(), _subtype="pdf")
                    part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(path))
                    msg.attach(part)
        if (imgs != []):
            for path, cid in imgs:
                with open(path, 'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-ID', f'<{cid}>')
                    msg.attach(img)
                print(cid)
        if (signature_path != ""):
            print("Insertando firma...")
            with open(signature_path, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-ID', f'<firma_img>')
                img.add_header('Content-Disposition', 'inline', filename=os.path.basename(signature_path))
                msg.attach(img)

        
        server.sendmail(transmitter, mail, msg.as_string())
        log(f"Enviando mail a {mail}...")  
        server.quit()
        log("", False)
        log(f"Email a {mail} enviado con éxito.")
        body_text.delete("1.0", tk.END)
        messagebox.showinfo("Emails enviados", "Se han enviado todos los emails exitosamente.")
        imgs = []
        attachments = []
        print("Correo enviado con éxito!")
    except Exception as e:
        messagebox.showerror("Error", f"Error al enviar el email: {e}")
        log("ERROR: {e}")
        print(f"Error al enviar el correo: {e}")
    
    addlist_btn.config(state=tk.NORMAL)
    dellist_btn.config(state=tk.NORMAL)
    import_btn.config(state=tk.NORMAL)
    send_btn.config(state=tk.NORMAL)
    onsending = False

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
def send_identifiers():
    global alls
    try: 
        if (data == {}): messagebox.showwarning("No hay listas", "Debe poseer por lo menos 2 listas para enviar a toda la base de datos");return
    except: messagebox.showwarning("No hay listas", "Debe poseer por lo menos 2 listas para enviar a toda la base de datos");return
    i = simpledialog.askstring("Enviar a identificadores", "Introduce el identificador de listas")
    alls = []
    lists = ""
    for list in data:
        if i in list:
            lists += f"{list}\n"
            for mail in data[list]:
                alls.append(mail)
    print(alls)
    if (lists == ""): messagebox.showinfo("Sin resultados", f'No se encontraron listas con identificador "{i}"');return
    c = messagebox.askyesno("Confirmar envío", f'Se encontraron listas con el identificador "{i}":\n\n{lists}\nPresione "Sí" para confirmar')
    if (c): 
        if (subject_text.get("1.0", tk.END).strip() == "" or body_text.get("1.0", tk.END).strip() == ""): messagebox.showerror("Error", "Escribe un asunto y un mensaje.");return
        start_sending_emails(4)

def send_all_database():
    if (subject_text.get("1.0", tk.END).strip() == "" or body_text.get("1.0", tk.END).strip() == ""): messagebox.showerror("Error", "Escribe un asunto y un mensaje.");return
    if (data == {}): messagebox.showwarning("No hay listas", "Debe poseer por lo menos 2 listas para enviar a toda la base de datos");return
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
        new_emails=[]
        err=0
        for line in emails:
            if ("@" in line and "." in line):
                new_emails.append(line)
                print("VALIDO")
            else: 
                print("NO VALIDO");err+=1
        json_global[name] = new_emails
        try: update_display_emails(name);write_json_lists();read_json_lists()
        except: messagebox.showerror("Error", "Ha ocurrido un error al actualizar la lista de emails");return
        print(f"MAILS: {len(new_emails)}, ERROR: {err}")
        messagebox.showinfo("Importación", f"Se han importado {len(emails)-err} de {len(emails)} mails a {name}")

def log(msg, showtime=True):
    console_text.config(state=tk.NORMAL)
    if(showtime): console_text.insert(tk.END, "<" + time.strftime("%H:%M") + "> " + msg + "\n")
    else: console_text.insert(tk.END, msg + "\n")
    console_text.see(tk.END) 
    console_text.config(state=tk.DISABLED)

def del_email():
    selected_list = listbox.get(listbox.curselection())
    key = selected_list.split(" (")[0]
    try: 
        mail = simpledialog.askstring("Eliminar mail", f'Introduzca el mail de la lista "{key}" a eliminar.', parent=root)
        if (mail in json_global[key]):
            json_global[key].remove(mail)
            write_json_lists()
            update_display_emails(key)
            read_json_lists()
            messagebox.showinfo("Email eliminado", f'Se ha eliminado el mail "{mail}" de la lista "{key}" con éxito')    
        else:
            messagebox.showwarning("Email no encontrado", f'No existe "{mail}" en "{key}"')
    except Exception as e: messagebox.showwarning("ERROR", f'Se produjo un error: {e}')
        
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
    try: update_display_emails(key);write_json_lists();read_json_lists()
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
                i=0;err=0
                for line in new_emails:
                    if ("@" in line and "." in line): 
                        json_global[key].append(new_emails[i])
                        print("VALIDO")
                    else: 
                        print("NO VALIDO");err+=1
                    i+=1
                try: update_display_emails(key);write_json_lists();read_json_lists()
                except: messagebox.showerror("Error", "Ha ocurrido un error al actualizar la lista de emails");return
                messagebox.showinfo("Importación", f"Se han importado {len(new_emails)-err} de {len(new_emails)} mails a {key}")
        elif c == False: 
            print(json_global)
            name = simpledialog.askstring("Crear lista de importación", "Ingrese el nombre de la nueva lista", parent=root)
            if name == None: return
            if len(name) > 20: messagebox.showwarning("Error", "Máximo 20 caracteres permitidos.");return
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
        if len(name) > 20: messagebox.showwarning("Error", "Máximo 20 caracteres permitidos.");return
        if name == '': messagebox.showinfo("Nombre inválido", "Debes añadir un nombre a la lista");return
        if (json_global != {}):
            for list in lists:
                if (name == list):
                    messagebox.showerror("Lista duplicada", "Ya existe una lista con este nombre");return
        if (not name): return
        add_list_imports(name)

# /// [START SENDING EMAILS]
def start_sending_emails(mode=1, mail_from_mode_2=None):
    global onsending, alls
    if (user == "" or passw == ""): messagebox.showerror("Error", "No hay ninguna cuenta de correo electrónico vinculada al programa. Vinculela haciendo click derecho en el logo.");return
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
        print(data)
        for list in data:
            for mail in data[list]:
                all.append(mail)
        print(all)
        print(f"ENVIO A TODA LA BASE")
        print(f'ASUNTO: {subject_text.get("1.0", tk.END)}')
        print(f'MENSAJE: {body_text.get("1.0", tk.END)}')
        threading.Thread(target=send_all_emails, args=(all,)).start()
    elif mode == 4: # ID's
        print(alls)
        print(f"ENVIO A IDENTIFICADORES")
        print(f'ASUNTO: {subject_text.get("1.0", tk.END)}')
        print(f'MENSAJE: {body_text.get("1.0", tk.END)}')
        print(f'DESTINATARIOS: {alls}')
        threading.Thread(target=send_emails, args=(True,)).start()
    else: # Error
        raise Exception("Modo no válido")

    onsending = True
    addlist_btn.config(state=tk.DISABLED)
    dellist_btn.config(state=tk.DISABLED)
    import_btn.config(state=tk.DISABLED)
    send_btn.config(state=tk.DISABLED)

# /// [SEND ALL EMAILS]
def send_all_emails(list):
    global imgs, len_imgs, onsending, attachments, body_text
    transmitter = user
    emails_destiny = list
    title_msg = subject_text.get("1.0", tk.END)
    body_msg = body_text.get("1.0", tk.END)

    try:
        log("Secuencia de envío iniciada")
        root.after(3000, log(f"Iniciando sesión en {transmitter}..."))
        if smtp_host in "smtp.office365.com":
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.ehlo()
            server.starttls()
            server.ehlo()
        else: server = smtplib.SMTP_SSL(smtp_host, smtp_port)  #SSL
        server.login(transmitter, passw) # Iniciar sesión
        log("Iniciando envíos...\n")
        i=1
        for recipient in emails_destiny:
            try:
                msg = MIMEMultipart('related') # CUERPO/MENSAJE
                msg['Subject'] = title_msg # ASUNTO
                msg['From'] = transmitter # EMISOR
                msg['To'] = recipient #RECEPTOR
                if (signature_path == ""):
                    html = f"""
                    <html>
                    <body>
                        <p style="font-family: {font}">{body_msg.replace('\n', '<br>')}</p>
                    </body>
                    </html>
                    """
                    print("FIRMA NO REGISTRADA")
                else:
                    html = f"""
                    <html>
                    <body>
                        <p style="font-family: {font}">{body_msg.replace('\n', '<br>')}</p><br>
                        <img src="cid:firma_img" width="450" height="120">
                    </body>
                    </html>
                    """
                    print(f"FIRMA REGISTRADA: {signature_path}")
                msg.attach(MIMEText(html, 'html'))
                body_all = body_msg + subject_text.get("1.0", tk.END)
                imgs = [pair for pair in imgs if f'cid:{pair[1]}' in body_all]
                if len(imgs) == 0: len_imgs = 0
                print(attachments)
                if (attachments != []):
                    for path in attachments:
                        with open(path, 'rb') as f:
                            part = MIMEApplication(f.read(), _subtype="pdf")
                            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(path))
                            msg.attach(part)
                if (imgs != []):
                    for path, cid in imgs:
                        with open(path, 'rb') as f:
                            img = MIMEImage(f.read())
                            img.add_header('Content-ID', f'<{cid}>')
                            msg.attach(img)
                        print(cid)
                if (signature_path != ""):
                    print("Insertando firma...")
                    with open(signature_path, 'rb') as f:
                        img = MIMEImage(f.read())
                        img.add_header('Content-ID', f'<firma_img>')
                        img.add_header('Content-Disposition', 'inline', filename=os.path.basename(signature_path))
                        msg.attach(img)

                server.sendmail(transmitter, recipient, msg.as_string())
                log(f"Enviando mail a {recipient} ({i}/{len(emails_destiny)})")
                i+=1
            except Exception as e:
                messagebox.showerror("Error", f"Error al enviar email a {recipient}: {e}")
                log(f"ERROR: Eliminando automaticamente {recipient}")
                # print(f"Error al enviar el correo {e}.")
                for list in data:
                    if (recipient in data[list]):
                        data[list].remove(recipient)
                write_json_lists()
                read_json_lists()
            
        server.quit()
        log("", False)
        log(f"{i-1} de {len(emails_destiny)} emails enviados con éxito.")
        attachments = []
        imgs = []
        len_imgs = 0
        body_text.delete("1.0", tk.END)
        messagebox.showinfo("Emails enviados", "Se han enviado todos los emails.")
        print("Correo enviado con éxito!")
    except Exception as e:
        messagebox.showerror("Error", f"Error al enviar a {recipient}: {e}")
        log(f"ERROR: {e}")
        print(f"Error al enviar el correo: {e}")

    addlist_btn.config(state=tk.NORMAL)
    dellist_btn.config(state=tk.NORMAL)
    import_btn.config(state=tk.NORMAL)
    send_btn.config(state=tk.NORMAL)
    onsending = False

def on_click_list(event):
    try:
        widget = event.widget
        selection = widget.curselection()
        if selection: selected_item = widget.get(selection[0])
        list_selected = selected_item
        email_selected_label.configure(text=f'Enviar a {list_selected}')
        update_display_emails(selected_item)
        if (listbox.size() == 0): list_emails_label.config(text="")
    except:
        update_display_emails("")
        if (listbox.size() == 0): list_emails_label.config(text="")

def update_display_emails(selected_item=list_selected):
    global after, user, passw
    t=""
    key = selected_item.split(" (")[0]
    list_emails_label.config(text=f"{key}")
    try:
        for mail in data[key]:
            t += f'{mail}\n'
        emails_display.config(state=tk.NORMAL)
        emails_display.delete('1.0', tk.END)
        emails_display.insert(tk.END, t)
        emails_display.config(state=tk.NORMAL)
        after = key
    except:
        list_emails_label.config(text=f"E-mails de {after}")

def read_json_configs():
    global configs, signature_path, user, passw, smtp_host, smtp_port
    try:
        with open(CONFIGDIR, 'r') as file:
            cdata = json.load(file)
            configs = cdata
            signature_path = configs['Signature']
            user = configs['Email']
            passw = configs['Password']
            smtp_host = configs['Host']
            smtp_port = configs['Port']
    except:
        configs = {'Email': '', 'Password': '', 'Host': 0, 'Port': '', 'Signature': ''} 
        with open(CONFIGDIR, 'w') as file:
            json.dump(configs, file, ensure_ascii=False, indent=4)
    if (user == ""): title.config(text="cricket  - ❗")
    else: title.config(text=f"cricket - {user}")

def write_json_configs():
    global configs
    with open(CONFIGDIR, 'w') as file:
        json.dump(configs, file, ensure_ascii=False, indent=4)

def read_json_lists():
    global listbox, json_global, data, lists_mails, lists
    try:
        with open(DATADIR, 'r') as file:
            data = json.load(file)
            json_global = data
            lists = list(data.keys()) # LISTAS
            lists_mails = list(data.values()) # MAILS DE LAS LISTAS

        listbox.delete(0, tk.END)
        for lista in lists:
            listbox.insert(tk.END, f'{lista} ({len(data[lista])})')
    except:
        with open(DATADIR, 'w') as file:
            file.write('')
        json_global = {}
    list_selected = listbox.get(tk.END).split(" (")[0]

def write_json_lists():
    global json_global
    with open(DATADIR, 'w') as file:
        json.dump(json_global, file, ensure_ascii=False, indent=4)

def add_list():
    global erased
    erased = ""
    name = simpledialog.askstring("Crear lista", "Ingrese el nombre de la nueva lista", parent=root)
    if len(name) > 20: messagebox.showwarning("Error", "Máximo 20 caracteres permitidos.");return
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

    write_json_lists()
    read_json_lists()
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
            write_json_lists()
            read_json_lists()
            messagebox.showinfo("Lista eliminada", f"Se eliminó la lista {selected_list}")
            emails_display.config(text="")
            email_selected_label.config(text="")
            list_emails_label.config(text="")
        else: pass
    except:
        emails_display.delete("1.0", tk.END)
        email_selected_label.config(text="")
        list_emails_label.config(text="")

def change_font():
    global font
    f = simpledialog.askinteger("Cambiar fuente", "Fuentes disponibles:\n1. Arial\n2. Times New Roman\n\nEscriba el número de la fuente deseada")
    if (f):
        match int(f):
            case 1:
                font = "Arial"
                messagebox.showinfo("Fuente cambiada", "Ahora la fuente es Arial.")
            case 2: 
                font = "Times New Roman"
                messagebox.showinfo("Fuente cambiada", "Ahora la fuente es Times New Roman.")
            case _:
                messagebox.showerror("Error", "Número inválido")
    print(font)
    body_text.config(font=(font, 13))

def style_text(mode):
    if (mode == "bold"):
        body_text.insert(tk.END, "<b></b>")
        body_text.mark_set("insert", f"{body_text.index('insert')} -4c")
    elif (mode == "italic"):
        body_text.insert(tk.END, "<i></i>")
        body_text.mark_set("insert", f"{body_text.index('insert')} -4c")
    else: return
    body_text.focus()

def start_move(event): root.x = event.x; root.y = event.y

def do_move(event):
    x = event.x_root - root.x
    y = event.y_root - root.y
    root.geometry(f'+{x}+{y}')

def refresh():
    read_json_configs()
    read_json_lists()

def on_leave(event):
    global console_text
    if (onsending): print("SE ESTÁ ENVIANDO UN MENSAJE");return
    addlist_btn.config(bg="#061E44")
    dellist_btn.config(bg="#061E44")
    import_btn.config(bg="#061E44")
    send_btn.config(bg="#061E44")
    console_text.config(state="normal")
    console_text.delete("1.0", tk.END)
    console_text.config(state="disabled")

def close_window(): root.destroy()

#! SETUP ###################################
title_bar = tk.Frame(root, bg="#000d21", relief='raised', bd=0, height=30)
title_bar.pack(fill=tk.X)
img = img.resize((50, 50), Image.LANCZOS).convert("RGBA")  # opcional, ajustar tamaño
photo = ImageTk.PhotoImage(img)
logo_img = tk.Label(title_bar, image=photo, bg="#000d21")
logo_img.place(x=7)
logo_img.bind('<Button-3>', show_settings_menu)
logo_img.bind("<Enter>", lambda e: (log("Presione CLICK DERECHO para gestionar su cuenta y otras preferencias.", False)) if not onsending else None)
logo_img.bind("<Leave>", lambda e: (on_leave(e)) if not onsending else None)
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
#!############################################

#! ELEMENTS !#################################
list_label = tk.Label(main_content, bg="#001536", fg="#fff", text="Listas de e-mails", font=('Arial', 16, "bold"))
list_label.place(x=15, y=10)

listbox = tk.Listbox(main_content, border=0)
listbox.config(font=('Arial', 16),background="#061E44", foreground="#fff", bd=0)
listbox.place(x=20, y=40, width=300, height=428)
listbox.bind("<<ListboxSelect>>", on_click_list)

addlist_btn = tk.Button(main_content, cursor="hand2", activebackground="#011330", activeforeground="#fff", text="Añadir", command=add_list, font=('Arial', 17), bg="#061E44", fg="#fff", bd=0)
addlist_btn.place(x=20, y=480)
addlist_btn.bind('<Button-3>', show_import_menu)
addlist_btn.bind('<Enter>', lambda e: (addlist_btn.config(bg="#012965"), log("Añada un email manualmente presionando CLICK DERECHO", False)) if not onsending else None)
addlist_btn.bind('<Leave>', lambda e: on_leave(e))

dellist_btn = tk.Button(main_content, cursor="hand2", activebackground="#011330", activeforeground="#fff", command=del_list,text="Eliminar", font=('Arial', 17), bg="#061E44", fg="#fff", bd=0)
dellist_btn.place(x=113, y=480)
dellist_btn.bind('<Button-3>', show_del_menu)
dellist_btn.bind('<Enter>', lambda e: (dellist_btn.config(bg="#012965"), log("Elimine un email de la lista presionando CLICK DERECHO", False)) if not onsending else None)
dellist_btn.bind('<Leave>', lambda e: on_leave(e))

import_btn = tk.Button(main_content, cursor="hand2", activebackground="#011330", activeforeground="#fff",command=import_file, text="Importar", font=('Arial', 17), bg="#061E44", fg="#fff", bd=0)
import_btn.place(x=220, y=480)
import_btn.bind('<Enter>', lambda e: import_btn.config(bg="#012965") if not onsending else None)
import_btn.bind('<Leave>', lambda e: on_leave(e))

list_emails_label = tk.Label(main_content, bg="#001536", fg="#fff", text="", font=('Arial', 15, "bold"))
list_emails_label.place(x=327, y=10)

emails_frame = tk.Frame(main_content, bg="#001536")
emails_frame.place(x=329, y=40, width=300, height=410)
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

body_text = tk.Text(main_content, padx=5, pady=5, wrap="word", font=('Arial', 13), bg="#082350", fg="#fff", bd=0, width=37, height=18)
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

bold_btn = tk.Button(main_content, cursor="hand2", command=lambda: style_text("bold"),  activebackground="#011330", activeforeground="#fff", text=" B ", font=('Arial', 17, "bold"), bg="#061E44", fg="#fff", bd=0)
bold_btn.place(x=876, y=400)
bold_btn.bind('<Enter>', lambda e: bold_btn.config(bg="#012965"))
bold_btn.bind('<Leave>', lambda e: bold_btn.config(bg="#061E44")) 

italic_btn = tk.Button(main_content, cursor="hand2", command=lambda: style_text("italic"), activebackground="#011330", activeforeground="#fff", text="  I  ", font=('Times', 17, "italic"), bg="#061E44", fg="#fff", bd=0)
italic_btn.place(x=820, y=400)
italic_btn.bind('<Enter>', lambda e: italic_btn.config(bg="#012965"))
italic_btn.bind('<Leave>', lambda e: italic_btn.config(bg="#061E44")) 

attach_btn = tk.Button(main_content, cursor="hand2", command=attach_img, activebackground="#011330", activeforeground="#fff", text="📎", font=('Arial', 18), bg="#061E44", fg="#fff", bd=0)
attach_btn.place(x=930, y=400)
attach_btn.bind('<Enter>', lambda e: attach_btn.config(bg="#012965"))
attach_btn.bind('<Leave>', lambda e: attach_btn.config(bg="#061E44")) 

send_btn = tk.Button(main_content, cursor="hand2", command=start_sending_emails, activebackground="#011330", activeforeground="#fff", text="   Enviar   ", font=('Arial', 18), bg="#061E44", fg="#fff", bd=0)
send_btn.place(x=845, y=483)
send_btn.bind('<Button-3>', show_send_menu)
send_btn.bind('<Enter>', lambda e: (send_btn.config(bg="#012965"), log("Acceda a mas opciones de envío presionando CLICK DERECHO", False)) if not onsending else None)
send_btn.bind('<Leave>', lambda e: on_leave(e)) 
#!##################################################

#! MENUES !#########################################
settings_menu = tk.Menu(root, tearoff=0, bg="#001536", fg="#ffffff")
# settings_menu.add_command(label="Importar texto", command=lambda: print("EN DESARROLLO"))
settings_menu.add_command(label="Fuente de texto", command=change_font)
settings_menu.add_separator()
settings_menu.add_command(label="Firma...", command=signatures)
settings_menu.add_separator()
settings_menu.add_command(label="Administrar cuenta...", command=check_account)
settings_menu.add_command(label="Creditos...", command=show_credits)

dellist_menu = tk.Menu(root, tearoff=0, bg="#001536", fg="#ffffff")
dellist_menu.add_command(label="Eliminar un email", command=del_email)

addlist_menu = tk.Menu(root, tearoff=0, bg="#001536", fg="#ffffff")
addlist_menu.add_command(label="Añadir un email", command=add_email)

send_menu = tk.Menu(root, tearoff=0, bg="#001536", fg="#ffffff")
send_menu.add_command(label="Envío rápido", command=fast_send)
send_menu.add_command(label="Envío a todo identificador...", command=send_identifiers)
send_menu.add_command(label="Enviar a toda la base de datos", command=send_all_database)
#!##############################################

read_json_lists()
read_json_configs()

show_splash()

root.mainloop()