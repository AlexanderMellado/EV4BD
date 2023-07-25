import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient
import json
from bson import ObjectId

# Conexión a la base de datos
client = MongoClient()
db = client.app_ejercicio

# Función para mostrar los campos de una colección en la interfaz gráfica
def mostrar_campos(coleccion, frame_campos):
    campos = db[coleccion].find_one()
    for clave in campos.keys():
        etiqueta = tk.Label(frame_campos, text=clave)
        etiqueta.pack(side=tk.LEFT)
        entrada = tk.Entry(frame_campos)
        entrada.pack(side=tk.LEFT)
        frame_campos.campos[clave] = entrada

# Función para obtener los valores ingresados en las entradas de texto
def obtener_valores(frame_campos):
    valores = {}
    for clave, entrada in frame_campos.campos.items():
        valores[clave] = entrada.get()
    return valores

# Función para insertar un documento en una colección
def insertar_documento(coleccion, frame_campos):
    datos = obtener_valores(frame_campos)
    try:
        datos['_id'] = str(ObjectId())  # Generar un ObjectId único para el campo _id y convertirlo a una cadena de caracteres
        datos_json = json.loads(json.dumps(datos, default=str))  # Convertir los datos a formato JSON, incluyendo el campo _id como cadena de caracteres
        db[coleccion].insert_one(datos_json)
        messagebox.showinfo("Éxito", "Documento insertado correctamente")
    except:
        messagebox.showerror("Error", "Los datos ingresados no son válidos")

# Función para actualizar un documento en una colección
def actualizar_documento(coleccion, filtro, nuevos_datos):
    nuevos_datos_json = {}
    for clave, valor in nuevos_datos.items():
        if clave != "_id":
            nuevos_datos_json[clave] = valor
    db[coleccion].update_one(filtro, {"$set": nuevos_datos_json})
    messagebox.showinfo("Éxito", "Documento actualizado correctamente")

# Función para eliminar un documento de una colección
def eliminar_documento(coleccion, frame_campos):
    filtro = {}
    for clave, entrada in frame_campos.campos.items():
        valor = entrada.get()
        if valor:
            filtro[clave] = valor
    db[coleccion].delete_one(filtro)
    messagebox.showinfo("Éxito", "Documento eliminado correctamente")

# Función para mostrar los documentos de una colección en un widget Text
def mostrar_documentos(coleccion, widget_text):
    documentos = db[coleccion].find()
    texto = ""
    for documento in documentos:
        for clave, valor in documento.items():
            texto += f"{clave}: {valor}\n"
        texto += "\n"
    widget_text.delete("1.0", tk.END)  # Limpiar el widget antes de mostrar los nuevos documentos
    widget_text.insert(tk.END, texto)

# Función para buscar el documento a actualizar y abrir una nueva ventana con los campos de texto para ingresar los nuevos datos
def buscar_documento_actualizar(coleccion, frame_campos):
    filtro = {}
    for clave, entrada in frame_campos.campos.items():
        valor = entrada.get()
        if valor and clave != "_id":
            filtro[clave] = valor
        elif clave == "_id" and ObjectId.is_valid(valor):
            filtro[clave] = ObjectId(valor)
    documento = db[coleccion].find_one(filtro)
    if documento:
        ventana_actualizar = tk.Toplevel()
        ventana_actualizar.title("Actualizar documento")
        ventana_actualizar.geometry("400x400")

        frame_campos_actualizar = tk.Frame(ventana_actualizar)
        frame_campos_actualizar.pack()

        frame_campos_actualizar.campos = {}
        for clave in documento.keys():
            if clave != "_id":
                etiqueta = tk.Label(frame_campos_actualizar, text=clave)
                etiqueta.pack(side=tk.LEFT)
                entrada = tk.Entry(frame_campos_actualizar)
                entrada.pack(side=tk.LEFT)
                entrada.insert(0, documento[clave])
                frame_campos_actualizar.campos[clave] = entrada

        boton_actualizar = tk.Button(ventana_actualizar, text="Actualizar", command=lambda: actualizar_documento(coleccion, {"_id": ObjectId(documento["_id"])}, obtener_valores(frame_campos_actualizar)))
        boton_actualizar.pack()

    else:
        messagebox.showerror("Error", "No se encontró ningún documento con los valores ingresados")

# Función para crear la interfaz gráfica dinámica
def crear_interfaz(coleccion):
    # Crear la ventana de la interfaz
    ventana = tk.Toplevel()
    ventana.title(f"{coleccion.capitalize()} - Interfaz de Base de Datos")
    ventana.geometry("400x400")

    # Crear un frame para los campos de la colección
    frame_campos = tk.Frame(ventana)
    frame_campos.pack()

    # Mostrar los campos de la colección en la interfaz gráfica
    frame_campos.campos = {}
    mostrar_campos(coleccion, frame_campos)

    # Botones para realizar acciones en la colección seleccionada
    boton_mostrar = tk.Button(ventana, text="Mostrar documentos", command=lambda: mostrar_documentos(coleccion, widget_text))
    boton_mostrar.pack()

    boton_insertar = tk.Button(ventana, text="Insertar documento", command=lambda: insertar_documento(coleccion, frame_campos))
    boton_insertar.pack()

    boton_actualizar = tk.Button(ventana, text="Actualizar documento", command=lambda: buscar_documento_actualizar(coleccion, frame_campos))
    boton_actualizar.pack()

    boton_eliminar = tk.Button(ventana, text="Eliminar documento", command=lambda: eliminar_documento(coleccion, frame_campos))
    boton_eliminar.pack()

    # Crear un widget Text para mostrar los documentos de la colección seleccionada
    widget_text = tk.Text(ventana)
    widget_text.pack()

    # Ejecutar la interfaz
    ventana.mainloop()

# Crear la ventana de la interfaz principal
ventana_principal = tk.Tk()
ventana_principal.title("Interfaz de Base de Datos")
ventana_principal.geometry("1280x720")

# Etiqueta y lista desplegable para seleccionar la colección
etiqueta = tk.Label(ventana_principal, text="Seleccione una colección:")
etiqueta.pack()

coleccion_seleccionada = tk.StringVar()
coleccion_seleccionada.set("usuarios")  # Valor predeterminado
lista_desplegable = tk.OptionMenu(ventana_principal, coleccion_seleccionada, "usuarios", "rutinas", "ejercicios", "registro_ejercicios", "progreso")
lista_desplegable.pack()

# Botón para crear la interfaz gráfica dinámica
boton_crear_interfaz = tk.Button(ventana_principal, text="Crear interfaz", command=lambda: crear_interfaz(coleccion_seleccionada.get()))
boton_crear_interfaz.pack()

# Ejecutar la interfaz principal
ventana_principal.mainloop()