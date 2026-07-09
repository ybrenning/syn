import sys
import ply.lex as lex
import ply.yacc as yacc


tokens = (
    'WHILE', 'IF', 'ELSE',
    'VAR', 'INT',
    'ASSIGN', 'PLUS', 'NEQ',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'SEMI',
)

t_ASSIGN = r'='
t_PLUS   = r'\+'
t_NEQ    = r'!='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_SEMI   = r';'

t_WHILE = r'WHILE'
t_IF    = r'IF'
t_ELSE  = r'ELSE'

def t_COMMENT_BLOCK(t):
    # NO NESTING
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')

def t_COMMENT_INLINE(t):
    r'//[^\n]*'

def t_VAR(t):
    r'x\d+'
    return t

def t_INT(t):
    r'-?\d+'
    t.value = int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'

def t_error(t):
    print("Illegal character %r on line %d" % (t.value[0], t.lexer.lineno))
    t.lexer.skip(1)


class Node:
    def __init__(self, type, children=None, leaf=None):
        self.type = type
        if children:
            self.children = children
        else:
            self.children = []
        self.leaf = leaf

def print_tree(node, prefix='', is_root=True, is_last=True):
    label = node.type if node.leaf is None else "%s %s" % (node.type, node.leaf)
    if is_root:
        print(label)
    else:
        print(prefix + ('|_ ' if is_last else '|- ') + label)
        prefix += '   ' if is_last else '|  '
    for i, child in enumerate(node.children):
        print_tree(
            child, prefix, False, i == len(node.children) - 1
        )


def p_program_single(p):
    'program : stmt'
    p[0] = Node("program", [p[1]])

def p_program_seq(p):
    'program : program SEMI stmt'
    p[1].children.append(p[3])
    p[0] = p[1]

def p_program_trailing(p):
    'program : program SEMI'
    p[0] = p[1]

def p_stmt_assign(p):
    'stmt : VAR ASSIGN VAR PLUS INT'
    p[0] = Node("assign", [
        Node("var", leaf=p[1]),
        Node("var", leaf=p[3]),
        Node("int", leaf=p[5]),
    ])

def p_stmt_assign_const(p):
    'stmt : VAR ASSIGN INT PLUS INT'
    p[0] = Node("assign", [
        Node("var", leaf=p[1]),
        Node("int", leaf=p[3]),
        Node("int", leaf=p[5]),
    ])

def p_stmt_while(p):
    'stmt : WHILE LPAREN VAR NEQ INT RPAREN LBRACE program RBRACE'
    cond = Node("cond", [Node("var", leaf=p[3]), Node("int", leaf=p[5])], leaf="!=")
    p[0] = Node("while", [cond, Node("body", [p[8]])])

def p_stmt_if(p):
    'stmt : IF LPAREN VAR NEQ INT RPAREN LBRACE program RBRACE'
    cond = Node("cond", [Node("var", leaf=p[3]), Node("int", leaf=p[5])], leaf="!=")
    p[0] = Node("if", [cond, Node("then", [p[8]])])

def p_stmt_ifelse(p):
    'stmt : IF LPAREN VAR NEQ INT RPAREN LBRACE program RBRACE ELSE LBRACE program RBRACE'
    cond = Node("cond", [Node("var", leaf=p[3]), Node("int", leaf=p[5])], leaf="!=")
    p[0] = Node("if-else", [cond, Node("then", [p[8]]), Node("else", [p[12]])])

# Don't print the incomplete tree
error_occurred = False

def p_error(p):
    global error_occurred
    error_occurred = True
    if p:
        print("Syntax error at %r (line %d)" % (p.value, p.lineno))
    else:
        print("Syntax error at end of input")


if __name__ == '__main__':
    src = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()

    lexer = lex.lex()

    # Look at the lexer
    print("Lexer Tokens:")
    lexer.input(src)
    for tok in lexer:
        print(tok)

    parser = yacc.yacc()
    tree = parser.parse(src, lexer=lexer)

    print("\nParse Tree:")
    if tree and not error_occurred:
        print_tree(tree)
