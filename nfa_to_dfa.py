import pandas as pd
from itertools import chain, combinations
import numpy as np
import NFA
from collections import deque

def get_all_states(start):
    visited = set()
    stack = [start]
    while stack:
        current = stack.pop()
        if current not in visited:
            visited.add(current)
            for states in current.transitions.values():
                stack.extend(states)
            stack.extend(current.epsilon)
            
    return visited

def epsilon_closure(states):
    closure = set(states)
    stack = list(states)
    
    while stack:
        state = stack.pop()
        for next_state in state.epsilon:
            if next_state not in closure:
                closure.add(next_state)
                stack.append(next_state)
    return closure

def move (states, symbol):
    result = set()
    for state in states:
        if symbol in state.transitions:
            result.update(state.transitions[symbol])
    return result

def nfa_2_dfa(nfa):
    symbols = set()
    all_states = set()
    
    def collect_symbols(state):
        if state in all_states:
            return
        all_states.add(state)
        for sym, targets in state.transitions.items():
            symbols.add(sym)
            for t in targets:
                collect_symbols(t)
        for t in state.epsilon:
            collect_symbols(t)
    
    collect_symbols(nfa.start)
    symbols.discard('ε')
    
    start_closure = frozenset(epsilon_closure([nfa.start]))
    dfa_states = {start_closure: "D0"}
    dfa_transitions = {}
    queue = deque([start_closure])
    state_id = 1
    
    while queue:
        current = queue.popleft()
        dfa_transitions[current] = {}
        
        for symbol in symbols:
            next_set = epsilon_closure(move(current, symbol))
            next_set = frozenset(next_set)
            if not next_set:
                continue
            if next_set not in dfa_states:
                dfa_states[next_set] = f"D{state_id}"
                state_id += 1
                queue.append(next_set)
            dfa_transitions[current][symbol] = next_set
    
    trap_state = frozenset()
    
    if trap_state not in dfa_states:
        dfa_states[trap_state] = f"D{state_id}"
        state_id += 1
    
    
    for state in dfa_transitions:
        for symbol in symbols:
            if symbol not in dfa_transitions[state]:
                dfa_transitions[state][symbol] = trap_state
    
    dfa_transitions[trap_state] = {symbol: trap_state for symbol in symbols}
    
    dfa_accepts = {s for s in dfa_states if nfa.accept in s}
    
    return dfa_states, dfa_transitions, start_closure, dfa_accepts, symbols

def dfa_to_dot(dfa_states, dfa_transitions, start_state, accept_states):
    lines = [
        "digraph DFA {",
        "rankdir=LR;",                                 # orientación horizontal
        'node [shape=circle, fontsize=12];',           # nodos medianos
        'edge [fontsize=10];',                         # etiquetas de transiciones legibles
        'graph [dpi=450, size="12,3", ratio=fill];',   # proporción horizontal amplia
        'ranksep=0.8;',                                # separación vertical moderada
        'nodesep=0.6;',                                # separación horizontal adecuada
        'splines=true;',                               # líneas curvas suaves
        'overlap=false;',                              # evita superposición
        'concentrate=true;'                            # agrupa transiciones paralelas
    ]

    # Estados de aceptación
    for state_set in accept_states:
        lines.append(f'{dfa_states[state_set]} [shape=doublecircle];')

    # Estado inicial ficticio
    lines.append('start [shape=point];')
    lines.append(f'start -> {dfa_states[start_state]};')

    # Transiciones
    for from_state, transitions in dfa_transitions.items():
        for symbol, to_state in transitions.items():
            lines.append(f'{dfa_states[from_state]} -> {dfa_states[to_state]} [label="{symbol}"];')

    lines.append("}")
    return "\n".join(lines)
