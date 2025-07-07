# AutoDelete YouTube Videos 🗑️🎬

This script automates the process of deleting videos from your YouTube "Watch Later" playlist using PyAutoGUI.

---

## Requirements 📦

- Python **3.11.10** 🐍

---

## Setup & Usage (English) 🇬🇧

### ⚙️ Requirements

- Python **3.11.10** 🐍

### 1️⃣ Create a Virtual Environment

**With `venv`:**
```bash
python3.11 -m venv venv
```

**With `virtualenv`:**
```bash
python3.11 -m pip install virtualenv
python3.11 -m virtualenv venv
```

### 2️⃣ Activate the Virtual Environment

**On Linux/macOS:**
```bash
source venv/bin/activate
```
**On Windows:**
```bash
venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run the Script 🚀

```bash
python script.py
```

---

## Features & Customization 🛠️

### Features

- 🖼️ **Image Recognition:**  
  Uses screenshots in the `img` folder to locate and interact with UI elements (browser icon, YouTube buttons, etc).

- 🔍 **Region-based Search:**  
  The script splits the screen into left and right halves to speed up image searches.

- 🗂️ **Automatic Tab Handling:**  
  Automatically opens/closes tabs and navigates to your "Watch Later" playlist.

- ⏱️ **Timing Controls:**  
  You can adjust `sleep` and `duration` values in the code to match your PC's speed.

- 🛑 **Hotkey Listener:**  
  Press `q` at any time to safely stop the script.

- 🖱️ **Easy Customization:**  
  Change the images in the `img` folder or tweak the logic in functions like `locate_img` and `change_to_not_available` to adapt to UI changes or other platforms.

### Customization

- 🖼️ **Browser Image:**  
  Replace the browser icon image in the `img` folder with a screenshot of your browser's icon. Make sure the filename matches the value of the `browser_img` variable in `script.py` (e.g., `brave.png` for Brave browser).

- 🔗 **Playlist URL:**  
  You can change the playlist URL by editing the value of the `playlist_url` variable at the top of the `script.py` file.

- ⏱️ **Adjust Timing:**  
  The script uses `sleep` and `duration` values to wait for your PC to respond. You may need to increase or decrease these values depending on your computer's speed and internet connection.

- 📌 **Pin Your Browser:**  
  For the script to work, your browser must be pinned to your taskbar.

---

# AutoDelete YouTube Videos 🗑️🎬

Este script automatiza el proceso de eliminar videos de tu lista de "Ver más tarde" en YouTube usando PyAutoGUI.

---

## Requisitos 📦

- Python **3.11.10** 🐍

---

## Configuración y Uso (Español) 🇪🇸

### ⚙️ Requisitos

- Python **3.11.10** 🐍

### 1️⃣ Crear un Entorno Virtual

**Con `venv`:**
```bash
python3.11 -m venv venv
```

**Con `virtualenv`:**
```bash
python3.11 -m pip install virtualenv
python3.11 -m virtualenv venv
```

### 2️⃣ Activar el Entorno Virtual

**En Linux/macOS:**
```bash
source venv/bin/activate
```
**En Windows:**
```bash
venv\Scripts\activate
```

### 3️⃣ Instalar las Dependencias

```bash
pip install -r requirements.txt
```

### 4️⃣ Ejecutar el Script 🚀

```bash
python script.py
```

---

## Funcionalidades y Personalización 🛠️

### Funcionalidades

- 🖼️ **Reconocimiento de Imágenes:**  
  Usa capturas en la carpeta `img` para localizar e interactuar con elementos de la interfaz (icono del navegador, botones de YouTube, etc).

- 🔍 **Búsqueda por Regiones:**  
  El script divide la pantalla en mitades izquierda y derecha para acelerar la búsqueda de imágenes.

- 🗂️ **Manejo Automático de Pestañas:**  
  Abre/cierra pestañas y navega automáticamente a tu lista de "Ver más tarde".

- ⏱️ **Control de Tiempos:**  
  Puedes ajustar los valores de `sleep` y `duration` en el código según la velocidad de tu PC.

- 🛑 **Escucha de Teclas:**  
  Presiona `q` en cualquier momento para detener el script de forma segura.

- 🖱️ **Fácil Personalización:**  
  Cambia las imágenes en la carpeta `img` o ajusta la lógica en funciones como `locate_img` y `change_to_not_available` para adaptarlo a cambios en la interfaz o a otras plataformas.

### Personalización

- 🖼️ **Imagen del Navegador:**  
  Reemplaza la imagen del icono de tu navegador en la carpeta `img` con una captura de pantalla del icono de tu navegador. Asegúrate de que el nombre del archivo coincida con el valor de la variable `browser_img` en `script.py` (por ejemplo, `brave.png` para el navegador Brave).

- 🔗 **URL de la Playlist:**  
  Puedes cambiar la URL de la playlist que se usa modificando el valor de la variable `playlist_url` al inicio del archivo `script.py`.

- ⏱️ **Ajusta los Tiempos:**  
  El script utiliza valores de `sleep` y `duration` para esperar la respuesta de tu PC. Puede que necesites aumentar o disminuir estos valores dependiendo de la velocidad de tu computadora y conexión a internet.

- 📌 **Ancla tu Navegador:**  
  Para que el script funcione, es indispensable que tengas tu navegador anclado a tu barra de tareas.