import re
import tkinter as tk
from tkinter import font
from tkinter import messagebox
import math
import re
import os
import sys
import subprocess

# Importar configuración de colores y utilidades de ventana
from config import constantes as cons
import util.util_ventana as util_ventana
from util.db_manager import GestorBD

# Clase principal de la calculadora: interfaz, botones y conexión a historial
class formulario_calculadora(tk.Tk):
    def __init__(self):
        super().__init__()
        self.db = None
        self.resultado_mostrado = False  # Bandera para saber si se mostró un resultado
        self.error_mostrado = False  # Bandera para saber si se está mostrando un error
        # Mapeo de resultados numéricos a rutas de archivos multimedia (audio/video)
        # Edita las rutas según tus archivos locales.
        self.media_map = {
            67: r"C:\Users\caanm\Downloads\AY 67 - Sound Effect (HD).mp4",
            # Ejemplo: 7: r"C:\path\to\sound.mp3"
        }
        try:
            self.db = GestorBD()  # Inicializa la conexión a MariaDB
        except Exception as e:
            print(f"⚠️ Advertencia: No se pudo conectar a MariaDB. La calculadora funcionará sin historial.\n{e}")

        # Configura la ventana y crea los widgets de la calculadora
        self.config_window()
        self.construir_widget()
        
    def config_window(self):
        # Configuración general de la ventana principal
        self.title("Calculadora")
        self.configure(bg=cons.color_de_fondo_dark)
        self.attributes('-alpha', 0.96)
        w, h = 370, 590
        util_ventana.centrar_ventana(self, w, h)

        # Ajusta el ancho relativo de cada columna en la cuadrícula
        for i in range(4):
            self.grid_columnconfigure(i, weight=1)

    def construir_widget(self):
        # Crea el área donde se muestra la operación y el resultado
        self.operation_label = tk.Label(
            self, text="", font=('Arial', 14), bd=0, 
            bg=cons.color_de_fondo_dark, fg=cons.color_de_texto_dark, 
            anchor='e'
        )
        # 2. CAMBIO CLAVE: columnspan=4 y sticky='we' / anchor='e'
        # Ahora la etiqueta de la operación abarca de la columna 0 a la 3 sin deformar ninguna.
        self.operation_label = tk.Label(
            self, text="", font=('Arial', 14), bd=0, 
            bg=cons.color_de_fondo_dark, fg=cons.color_de_texto_dark, 
            anchor='e'
        )
        self.operation_label.grid(row=0, column=0, columnspan=4, sticky='we', padx=10, pady=(10, 0))

        # 3. CAMBIO CLAVE: Se quita width fijo del Entry y se usa sticky='we'
        self.entry = tk.Entry(
            self, font=('Arial', 32), bg=cons.color_caja_texto_dark, 
            fg=cons.color_de_texto_dark, justify='right'
        )
        self.entry.grid(row=1, column=0, columnspan=4, sticky='we', padx=10, pady=10)

        buttons = [
          '(', ')', 'x²', '√',
            'c', '%', '<', '/',
            '7', '8', '9', '*',
            '4', '5', '6', '-',
            '1', '2', '3', '+',
            '0', '.', '='
        ]

        row_value = 2
        col_value = 0

        roboto_font = font.Font(family='Roboto', size=16)

        for button in buttons: 
            if button in ['=', '*', '(', ')',  '/', '-', '+', 'c', '%', '<', 'x²', '√']:
                color_fondo = cons.color_botones_especiales_dark
                button_font = font.Font(size=16, weight='bold')
            else:
                color_fondo = cons.color_botones_dark
                button_font = roboto_font
            
            if button == '=':
                tk.Button(
                    self, text=button, height=2, bg=color_fondo, relief=tk.FLAT, 
                    fg=cons.color_de_texto_dark, font=button_font, 
                    command=lambda b=button: self.on_button_click(b)
                ).grid(row=row_value, column=col_value, columnspan=2, sticky='nsew', padx=2, pady=2) 
                col_value += 1
            else:
                tk.Button(
                    self, text=button, height=2, relief=tk.FLAT, bg=color_fondo, 
                    fg=cons.color_de_texto_dark, font=button_font, 
                    command=lambda b=button: self.on_button_click(b), overrelief='flat'
                ).grid(row=row_value, column=col_value, sticky='nsew', padx=2, pady=2)
                col_value += 1

            if col_value > 3:
                col_value = 0
                row_value += 1
        
        # Botón para ver historial (solo si MariaDB está disponible)
        if self.db:
            tk.Button(
                self, text="Historial", height=2, bg=cons.color_botones_especiales_dark, 
                relief=tk.FLAT, fg=cons.color_de_texto_dark, font=roboto_font, 
                command=self.mostrar_historial
            ).grid(row=row_value+1, column=0, columnspan=4, sticky='we', pady=5, padx=10)

    def on_button_click(self, button):
        if button == 'c':
            self.entry.delete(0, tk.END)
            self.operation_label.config(text="")
            self.resultado_mostrado = False
            self.error_mostrado = False

        elif button == '<':
            current_text = self.entry.get()
            self.entry.delete(0, tk.END)
            self.entry.insert(0, current_text[:-1])
            self.resultado_mostrado = False
            self.error_mostrado = False

        elif button == 'x²':
            # Muestra el símbolo de potencia en la pantalla
            self.entry.insert(tk.END, "^")
            self.resultado_mostrado = False 
        elif button == '√':
            # Agrega el símbolo de raíz cuadrada visible en la entrada
            self.entry.insert(tk.END, "√")
            self.resultado_mostrado = False

        elif button == '=':
            try:
                expression = self.entry.get()
                
                # Traducir la expresión visual a sintaxis válida de Python
                expr_eval = expression
                expr_eval = re.sub(r'(?<=\d)√', r'*√', expr_eval)
                expr_eval = re.sub(r'√(\d+(\.\d+)?)', r'math.sqrt(\1)', expr_eval)
                expr_eval = expr_eval.replace('^', '**')
                

                # Evaluar la expresión incluyendo el módulo math
                result = eval(expr_eval, {"__builtins__": None, "math": math})
                
                # Formatear el resultado si es entero (ej: 4.0 -> 4)
                if isinstance(result, float) and result.is_integer():
                    result = int(result)

                self.resultado_mostrado = True

                # Reacción a resultados específicos: reproducir media si hay coincidencia
                try:
                    key = result
                    if isinstance(key, float) and float(key).is_integer():
                        key = int(key)
                    if key in self.media_map:
                        self.play_media(self.media_map[key])
                except Exception as e:
                    print(f"Error al intentar reproducir media: {e}")

                # Guardar en MariaDB si está disponible
                if self.db:
                    self.db.guardar_operacion(expression, str(result))

                self.entry.delete(0, tk.END)
                self.entry.insert(0, str(result))
                self.operation_label.config(text=expression + " =")

            except Exception as e:
                self.entry.delete(0, tk.END)
                self.entry.insert(0, "Error")
                print(f"Error al evaluar la expresión: {e}")
                self.resultado_mostrado = False
                self.error_mostrado = True

        else:
            # Si hay un error mostrado, reemplazarlo con la nueva entrada
            if self.error_mostrado:
                self.entry.delete(0, tk.END)
                self.entry.insert(0, button)
                self.error_mostrado = False
                self.resultado_mostrado = False
            # Agregar dígito u operador a la entrada
            elif self.resultado_mostrado:
                if button in '0123456789.':
                    # Reemplazar el resultado con el nuevo número
                    self.entry.delete(0, tk.END)
                    self.entry.insert(0, button)
                else:
                    # Continuar la operación usando el resultado anterior
                    current_text = self.entry.get()
                    self.entry.delete(0, tk.END)
                    self.entry.insert(0, current_text + button)
                self.resultado_mostrado = False
            else:
                current_text = self.entry.get()
                new_text = current_text + button
                self.entry.delete(0, tk.END)
                self.entry.insert(0, new_text)

    
    def mostrar_historial(self):
        """Muestra una ventana con el historial de operaciones desde MariaDB"""
        if not self.db:
            messagebox.showwarning("Sin conexión", "MariaDB no está disponible")
            return
        
        historial = self.db.obtener_todas_operaciones()
        
        if not historial:
            messagebox.showinfo("Historial", "No hay operaciones guardadas")
            return
        
        # Crear ventana del historial
        ventana_historial = tk.Toplevel(self)
        ventana_historial.title("Historial de Operaciones (MariaDB)")
        ventana_historial.configure(bg=cons.color_de_fondo_dark)
        ventana_historial.geometry("500x400")
        
        # Frame con scrollbar
        frame = tk.Frame(ventana_historial, bg=cons.color_de_fondo_dark)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Crear texto con scrollbar
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(frame, yscrollcommand=scrollbar.set, bg=cons.color_caja_texto_dark, 
                              fg=cons.color_de_texto_dark, font=('Arial', 10), height=15, width=50)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        
        # Llenar con el historial
        for expresion, resultado, fecha_hora in historial:
            text_widget.insert(tk.END, f"{expresion} = {resultado}\n")
            text_widget.insert(tk.END, f"   Fecha: {fecha_hora}\n\n")
        
        text_widget.config(state=tk.DISABLED)  # Hacer de solo lectura
        
        # Botón para limpiar historial
        btn_limpiar = tk.Button(ventana_historial, text="Limpiar Historial", 
                               bg=cons.color_botones_especiales_dark, fg=cons.color_de_texto_dark,
                               command=lambda: self.limpiar_historial_bd(ventana_historial))
        btn_limpiar.pack(pady=10)
    
    def limpiar_historial_bd(self, ventana):
        """Limpia el historial de MariaDB y cierra la ventana"""
        if messagebox.askyesno("Confirmar", "¿Deseas eliminar todo el historial?"):
            if self.db and self.db.limpiar_historial():
                ventana.destroy()
                messagebox.showinfo("Éxito", "Historial eliminado correctamente")
            else:
                messagebox.showerror("Error", "No se pudo limpiar el historial")

    def play_media(self, filepath):
        """Intenta reproducir/abrir un archivo multimedia con el reproductor por defecto."""
        try:
            if sys.platform.startswith('win'):
                os.startfile(filepath)
            elif sys.platform.startswith('darwin'):
                subprocess.Popen(['open', filepath])
            else:
                subprocess.Popen(['xdg-open', filepath])
        except Exception as e:
            messagebox.showerror("Error reproducción", f"No se pudo abrir el archivo: {e}")