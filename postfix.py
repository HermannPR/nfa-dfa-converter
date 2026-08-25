def add_concatenation(exp):
    result = ""
    for i in range(len(exp)):
        result += exp[i]
        if i + 1 < len(exp):
            if (exp[i].isalnum() or exp[i] == ')' or exp[i] == '*') and (exp[i+1].isalnum() or exp[i+1] == '('):
                result += '.'
    return result

def precedence(op):
    return {"*":3, ".":2, "+":1}.get(op, 0)

def infix_to_postfix(expression):
    output = ""
    stack = []
    for char in expression:
        if char.isalnum():
            output += char
        elif char == "(":
            stack.append(char)
        elif char == ")":
            while stack and stack[-1] != "(":
                output += stack.pop()
            stack.pop()
        else:
            while stack and stack[-1] != "(" and precedence(char) <= precedence(stack[-1]):
                output += stack.pop()
            stack.append(char)
            
    while stack:
        output += stack.pop()
    
    return output

