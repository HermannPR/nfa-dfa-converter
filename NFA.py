import postfix
def nfa_to_dot(nfa):
    state_ids = {}
    counter = [0]

    def get_id(state):
        if state not in state_ids:
            state_ids[state] = f"S{counter[0]}"
            counter[0] += 1
        return state_ids[state]

    visited = set()
    lines = ["digraph NFA {", "rankdir=LR;", 'node [shape=circle];']

    def visit(state):
        if state in visited:
            return
        visited.add(state)

        sid = get_id(state)
        if state == nfa.accept:
            lines.append(f'{sid} [shape=doublecircle];')

        for symbol, targets in state.transitions.items():
            for t in targets:
                tid = get_id(t)
                lines.append(f'{sid} -> {tid} [label="{symbol}"];')

        for target in state.epsilon:
            tid = get_id(target)
            lines.append(f'{sid} -> {tid} [label="ε"];')

        for t in state.transitions.values():
            for next_state in t:
                visit(next_state)
        for e in state.epsilon:
            visit(e)

    lines.append(f'start [shape=point];')
    lines.append(f'start -> {get_id(nfa.start)};')

    visit(nfa.start)
    lines.append("}")
    return "\n".join(lines)

class state:
    def __init__(self):
        self.transitions = {}
        self.epsilon = []
    
class NFA:
    def __init__(self, start, accept):
        self.start = start
        self.accept = accept

def build_nfa(postfix):
    stack =  []
    
    for char in postfix:
        if char.isalnum():
            start = state()
            accept = state()
            start.transitions[char] = [accept]
            stack.append(NFA(start, accept))
        
        elif char == '*':
            nfa = stack.pop()
            start = state()
            accept = state()
            start.epsilon.append(nfa.start)
            start.epsilon.append(accept)
            nfa.accept.epsilon.append(nfa.start)
            nfa.accept.epsilon.append(accept)
            stack.append(NFA(start, accept))
            
        elif char == '.':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            nfa1.accept.epsilon.append(nfa2.start)
            stack.append(NFA(nfa1.start, nfa2.accept))
        
        elif char == '+':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            start = state()
            accept = state()
            start.epsilon.append(nfa1.start)
            start.epsilon.append(nfa2.start)
            nfa1.accept.epsilon.append(accept)
            nfa2.accept.epsilon.append(accept)
            stack.append(NFA(start, accept))

    return stack.pop()
def epsilon_closure(state, visited=None):
    """Calcula el cierre epsilon de un estado"""
    if visited is None:
        visited = set()
    
    if state in visited:
        return visited
    
    visited.add(state)
    for next_state in state.epsilon:
        epsilon_closure(next_state, visited)
    
    return visited

def simulate_nfa(nfa, input_string):
    """Simula el NFA con una cadena de entrada"""
    current_states = epsilon_closure(nfa.start)
    
    for symbol in input_string:
        next_states = set()
        for state in current_states:
            if symbol in state.transitions:
                for next_state in state.transitions[symbol]:
                    next_states.update(epsilon_closure(next_state))
        
        current_states = next_states
        if not current_states:  # Si no hay estados a los que transitar
            return False
    
    # Verificar si algún estado actual es de aceptación
    return any(state == nfa.accept for state in current_states)