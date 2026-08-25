import postfix
import NFA
import os
from NFA import nfa_to_dot
from nfa_to_dfa import nfa_2_dfa
from nfa_to_dfa import dfa_to_dot

if __name__ == "__main__":
    
    infix = "a*b+c"
    with_concatenation = postfix.add_concatenation(infix)
    postfix_exp = postfix.infix_to_postfix(with_concatenation)
    nfaa = NFA.build_nfa(postfix_exp)
    dot_code = nfa_to_dot(nfaa)
    
    with open("nfaa.dot", "w", encoding="UTF-8") as f:
        f.write(dot_code)
        
    os.system("dot -Tpng nfaa.dot -o nfaa.png")
    
    # Convertir NFA a DFA
    dfa_states, dfa_transitions, start, accept_states, symbols = nfa_2_dfa(nfaa)
    dotdfa = dfa_to_dot(dfa_states, dfa_transitions, start, accept_states)
    with open("dfa.dot", "w", encoding="UTF-8") as f:
        f.write(dotdfa)
        
    os.system("dot -Tpng dfa.dot -o dfa.png")

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
        self.display_nfa_image(self.nfa_image_path)

        # Generar DFA a partir del NFA
        dfa_states, dfa_transitions, start, accept_states, symbols = nfa_2_dfa(self.current_nfa)
        dfa_dot_code = dfa_to_dot(dfa_states, dfa_transitions, start, accept_states)

        with open("dfa.dot", "w", encoding="UTF-8") as f:
            f.write(dfa_dot_code)

        os.system("dot -Tpng dfa.dot -o dfa.png")
        self.dfa_image_path = "dfa.png"  # Guardar la ruta del DFA

        # Asegurar que el canvas del DFA esté listo para mostrar la imagen
        self.dfa_canvas.delete("all")
        self.display_dfa_image(self.dfa_image_path)

        # Resetear zoom para ambas imágenes
        self.reset_zoom_nfa()
        self.reset_zoom_dfa()

        self.result_text.insert(tk.END, "¡Autómatas generados con éxito!\n")
        self.result_text.config(state=tk.DISABLED)

    except Exception as e:
        messagebox.showerror("Error", f"Error al generar el autómata: {str(e)}")