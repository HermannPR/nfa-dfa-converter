import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from PIL import Image, ImageTk
import os
import postfix
import NFA
from NFA import nfa_to_dot, simulate_nfa
from nfa_to_dfa import nfa_2_dfa, dfa_to_dot

class RegexApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Autómatas")
        self.root.geometry("800x800")  # Altura adecuada para ambos autómatas
        
        # Centrar la ventana principal
        self.center_window(800, 800)
        
        # Variable para el modo oscuro
        self.dark_mode = False
        self.dark_mode_first_time = True
        
        # Configurar estilos
        self.style = ttk.Style()
        self.create_styles()
        
        self.create_widgets()
        self.current_nfa = None
        self.current_dfa = None
        self.nfa_image_path = None
        self.dfa_image_path = None
        
        # Nuevas variables para el zoom
        self.nfa_zoom_factor = 1.0
        self.dfa_zoom_factor = 0.8  # Valor inicial más bajo para mostrar DFA más alejado
        self.original_nfa_image = None
        self.original_dfa_image = None

        # Nuevas variables para posición del ratón y la imagen
        self.nfa_mouse_x = 0
        self.nfa_mouse_y = 0
        self.dfa_mouse_x = 0
        self.dfa_mouse_y = 0
        self.nfa_image_id = None
        self.dfa_image_id = None
        
    def create_styles(self):
        # Estilos para tema claro
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabelframe', background='#f0f0f0')
        self.style.configure('TLabelframe.Label', background='#f0f0f0', foreground='#000000')
        self.style.configure('TLabel', background='#f0f0f0', foreground='#000000')
        self.style.configure('TButton', background='#e0e0e0', foreground='#000000')
        self.style.configure('TCheckbutton', background='#f0f0f0', foreground='#000000')
        self.style.map('TButton', 
            background=[('active', '#d0d0d0')],
            foreground=[('active', '#000000')]
        )
        self.style.configure('TEntry', fieldbackground='#ffffff', foreground='#000000')
        # Estilo para fondo blanco en los frames de control
        self.style.configure('White.TFrame', background='#ffffff')
        
    def toggle_dark_mode(self):
        """Alterna entre el tema claro y oscuro de la aplicación"""
        self.dark_mode = not self.dark_mode
        # Definir colores una sola vez, incluyendo frame_control_bg
        bg_color, fg_color, entry_bg, entry_fg, text_bg, text_fg, button_bg, button_fg, tab_bg, canvas_bg, frame_control_bg, scroll_bg, scroll_fg = (
            ('#000000', '#d3d3d3', '#1c1c1c', '#d3d3d3', '#1c1c1c', '#d3d3d3', '#333333', '#d3d3d3', '#1c1c1c', '#000000', '#000000', '#222222', '#555555')
            if self.dark_mode else
            ('#f0f0f0', '#000000', '#ffffff', '#000000', '#ffffff', '#000000', '#e0e0e0', '#000000', '#f0f0f0', '#ffffff', '#ffffff', '#e0e0e0', '#b0b0b0')
        )
    
        # Aplicar colores a widgets tk
        self.root.configure(bg=bg_color)
        self.main_canvas.config(bg=bg_color)
        self.dark_mode_btn.config(text="🌞 Modo Claro" if self.dark_mode else "🌙 Modo Oscuro", bg=button_bg, fg=button_fg)
        self.regex_entry.config(bg=entry_bg, fg=entry_fg)
        self.word_entry.config(bg=entry_bg, fg=entry_fg)
        self.result_text.config(bg=text_bg, fg=text_fg)
        self.validation_result.config(background=bg_color, foreground=fg_color)
    
        for btn in self.tk_buttons:
            btn.config(bg=button_bg, fg=button_fg)
    
        # Aplicar colores a estilos ttk
        self.style.theme_use('clam') # Asegurar tema clam para scrollbars
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabelframe', background=bg_color)
        self.style.configure('TLabelframe.Label', background=bg_color, foreground=fg_color)
        self.style.configure('TLabel', background=bg_color, foreground=fg_color)
        self.style.configure('TEntry', fieldbackground=entry_bg, foreground=entry_fg)
        self.style.configure('White.TFrame', background=frame_control_bg) # Ahora frame_control_bg está definido
        self.style.configure('Main.TFrame', background=bg_color)
        self.style.configure('Vertical.TScrollbar', background=scroll_bg, troughcolor=scroll_fg, arrowcolor=scroll_fg)
        self.style.configure('Horizontal.TScrollbar', background=scroll_bg, troughcolor=scroll_fg, arrowcolor=scroll_fg)
        self.style.configure('TNotebook', background=tab_bg)
        self.style.configure('TNotebook.Tab', background=tab_bg, foreground='#000000')
        self.style.map('TNotebook.Tab', background=[('selected', button_bg)], foreground=[('selected', '#000000')])
    
        # Aplicar colores a canvas
        self.nfa_canvas.config(bg=canvas_bg)
        self.dfa_canvas.config(bg=canvas_bg)
    
        # Invertir colores de imágenes si existen
        if self.nfa_image_path:
            self.display_nfa_image(self.nfa_image_path, invert_colors=self.dark_mode)
        if self.dfa_image_path:
            self.display_dfa_image(self.dfa_image_path, invert_colors=self.dark_mode)
    
        # Resetear zoom para asegurar redibujado
        self.reset_zoom_nfa()
        self.reset_zoom_dfa()

        # Forzar actualización de la UI
        self.main_canvas.update_idletasks()
        self.root.update()

    def create_widgets(self):
        self.tk_buttons = []

        # Canvas principal con scrollbar
        self.main_canvas = tk.Canvas(self.root, borderwidth=0, background="#f0f0f0")
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.main_canvas.configure(yscrollcommand=v_scrollbar.set)

        # Frame dentro del canvas
        main_frame = ttk.Frame(self.main_canvas, padding="10")
        self.main_frame = main_frame  # Guarda referencia si la necesitas

        # Crear ventana dentro del canvas
        self.main_canvas.create_window((0, 0), window=main_frame, anchor="nw")

        # Ajustar el scrollregion cuando cambie el tamaño del frame
        def on_frame_configure(event):
            self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        main_frame.bind("<Configure>", on_frame_configure)

        # Permitir scroll con la rueda del ratón
        def _on_mousewheel(event):
            self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Cambiar fondo del frame principal (main_frame) usando estilos ttk
        self.style.configure('Main.TFrame', background='#f0f0f0')
        # Cambiar fondo de los LabelFrame (Expresión Regular, Resultados, Visualización de Autómatas, Validar Palabras)
        self.style.configure('TLabelframe', background='#f0f0f0')
        self.style.configure('TLabelframe.Label', background='#f0f0f0', foreground='#000000')
        # Cambiar color de la scrollbar de resultados (usando ttk.Style y tema clam)
        self.style.theme_use('clam')
        self.style.configure('Vertical.TScrollbar', background='#e0e0e0', troughcolor='#b0b0b0', arrowcolor='#b0b0b0')
        self.style.configure('Horizontal.TScrollbar', background='#e0e0e0', troughcolor='#b0b0b0', arrowcolor='#b0b0b0')
       
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(fill=tk.X, pady=5)

        # Botón para limpiar todo
        clear_all_btn = tk.Button(toolbar_frame, text="🗑️ Limpiar Todo", 
                               command=self.clear_all,
                               bg='#e0e0e0', fg='#000000')
        clear_all_btn.pack(side=tk.LEFT, padx=5)
        self.tk_buttons.append(clear_all_btn)

        # Frame para los botones de tamaño de fuente
        font_frame = ttk.Frame(toolbar_frame)
        font_frame.pack(side=tk.LEFT, padx=5)

        # Botones para cambiar el tamaño de la fuente
        decrease_font_btn = tk.Button(font_frame, text="A-", width=3, 
                                   command=self.decrease_font_size,
                                   bg='#e0e0e0', fg='#000000')
        decrease_font_btn.pack(side=tk.LEFT)
        self.tk_buttons.append(decrease_font_btn)

        increase_font_btn = tk.Button(font_frame, text="A+", width=3, 
                                   command=self.increase_font_size,
                                   bg='#e0e0e0', fg='#000000')
        increase_font_btn.pack(side=tk.LEFT)
        self.tk_buttons.append(increase_font_btn)

        # Botón para acerca de
        about_btn = tk.Button(toolbar_frame, text="ℹ️ Acerca de", 
                           command=self.show_about,
                           bg='#e0e0e0', fg='#000000')
        about_btn.pack(side=tk.LEFT, padx=5)
        self.tk_buttons.append(about_btn)

        # Botón para alternar modo oscuro
        self.dark_mode_btn = tk.Button(toolbar_frame, 
                                    text="🌙 Modo Oscuro",
                                    command=self.toggle_dark_mode,
                                    bg='#e0e0e0', fg='#000000')
        self.dark_mode_btn.pack(side=tk.RIGHT, padx=5)

        # Frame superior para entrada y botones
        input_frame = ttk.LabelFrame(main_frame, text="Expresión Regular", padding="10")
        input_frame.pack(fill=tk.X, pady=10)

        ttk.Label(input_frame, text="Ingresar expresión (infix):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.regex_entry = tk.Entry(input_frame, width=40, bg='#ffffff', fg='#000000')
        self.regex_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        self.regex_entry.insert(0, "a*b+c")

        # Botón Generar Autómata 
        self.generate_btn = tk.Button(input_frame, text="Generar Autómata", 
                        command=self.generate_automaton,
                        bg='#e0e0e0', fg='#000000',
                        relief=tk.RAISED, padx=10)
        self.generate_btn.grid(row=0, column=2, padx=10, pady=5)
        self.tk_buttons.append(self.generate_btn)

        # Frame para mostrar resultados
        result_frame = ttk.LabelFrame(main_frame, text="Resultados", padding="10")
        result_frame.pack(fill=tk.X, pady=10)

        self.result_text = scrolledtext.ScrolledText(result_frame, height=5)
        self.result_text.pack(fill=tk.X)
        self.result_text.config(state=tk.DISABLED)

        # Frame para mostrar ambos autómatas con pestañas
        automata_frame = ttk.LabelFrame(main_frame, text="Visualización de Autómatas", padding="10")
        automata_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Crear pestañas para NFA y DFA
        automata_notebook = ttk.Notebook(automata_frame)
        automata_notebook.pack(fill=tk.BOTH, expand=True)
        automata_notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # Pestaña para NFA con controles de zoom
        nfa_frame = ttk.Frame(automata_notebook)
        automata_notebook.add(nfa_frame, text="NFA")

        # Frame de control para botones de zoom
        nfa_control_frame = ttk.Frame(nfa_frame, style='White.TFrame')
        nfa_control_frame.pack(fill=tk.X, pady=5)

        # Botones de zoom para NFA
        zoom_in_nfa = tk.Button(nfa_control_frame, text="🔍+", 
                          command=self.zoom_in_nfa,
                          bg='#e0e0e0', fg='#000000')
        zoom_in_nfa.pack(side=tk.LEFT, padx=5)
        self.tk_buttons.append(zoom_in_nfa)

        zoom_out_nfa = tk.Button(nfa_control_frame, text="🔍-", 
                           command=self.zoom_out_nfa,
                           bg='#e0e0e0', fg='#000000')
        zoom_out_nfa.pack(side=tk.LEFT, padx=5)
        self.tk_buttons.append(zoom_out_nfa)

        reset_zoom_nfa = tk.Button(nfa_control_frame, text="Reset Zoom", 
                             command=self.reset_zoom_nfa,
                             bg='#e0e0e0', fg='#000000')
        reset_zoom_nfa.pack(side=tk.LEFT, padx=5)
        self.tk_buttons.append(reset_zoom_nfa)

        # Botón de información para NFA
        info_nfa_btn = tk.Button(nfa_control_frame, text="ℹ️", width=2,
                                 command=lambda: messagebox.showinfo(
                                     "Controles de Navegación",
                                     "Utilice el scroll para zoom y el clic derecho para desplazar"
                                 ),
                                 bg='#e0e0e0', fg='#000000')
        info_nfa_btn.pack(side=tk.LEFT, padx=5)
        self.tk_buttons.append(info_nfa_btn)

        # Crear un frame con scrollbars para el canvas
        nfa_scroll_frame = ttk.Frame(nfa_frame)
        nfa_scroll_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbars horizontal y vertical
        nfa_h_scroll = ttk.Scrollbar(nfa_scroll_frame, orient=tk.HORIZONTAL)
        nfa_h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        nfa_v_scroll = ttk.Scrollbar(nfa_scroll_frame, orient=tk.VERTICAL)
        nfa_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Canvas para la imagen NFA con scrollbars
        self.nfa_canvas = tk.Canvas(nfa_scroll_frame, 
                             xscrollcommand=nfa_h_scroll.set,
                             yscrollcommand=nfa_v_scroll.set,
                             bg='#ffffff',  # Fondo blanco por defecto
                             highlightthickness=0)
        self.nfa_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Pestaña para DFA con controles de zoom
        dfa_frame = ttk.Frame(automata_notebook)
        automata_notebook.add(dfa_frame, text="DFA")

        # Frame de control para botones de zoom
        dfa_control_frame = ttk.Frame(dfa_frame, style='White.TFrame')
        dfa_control_frame.pack(fill=tk.X, pady=5)

        # Botones de zoom para DFA
        zoom_in_dfa = tk.Button(dfa_control_frame, text="🔍+", 
                          command=self.zoom_in_dfa,
                          bg='#e0e0e0', fg='#000000')
        zoom_in_dfa.pack(side=tk.LEFT, padx=5)
        self.tk_buttons.append(zoom_in_dfa)

        zoom_out_dfa = tk.Button(dfa_control_frame, text="🔍-", 
                           command=self.zoom_out_dfa,
                           bg='#e0e0e0', fg='#000000')
        zoom_out_dfa.pack(side=tk.LEFT, padx=5)
        self.tk_buttons.append(zoom_out_dfa)

        reset_zoom_dfa = tk.Button(dfa_control_frame, text="Reset Zoom", 
                             command=self.reset_zoom_dfa,
                             bg='#e0e0e0', fg='#000000')
        reset_zoom_dfa.pack(side=tk.LEFT, padx=5)
        self.tk_buttons.append(reset_zoom_dfa)

        # Botón de información para DFA
        info_dfa_btn = tk.Button(dfa_control_frame, text="ℹ️", width=2,
                                 command=lambda: messagebox.showinfo(
                                     "Controles de Navegación",
                                     "Utilice el scroll para zoom y el clic derecho para desplazar"
                                 ),
                                 bg='#e0e0e0', fg='#000000')
        info_dfa_btn.pack(side=tk.LEFT, padx=5)
        self.tk_buttons.append(info_dfa_btn)

        # Crear un frame con scrollbars para el canvas
        dfa_scroll_frame = ttk.Frame(dfa_frame)
        dfa_scroll_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbars horizontal y vertical
        dfa_h_scroll = ttk.Scrollbar(dfa_scroll_frame, orient=tk.HORIZONTAL)
        dfa_h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        dfa_v_scroll = ttk.Scrollbar(dfa_scroll_frame, orient=tk.VERTICAL)
        dfa_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Canvas para la imagen DFA con scrollbars
        self.dfa_canvas = tk.Canvas(dfa_scroll_frame, 
                             xscrollcommand=dfa_h_scroll.set,
                             yscrollcommand=dfa_v_scroll.set,
                             bg='#ffffff',  # Fondo blanco por defecto
                             highlightthickness=0)
        self.dfa_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # MODIFICADO: Frame para validación de palabras (con resultados en la misma línea)
        validate_frame = ttk.LabelFrame(main_frame, text="Validar Palabras", padding="10")
        validate_frame.pack(fill=tk.X, pady=10)

        # Diseño horizontal integrado: etiqueta, campo de entrada, botón y resultados
        ttk.Label(validate_frame, text="Palabra a validar:").pack(side=tk.LEFT, padx=(0,10))

        self.word_entry = tk.Entry(validate_frame, width=20, bg='#ffffff', fg='#000000')
        self.word_entry.pack(side=tk.LEFT, padx=(0,10))

        validate_btn = tk.Button(validate_frame, text="Validar",
                               command=self.validate_word,
                               bg='#e0e0e0', fg='#000000')
        validate_btn.pack(side=tk.LEFT, padx=(0,10))
        self.tk_buttons.append(validate_btn)

        # Resultados en la misma línea
        ttk.Label(validate_frame, text="Resultado:").pack(side=tk.LEFT, padx=(10,5))

        # Área de resultados inline (usando Label en lugar de ScrolledText)
        self.validation_result = ttk.Label(validate_frame, text="Pendiente de validación", 
                                         background='#f0f0f0', padding=(5,2))
        self.validation_result.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Variables para el manejo de fuentes
        self.font_size = 10
        self.update_fonts()

        # Configurar eventos de la rueda del ratón para zoom
        self.nfa_canvas.bind("<MouseWheel>", self.nfa_mouse_wheel)  # Windows
        self.nfa_canvas.bind("<Button-4>", self.nfa_mouse_wheel)    # Linux (arriba)
        self.nfa_canvas.bind("<Button-5>", self.nfa_mouse_wheel)    # Linux (abajo)
        
        self.dfa_canvas.bind("<MouseWheel>", self.dfa_mouse_wheel)  # Windows
        self.dfa_canvas.bind("<Button-4>", self.dfa_mouse_wheel)    # Linux (arriba)
        self.dfa_canvas.bind("<Button-5>", self.dfa_mouse_wheel)    # Linux (abajo)

        # Configurar eventos para arrastrar con clic derecho
        self.nfa_canvas.bind('<Button-3>', self.start_nfa_pan)
        self.nfa_canvas.bind('<B3-Motion>', self.nfa_pan)
        self.dfa_canvas.bind('<Button-3>', self.start_dfa_pan)
        self.dfa_canvas.bind('<B3-Motion>', self.dfa_pan)

        # Configurar eventos de movimiento del ratón para guardar posición
        self.nfa_canvas.bind("<Motion>", self.nfa_mouse_move)
        self.dfa_canvas.bind("<Motion>", self.dfa_mouse_move)
    
    def update_fonts(self):
        """Actualiza el tamaño de fuente en los widgets de texto"""
        font_config = ("Consolas", self.font_size)
        self.result_text.config(font=font_config)
        self.validation_result.config(font=font_config)  # Añadido
        
    def increase_font_size(self):
        """Aumenta el tamaño de la fuente"""
        if self.font_size < 20:  # Limitar el tamaño máximo
            self.font_size += 2
            self.update_fonts()
            
    def decrease_font_size(self):
        """Disminuye el tamaño de la fuente"""
        if self.font_size > 8:  # Limitar el tamaño mínimo
            self.font_size -= 2
            self.update_fonts()
    
    def clear_all(self):
        """Limpia todos los campos y reinicia la aplicación"""
        self.regex_entry.delete(0, tk.END)
        self.regex_entry.insert(0, "a*b+c")  # Valor por defecto
        
        self.validation_result.config(text="Pendiente de validación")
        
        # Limpiar ambas imágenes y reiniciar zoom
        self.nfa_canvas.delete("all")
        self.dfa_canvas.delete("all")
        
        self.current_nfa = None
        self.current_dfa = None
        self.nfa_image_path = None
        self.dfa_image_path = None
        self.original_nfa_image = None
        self.original_dfa_image = None
        self.nfa_zoom_factor = 1.0
        self.dfa_zoom_factor = 0.8  # Zoom inicial para DFA más alejado

        # Limpiar el campo de palabra y resultados de validación
        self.word_entry.delete(0, tk.END)
        self.validation_result.config(text="Pendiente de validación")
    
    def show_about(self):
        """Muestra información sobre la aplicación"""
        messagebox.showinfo(
            "Acerca de", 
            "Visualizador de Autómatas Finitos\n\n"
            "Esta aplicación permite:\n"
            "• Convertir expresiones regulares a autómatas finitos\n"
            "• Visualizar autómatas finitos no deterministas (NFA)\n"
            "• Visualizar autómatas finitos deterministas (DFA)\n"
            "• Probar la validación de palabras en los autómatas\n"
            "• Manipular los diagramas con zoom y navegación\n\n"
            "La aplicación implementa el algoritmo de Thompson para construcción\n"
            "de NFAs y el algoritmo de subconjuntos para conversión a DFAs.\n\n"

        )
    
    def generate_automaton(self):
        """Genera el NFA y DFA a partir de la expresión regular ingresada"""
        try:
            infix = self.regex_entry.get()
            if not infix:
                messagebox.showwarning("Advertencia", "Ingrese una expresión regular")
                return
            
            # Habilitar el widget temporalmente para modificarlo
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Expresión infix: {infix}\n")
            
            with_concatenation = postfix.add_concatenation(infix)
            self.result_text.insert(tk.END, f"Con concatenación explícita: {with_concatenation}\n")
            
            postfix_exp = postfix.infix_to_postfix(with_concatenation)
            self.result_text.insert(tk.END, f"Expresión postfix: {postfix_exp}\n")
            
            # Generar NFA
            self.current_nfa = NFA.build_nfa(postfix_exp)
            nfa_dot_code = nfa_to_dot(self.current_nfa)
            
            with open("nfaa.dot", "w", encoding="UTF-8") as f:
                f.write(nfa_dot_code)
            
            os.system("dot -Tpng -Gdpi=300 nfaa.dot -o nfaa.png")
            self.nfa_image_path = "nfaa.png"  # Guardar la ruta del NFA

            # Generar DFA a partir del NFA
            dfa_states, dfa_transitions, start, accept_states, symbols = nfa_2_dfa(self.current_nfa)
            dfa_dot_code = dfa_to_dot(dfa_states, dfa_transitions, start, accept_states)
            
            with open("dfa.dot", "w", encoding="UTF-8") as f:
                f.write(dfa_dot_code)
                
            os.system("dot -Tpng dfa.dot -o dfa.png")
            self.dfa_image_path = "dfa.png"  # Guardar la ruta del DFA

            # Convertir las imágenes a modo oscuro si está activado
            if self.dark_mode:
                self.display_nfa_image(self.nfa_image_path, invert_colors=True)
                self.display_dfa_image(self.dfa_image_path, invert_colors=True)
            else:
                self.display_nfa_image(self.nfa_image_path, invert_colors=False)
                self.display_dfa_image(self.dfa_image_path, invert_colors=False)

            # Llamar a las funciones de reset zoom para NFA y DFA
            self.reset_zoom_nfa()
            self.reset_zoom_dfa()
            
            self.result_text.insert(tk.END, "¡Autómatas generados con éxito!\n")
            self.result_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar el autómata: {str(e)}")
            self.result_text.config(state=tk.NORMAL)
            self.result_text.insert(tk.END, f"ERROR: {str(e)}\n")
            self.result_text.config(state=tk.DISABLED)
            self.validation_result.config(text="Error al generar autómata")
    
    def display_nfa_image(self, image_path, invert_colors=False):
        """Muestra la imagen del NFA en su canvas correspondiente"""
        try:
            self.original_nfa_image = Image.open(image_path).convert("RGB")  # Asegurar modo RGB
            self.nfa_image_path = image_path

            if invert_colors:
                # Invertir colores de la imagen
                self.original_nfa_image = Image.eval(self.original_nfa_image, lambda x: 255 - x)

            photo = ImageTk.PhotoImage(self.original_nfa_image)

            self.nfa_canvas.delete("all")
            self.nfa_canvas.create_image(0, 0, image=photo, anchor="nw")
            self.nfa_canvas.image = photo

            # Configurar región de scroll basada en el tamaño original de la imagen
            self.nfa_canvas.config(scrollregion=(0, 0, self.original_nfa_image.width, self.original_nfa_image.height))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen NFA: {str(e)}")

    def display_dfa_image(self, image_path, invert_colors=False):
        """Muestra la imagen del DFA en su canvas correspondiente"""
        try:
            self.original_dfa_image = Image.open(image_path).convert("RGB")  # Asegurar modo RGB
            self.dfa_image_path = image_path

            if invert_colors:
                # Invertir colores de la imagen
                self.original_dfa_image = Image.eval(self.original_dfa_image, lambda x: 255 - x)

            photo = ImageTk.PhotoImage(self.original_dfa_image)

            self.dfa_canvas.delete("all")
            self.dfa_canvas.create_image(0, 0, image=photo, anchor="nw")
            self.dfa_canvas.image = photo

            # Configurar región de scroll basada en el tamaño original de la imagen
            self.dfa_canvas.config(scrollregion=(0, 0, self.original_dfa_image.width, self.original_dfa_image.height))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen DFA: {str(e)}")

    def zoom_in_nfa(self):
        """Aumenta el zoom de la imagen NFA"""
        if self.original_nfa_image:
            self.nfa_zoom_factor *= 1.2
            self.apply_zoom_nfa()

    def zoom_out_nfa(self):
        """Reduce el zoom de la imagen NFA"""
        if self.original_nfa_image:
            self.nfa_zoom_factor /= 1.2
            self.apply_zoom_nfa()

    def reset_zoom_nfa(self):
        """Restaura el zoom original de la imagen NFA"""
        if self.original_nfa_image:
            self.nfa_zoom_factor = 0.24
            self.apply_zoom_nfa()

    def zoom_in_dfa(self):
        """Aumenta el zoom de la imagen DFA"""
        if self.original_dfa_image:
            self.dfa_zoom_factor *= 1.2
            self.apply_zoom_dfa()

    def zoom_out_dfa(self):
        """Reduce el zoom de la imagen DFA"""
        if self.original_dfa_image:
            self.dfa_zoom_factor /= 1.2
            self.apply_zoom_dfa()

    def reset_zoom_dfa(self):
        """Restaura el zoom original de la imagen DFA"""
        if self.original_dfa_image:
            self.dfa_zoom_factor = 0.15  # Zoom predefinido más alejado
            self.apply_zoom_dfa()

    def apply_zoom_nfa(self):
        """Aplica el factor de zoom a la imagen NFA usando canvas"""
        if not self.original_nfa_image:
            return
        
        try:
            # Obtener dimensiones originales
            orig_width, orig_height = self.original_nfa_image.size
            
            # Calcular nuevas dimensiones con zoom
            width = int(orig_width * self.nfa_zoom_factor)
            height = int(orig_height * self.nfa_zoom_factor)
            
            # Asegurar que width y height siempre sean mayores que 0
            width = max(1, width)
            height = max(1, height)
            
            # Limitar el tamaño máximo para evitar problemas de memoria
            max_dimension = 4000
            if width > max_dimension or height > max_dimension:
                ratio = min(max_dimension / width, max_dimension / height)
                width = int(width * ratio)
                height = int(height * ratio)
                self.nfa_zoom_factor *= ratio
            
            # Redimensionar la imagen con el zoom aplicado
            img = self.original_nfa_image.resize((width, height), Image.LANCZOS)
            
            # Convertir a PhotoImage para el canvas
            photo = ImageTk.PhotoImage(img)
            
            # Limpiar el canvas y mostrar la nueva imagen
            self.nfa_canvas.delete("all")
            self.nfa_image_id = self.nfa_canvas.create_image(0, 0, image=photo, anchor="nw")
            self.nfa_canvas.image = photo  # Mantener referencia
            
            # Actualizar la región desplazable
            self.nfa_canvas.config(scrollregion=(0, 0, width, height))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar zoom: {str(e)}")

    def apply_zoom_nfa(self):
        """Aplica el factor de zoom a la imagen NFA usando canvas"""
        if not self.original_nfa_image:
            return
        
        try:
            # Obtener dimensiones originales
            orig_width, orig_height = self.original_nfa_image.size
            
            # Calcular nuevas dimensiones con zoom
            width = int(orig_width * self.nfa_zoom_factor)
            height = int(orig_height * self.nfa_zoom_factor)
            
            # Asegurar que width y height siempre sean mayores que 0
            width = max(1, width)
            height = max(1, height)
            
            # Limitar el tamaño máximo para evitar problemas de memoria
            max_dimension = 4000
            if width > max_dimension or height > max_dimension:
                ratio = min(max_dimension / width, max_dimension / height)
                width = int(width * ratio)
                height = int(height * ratio)
                self.nfa_zoom_factor *= ratio
            
            # Redimensionar la imagen con el zoom aplicado
            img = self.original_nfa_image.resize((width, height), Image.LANCZOS)
            
            # Convertir a PhotoImage para el canvas
            photo = ImageTk.PhotoImage(img)
            
            # Limpiar el canvas y mostrar la nueva imagen
            self.nfa_canvas.delete("all")
            self.nfa_image_id = self.nfa_canvas.create_image(0, 0, image=photo, anchor="nw")
            self.nfa_canvas.image = photo  # Mantener referencia
            
            # Actualizar la región desplazable
            self.nfa_canvas.config(scrollregion=(0, 0, width, height))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar zoom: {str(e)}")
    
    def apply_zoom_dfa(self):
        """Aplica el factor de zoom a la imagen DFA usando canvas"""
        if not self.original_dfa_image:
            return
        
        try:
            # Obtener dimensiones originales
            orig_width, orig_height = self.original_dfa_image.size
            
            # Calcular nuevas dimensiones con zoom
            width = int(orig_width * self.dfa_zoom_factor)
            height = int(orig_height * self.dfa_zoom_factor)
            
            # Asegurar que width y height siempre sean mayores que 0
            width = max(1, width)
            height = max(1, height)
            
            # Limitar el tamaño máximo para evitar problemas de memoria
            max_dimension = 4000
            if width > max_dimension or height > max_dimension:
                ratio = min(max_dimension / width, max_dimension / height)
                width = int(width * ratio)
                height = int(height * ratio)
                self.dfa_zoom_factor *= ratio
            
            # Redimensionar la imagen con el zoom aplicado
            img = self.original_dfa_image.resize((width, height), Image.LANCZOS)
            
            # Convertir a PhotoImage para el canvas
            photo = ImageTk.PhotoImage(img)
            
            # Limpiar el canvas y mostrar la nueva imagen
            self.dfa_canvas.delete("all")
            self.dfa_image_id = self.dfa_canvas.create_image(0, 0, image=photo, anchor="nw")
            self.dfa_canvas.image = photo  # Mantener referencia
            
            # Actualizar la región desplazable
            self.dfa_canvas.config(scrollregion=(0, 0, width, height))
            
            # Forzar actualización inmediata del canvas
            self.dfa_canvas.update_idletasks()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar zoom: {str(e)}")

    def validate_word(self):
        """Validación simple de una palabra contra el autómata actual"""
        # Verificar que exista un autómata
        if not self.current_nfa:
            messagebox.showwarning("Advertencia", "Primero genere un autómata")
            return
        
        # Obtener la palabra a validar
        word = self.word_entry.get()
        
        try:
            # Validar la palabra usando el NFA
            result = simulate_nfa(self.current_nfa, word)
            
            # Mostrar resultado
            if result:
                self.validation_result.config(
                    text=f"La palabra '{word}' es ACEPTADA", 
                    foreground="green",
                    font=("Consolas", 10, "bold")
                )
            else:
                self.validation_result.config(
                    text=f"La palabra '{word}' es RECHAZADA", 
                    foreground="red",
                    font=("Consolas", 10, "bold")
                )
        
        except Exception as e:
            self.validation_result.config(
                text=f"Error: {str(e)}", 
                foreground="red",
                font=("Consolas", 10, "bold")
            )

    def nfa_mouse_wheel(self, event):
        """Zoom centrado en la posición del ratón para la imagen NFA"""
        if not self.original_nfa_image:
            return
        
        # Guardar el factor de zoom anterior
        old_zoom = self.nfa_zoom_factor
        
        # Calcular nuevo factor de zoom
        if event.num == 5 or event.delta < 0:
            self.nfa_zoom_factor /= 1.1
            if self.nfa_zoom_factor < 0.1:  # Limitar zoom mínimo
                self.nfa_zoom_factor = 0.1
        if event.num == 4 or event.delta > 0:
            self.nfa_zoom_factor *= 1.1
            if self.nfa_zoom_factor > 10:  # Limitar zoom máximo
                self.nfa_zoom_factor = 10
        
        # Obtener posición relativa del cursor respecto a la imagen
        canvas_width = self.nfa_canvas.winfo_width()
        canvas_height = self.nfa_canvas.winfo_height()
        
        # Calcular el desplazamiento para mantener el zoom centrado
        x_frac = self.nfa_mouse_x / (old_zoom * self.original_nfa_image.width)
        y_frac = self.nfa_mouse_y / (old_zoom * self.original_nfa_image.height)
        
        # Aplicar el zoom
        self.apply_zoom_nfa()
        
        # Centrar en el punto donde estaba el cursor
        new_width = self.nfa_zoom_factor * self.original_nfa_image.width
        new_height = self.nfa_zoom_factor * self.original_nfa_image.height
        
        # Calcular nuevas coordenadas del centro
        new_x = x_frac * new_width
        new_y = y_frac * new_height
        
        # Ajustar scrollbars para centrar el punto
        self.nfa_canvas.xview_moveto(max(0, (new_x - canvas_width/2) / new_width))
        self.nfa_canvas.yview_moveto(max(0, (new_y - canvas_height/2) / new_height))
        
        return "break"  # Prevenir el desplazamiento normal

    def dfa_mouse_wheel(self, event):
        """Zoom centrado en la posición del ratón para la imagen DFA"""
        if not self.original_dfa_image:
            return
        
        # Guardar el factor de zoom anterior
        old_zoom = self.dfa_zoom_factor
        
        # Calcular nuevo factor de zoom
        if event.num == 5 or event.delta < 0:
            self.dfa_zoom_factor /= 1.1
            if self.dfa_zoom_factor < 0.1:  # Limitar zoom mínimo
                self.dfa_zoom_factor = 0.1
        if event.num == 4 or event.delta > 0:
            self.dfa_zoom_factor *= 1.1
            if self.dfa_zoom_factor > 10:  # Limitar zoom máximo
                self.dfa_zoom_factor = 10
        
        # Obtener posición relativa del cursor respecto a la imagen
        canvas_width = self.dfa_canvas.winfo_width()
        canvas_height = self.dfa_canvas.winfo_height()
        
        # Calcular el desplazamiento para mantener el zoom centrado
        x_frac = self.dfa_mouse_x / (old_zoom * self.original_dfa_image.width)
        y_frac = self.dfa_mouse_y / (old_zoom * self.original_dfa_image.height)
        
        # Aplicar el zoom
        self.apply_zoom_dfa()
        
        # Centrar en el punto donde estaba el cursor
        new_width = self.dfa_zoom_factor * self.original_dfa_image.width
        new_height = self.dfa_zoom_factor * self.original_dfa_image.height
        
        # Calcular nuevas coordenadas del centro
        new_x = x_frac * new_width
        new_y = y_frac * new_height
        
        # Ajustar scrollbars para centrar el punto
        self.dfa_canvas.xview_moveto(max(0, (new_x - canvas_width/2) / new_width))
        self.dfa_canvas.yview_moveto(max(0, (new_y - canvas_height/2) / new_height))
        
        return "break"  # Prevenir el desplazamiento normal

    def nfa_mouse_move(self, event):
        """Guarda la posición actual del cursor en el canvas NFA"""
        self.nfa_mouse_x = self.nfa_canvas.canvasx(event.x)
        self.nfa_mouse_y = self.nfa_canvas.canvasy(event.y)

    def dfa_mouse_move(self, event):
        """Guarda la posición actual del cursor en el canvas DFA"""
        self.dfa_mouse_x = self.dfa_canvas.canvasx(event.x)
        self.dfa_mouse_y = self.dfa_canvas.canvasy(event.y)

    def start_nfa_pan(self, event):
        self.nfa_canvas.scan_mark(event.x, event.y)

    def nfa_pan(self, event):
        self.nfa_canvas.scan_dragto(event.x, event.y, gain=1)

    def start_dfa_pan(self, event):
        self.dfa_canvas.scan_mark(event.x, event.y)

    def dfa_pan(self, event):
        self.dfa_canvas.scan_dragto(event.x, event.y, gain=1)

    def on_tab_change(self, event):
        """Maneja el cambio de pestañas para asegurar que las imágenes se muestren correctamente"""
        tab = event.widget.tab(event.widget.index("current"), "text")

        if (tab == "DFA" and self.dfa_image_path) or (tab == "NFA" and self.nfa_image_path):
            self.force_update_canvas()

    def force_update_canvas(self):
        """Fuerza la actualización del canvas con técnicas más agresivas"""
        try:
            # Forzar actualización completa del canvas
            self.nfa_canvas.update()
            self.dfa_canvas.update()
            
            # Obtener dimensiones actuales
            nfa_width = int(self.original_nfa_image.width * self.nfa_zoom_factor)
            nfa_height = int(self.original_nfa_image.height * self.nfa_zoom_factor)
            dfa_width = int(self.original_dfa_image.width * self.dfa_zoom_factor)
            dfa_height = int(self.original_dfa_image.height * self.dfa_zoom_factor)
            
            # Asegurar dimensiones mínimas
            nfa_width = max(1, nfa_width)
            nfa_height = max(1, nfa_height)
            dfa_width = max(1, dfa_width)
            dfa_height = max(1, dfa_height)
            
            # Recrear la imagen con zoom aplicado
            nfa_img = self.original_nfa_image.resize((nfa_width, nfa_height), Image.LANCZOS)
            dfa_img = self.original_dfa_image.resize((dfa_width, dfa_height), Image.LANCZOS)
            
            # Crear nueva referencia de PhotoImage
            self.nfa_photo = ImageTk.PhotoImage(nfa_img)
            self.dfa_photo = ImageTk.PhotoImage(dfa_img)
            
            # Limpiar canvas y mostrar nueva imagen
            self.nfa_canvas.delete("all")
            self.nfa_image_id = self.nfa_canvas.create_image(0, 0, image=self.nfa_photo, anchor="nw")
            self.dfa_canvas.delete("all")
            self.dfa_image_id = self.dfa_canvas.create_image(0, 0, image=self.dfa_photo, anchor="nw")
            
            # Actualizar región de scroll
            self.nfa_canvas.config(scrollregion=(0, 0, nfa_width, nfa_height))
            self.dfa_canvas.config(scrollregion=(0, 0, dfa_width, dfa_height))
            
            # Hacer zoom out ligeramente para mostrar más del diagrama
            nfa_canvas_width = self.nfa_canvas.winfo_width()
            nfa_canvas_height = self.nfa_canvas.winfo_height()
            dfa_canvas_width = self.dfa_canvas.winfo_width()
            dfa_canvas_height = self.dfa_canvas.winfo_height()
            
            # Centrar vista
            if nfa_width > nfa_canvas_width:
                self.nfa_canvas.xview_moveto(0.5 - (nfa_canvas_width/2)/nfa_width)
            else:
                self.nfa_canvas.xview_moveto(0)
                
            if nfa_height > nfa_canvas_height:
                self.nfa_canvas.yview_moveto(0.5 - (nfa_canvas_height/2)/nfa_height)
            else:
                self.nfa_canvas.yview_moveto(0)
            
            if dfa_width > dfa_canvas_width:
                self.dfa_canvas.xview_moveto(0.5 - (dfa_canvas_width/2)/dfa_width)
            else:
                self.dfa_canvas.xview_moveto(0)
                
            if dfa_height > dfa_canvas_height:
                self.dfa_canvas.yview_moveto(0.5 - (dfa_canvas_height/2)/dfa_height)
            else:
                self.dfa_canvas.yview_moveto(0)
            
            # Forzar actualización final
            self.nfa_canvas.update_idletasks()
            self.dfa_canvas.update_idletasks()
            self.root.update()
    
        except Exception as e:
            print(f"Error al actualizar canvas: {str(e)}")

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RegexApp(root)
    root.mainloop()