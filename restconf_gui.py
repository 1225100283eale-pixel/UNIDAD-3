import json
import tkinter as tk
from tkinter import ttk, messagebox

import requests

requests.packages.urllib3.disable_warnings()

BASE_URL = "https://10.10.20.48/restconf/data/ietf-interfaces:interfaces"

HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-type": "application/yang-data+json",
}


def actualizar_estado(mensaje, tipo="neutral"):
    colores = {
        "success": ("#166534", "white"),
        "error": ("#b91c1c", "white"),
        "neutral": ("#e5e7eb", "#111827"),
    }
    fondo, texto = colores.get(tipo, colores["neutral"])
    status_bar.config(
        text=f"Estado: {mensaje}",
        bg=fondo,
        fg=texto,
    )


def consultar_interfaz():
    nombre = interfaz_entry.get().strip()
    usuario = usuario_entry.get().strip()
    password = password_entry.get()

    resultado.delete("1.0", tk.END)

    if not nombre or not usuario or not password:
        mensaje = "Completa interfaz, usuario y contraseña."
        resultado.insert(tk.END, mensaje)
        actualizar_estado(mensaje, "error")
        return

    url = f"{BASE_URL}/interface={nombre}"
    actualizar_estado(f"Consultando {nombre}...", "neutral")

    try:
        respuesta = requests.get(
            url,
            auth=(usuario, password),
            headers=HEADERS,
            verify=False,
            timeout=15,
        )

        if respuesta.status_code == 200:
            datos = respuesta.json()
            interfaz = datos.get("ietf-interfaces:interface", datos)

            if isinstance(interfaz, list):
                interfaz = next(
                    (
                        item
                        for item in interfaz
                        if item.get("name") == nombre
                    ),
                    {},
                )

            if not isinstance(interfaz, dict) or not interfaz:
                mensaje = f"No se encontró la interfaz {nombre}."
                resultado.insert(tk.END, mensaje)
                actualizar_estado(mensaje, "error")
                return

            direcciones = (
                interfaz.get("ietf-ip:ipv4", {})
                .get("address", [])
            )

            if direcciones:
                ip = direcciones[0].get("ip", "No disponible")
                mascara = direcciones[0].get("netmask", "No disponible")
            else:
                ip = "Sin dirección IPv4 configurada"
                mascara = "No disponible"

            if interfaz.get("enabled") is True:
                estado = "Habilitada"
            elif interfaz.get("enabled") is False:
                estado = "Deshabilitada"
            else:
                estado = "No disponible"

            resultado.insert(
                tk.END,
                f"Nombre: {interfaz.get('name', nombre)}\n"
                f"Descripción: "
                f"{interfaz.get('description', 'Sin descripción')}\n"
                f"Dirección IP: {ip}\n"
                f"Máscara: {mascara}\n"
                f"Estado administrativo: {estado}\n"
                f"Código HTTP: {respuesta.status_code}",
            )
            actualizar_estado(
                f"Operación exitosa (HTTP {respuesta.status_code})",
                "success",
            )
        else:
            detalle = (
                f"Error HTTP {respuesta.status_code}\n"
                f"{respuesta.text}"
            )
            resultado.insert(tk.END, detalle)
            actualizar_estado(
                f"Error HTTP {respuesta.status_code}",
                "error",
            )

    except requests.RequestException as error:
        mensaje = f"Error de conexión: {error}"
        resultado.insert(tk.END, mensaje)
        actualizar_estado(mensaje, "error")


def crear_actualizar_interfaz():
    nombre = nombre_form_entry.get().strip()
    ip = ip_entry.get().strip()
    mascara = mascara_entry.get().strip()
    descripcion = descripcion_entry.get().strip()
    usuario = usuario_entry.get().strip()
    password = password_entry.get()

    if not all((nombre, ip, mascara, descripcion, usuario, password)):
        mensaje = "Completa todos los campos y los datos de acceso."
        resultado.delete("1.0", tk.END)
        resultado.insert(tk.END, mensaje)
        actualizar_estado(mensaje, "error")
        return

    yangConfig = {
        "ietf-interfaces:interface": {
            "name": nombre,
            "description": descripcion,
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
            "ietf-ip:ipv4": {
                "address": [
                    {
                        "ip": ip,
                        "netmask": mascara,
                    }
                ]
            },
            "ietf-ip:ipv6": {},
        }
    }

    url = f"{BASE_URL}/interface={nombre}"
    actualizar_estado(f"Creando o actualizando {nombre}...", "neutral")

    try:
        respuesta = requests.put(
            url,
            data=json.dumps(yangConfig),
            auth=(usuario, password),
            headers=HEADERS,
            verify=False,
            timeout=15,
        )

        resultado.delete("1.0", tk.END)

        if 200 <= respuesta.status_code <= 299:
            mensaje = (
                f"{nombre} creada o actualizada "
                f"(HTTP {respuesta.status_code})."
            )
            resultado.insert(tk.END, mensaje)
            actualizar_estado(
                f"Operación exitosa (HTTP {respuesta.status_code})",
                "success",
            )
            messagebox.showinfo("Operación exitosa", mensaje)
        else:
            detalle = (
                f"Error HTTP {respuesta.status_code}\n"
                f"{respuesta.text}"
            )
            resultado.insert(tk.END, detalle)
            actualizar_estado(
                f"Error HTTP {respuesta.status_code}",
                "error",
            )
            messagebox.showerror("Error RESTCONF", detalle)

    except requests.RequestException as error:
        mensaje = f"Error de conexión: {error}"
        resultado.delete("1.0", tk.END)
        resultado.insert(tk.END, mensaje)
        actualizar_estado(mensaje, "error")
        messagebox.showerror("Error de conexión", mensaje)


def eliminar_interfaz():
    nombre = eliminar_entry.get().strip()
    usuario = usuario_entry.get().strip()
    password = password_entry.get()

    if not nombre or not usuario or not password:
        mensaje = "Completa interfaz y datos de acceso."
        resultado.delete("1.0", tk.END)
        resultado.insert(tk.END, mensaje)
        actualizar_estado(mensaje, "error")
        return

    confirmar = messagebox.askyesno(
        "Confirmar eliminación",
        f"¿Seguro que deseas eliminar la interfaz {nombre}?",
    )

    if not confirmar:
        mensaje = f"Eliminación de {nombre} cancelada."
        resultado.delete("1.0", tk.END)
        resultado.insert(tk.END, mensaje)
        actualizar_estado(mensaje, "neutral")
        return

    url = f"{BASE_URL}/interface={nombre}"
    actualizar_estado(f"Eliminando {nombre}...", "neutral")

    try:
        respuesta = requests.delete(
            url,
            auth=(usuario, password),
            headers=HEADERS,
            verify=False,
            timeout=15,
        )

        resultado.delete("1.0", tk.END)

        if 200 <= respuesta.status_code <= 299:
            mensaje = (
                f"{nombre} eliminada correctamente "
                f"(HTTP {respuesta.status_code})."
            )
            resultado.insert(tk.END, mensaje)
            actualizar_estado(
                f"Operación exitosa (HTTP {respuesta.status_code})",
                "success",
            )
            messagebox.showinfo("Operación exitosa", mensaje)
        else:
            detalle = (
                f"Error HTTP {respuesta.status_code}\n"
                f"{respuesta.text}"
            )
            resultado.insert(tk.END, detalle)
            actualizar_estado(
                f"Error HTTP {respuesta.status_code}",
                "error",
            )
            messagebox.showerror("Error RESTCONF", detalle)

    except requests.RequestException as error:
        mensaje = f"Error de conexión: {error}"
        resultado.delete("1.0", tk.END)
        resultado.insert(tk.END, mensaje)
        actualizar_estado(mensaje, "error")
        messagebox.showerror("Error de conexión", mensaje)


ventana = tk.Tk()
ventana.title("Cliente RESTCONF - Interfaces")
ventana.geometry("780x850")
ventana.columnconfigure(0, weight=1)
ventana.rowconfigure(0, weight=1)

marco = ttk.Frame(ventana, padding=14)
marco.grid(row=0, column=0, sticky="nsew")
marco.columnconfigure(0, weight=1)
marco.rowconfigure(5, weight=1)

ttk.Label(
    marco,
    text="Cliente RESTCONF con Tkinter",
    font=("Segoe UI", 14, "bold"),
).grid(row=0, column=0, sticky="w", pady=(0, 10))

acceso = ttk.LabelFrame(marco, text="Acceso al router", padding=10)
acceso.grid(row=1, column=0, sticky="ew", pady=(0, 8))
acceso.columnconfigure(1, weight=1)

ttk.Label(acceso, text="Usuario:").grid(
    row=0, column=0, sticky="w", padx=(0, 8), pady=4
)
usuario_entry = ttk.Entry(acceso)
usuario_entry.grid(row=0, column=1, sticky="ew", pady=4)
usuario_entry.insert(0, "developer")

ttk.Label(acceso, text="Contraseña:").grid(
    row=1, column=0, sticky="w", padx=(0, 8), pady=4
)
password_entry = ttk.Entry(acceso, show="*")
password_entry.grid(row=1, column=1, sticky="ew", pady=4)

consulta = ttk.LabelFrame(marco, text="Consultar interfaz (GET)", padding=10)
consulta.grid(row=2, column=0, sticky="ew", pady=8)
consulta.columnconfigure(1, weight=1)

ttk.Label(consulta, text="Interfaz:").grid(
    row=0, column=0, sticky="w", padx=(0, 8), pady=4
)
interfaz_entry = ttk.Entry(consulta)
interfaz_entry.grid(row=0, column=1, sticky="ew", pady=4)
interfaz_entry.insert(0, "GigabitEthernet1")

ttk.Button(
    consulta,
    text="Consultar Interfaz",
    command=consultar_interfaz,
).grid(row=0, column=2, padx=(8, 0), pady=4)

formulario = ttk.LabelFrame(
    marco,
    text="Crear/actualizar interfaz (PUT)",
    padding=10,
)
formulario.grid(row=3, column=0, sticky="ew", pady=8)
formulario.columnconfigure(1, weight=1)

ttk.Label(formulario, text="Nombre de interfaz:").grid(
    row=0, column=0, sticky="w", padx=(0, 8), pady=4
)
nombre_form_entry = ttk.Entry(formulario)
nombre_form_entry.grid(row=0, column=1, sticky="ew", pady=4)
nombre_form_entry.insert(0, "Loopback99")

ttk.Label(formulario, text="Dirección IP:").grid(
    row=1, column=0, sticky="w", padx=(0, 8), pady=4
)
ip_entry = ttk.Entry(formulario)
ip_entry.grid(row=1, column=1, sticky="ew", pady=4)
ip_entry.insert(0, "99.99.99.99")

ttk.Label(formulario, text="Máscara:").grid(
    row=2, column=0, sticky="w", padx=(0, 8), pady=4
)
mascara_entry = ttk.Entry(formulario)
mascara_entry.grid(row=2, column=1, sticky="ew", pady=4)
mascara_entry.insert(0, "255.255.255.0")

ttk.Label(formulario, text="Descripción:").grid(
    row=3, column=0, sticky="w", padx=(0, 8), pady=4
)
descripcion_entry = ttk.Entry(formulario)
descripcion_entry.grid(row=3, column=1, sticky="ew", pady=4)
descripcion_entry.insert(0, "WHATEVER99")

ttk.Button(
    formulario,
    text="Crear/Actualizar Interfaz",
    command=crear_actualizar_interfaz,
).grid(row=4, column=0, columnspan=2, pady=(8, 2))

eliminacion = ttk.LabelFrame(
    marco,
    text="Eliminar interfaz (DELETE)",
    padding=10,
)
eliminacion.grid(row=4, column=0, sticky="ew", pady=8)
eliminacion.columnconfigure(1, weight=1)

ttk.Label(eliminacion, text="Nombre de interfaz:").grid(
    row=0, column=0, sticky="w", padx=(0, 8), pady=4
)
eliminar_entry = ttk.Entry(eliminacion)
eliminar_entry.grid(row=0, column=1, sticky="ew", pady=4)
eliminar_entry.insert(0, "Loopback99")

ttk.Button(
    eliminacion,
    text="Eliminar Interfaz",
    command=eliminar_interfaz,
).grid(row=0, column=2, padx=(8, 0), pady=4)

resultado = tk.Text(marco, height=9, wrap="word")
resultado.grid(row=5, column=0, sticky="nsew", pady=(8, 0))
resultado.insert(tk.END, "Los resultados de las operaciones aparecerán aquí.")

status_bar = tk.Label(
    marco,
    text="Estado: Listo",
    anchor="w",
    relief="sunken",
    bg="#e5e7eb",
    fg="#111827",
    padx=8,
    pady=6,
)
status_bar.grid(row=6, column=0, sticky="ew", pady=(8, 0))

ventana.mainloop()