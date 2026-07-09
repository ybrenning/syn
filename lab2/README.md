# Lab 2

Grammar sketch:

```
program -> stmt
         | program ; stmt
         | program ;

stmt -> VAR = VAR + INT
      | VAR = INT + INT
      | WHILE ( VAR != INT ) { program }
      | IF ( VAR != INT ) { program }
      | IF ( VAR != INT ) { program } ELSE { program }
```

where `VAR` matches `x\d+` (the variable index is folded into the token) and
`INT` matches `-?\d+` (a leading `-` is folded in, so a summand may be negative).

The condition is always of the form `VAR != INT`, as required by the "While
programs" definition.

I also allow a trailing separator (semicolon), since it felt more natural and similar to semicolon-based programming languages. This means a program can end with a semicolon or have to semicolons after each other, for example.

Also, I allow the first term of a sum to be a constant integer, as opposed to only variables. This just seemed like a natural/easy extension of the base grammar. Something like x0 = 1 + 1 should work instead of necessitating a helper variable.

  `x0 = 5 + -5` parse directly instead of forcing a helper variable.

I used PLY which lets me define lexer and parser within the same file. I stay with Python since it is the simplest option, the library's example was well-documented (https://www.dabeaz.com/ply/ply.html), and I already used the language in the previous task.

PLY's `yacc` generates LALR(1) parse tables, so the grammar used for parsing is LALR(1) .

Block comments are matched with a non-greedy regex so it stops at the next `*/` and can't span a nested block.

## Instructions

### Running the parser

Install the requirements:

```text
$ python3 -m venv venv
$ . venv/bin/activate
$ (venv) pip install ply
```

Run the main script on a source file:

```
$ python3 while_parser.py program.lang
```

The program first prints the token stream produced by the lexer (mainly for debugging, can be commented out). It then prints the parse tree of the source code as an indented tree. If an error occurs, a message is printed and the (incomplete) tree is not shown.

### Example

Input `program.lang`:

```
x0 = 5 + -5 ;
x1 = x0 + 3 ;
WHILE(x0 != 0) {
    x1 = x1 + 1 ;
    IF(x2 != 0) { x2 = x2 + -1 }
    ELSE { x3 = x3 + 0 }
}
```

Should produce:

```
program
|- assign
|  |- var x0
|  |- int 5
|  |_ int -5
|- assign
|  |- var x1
|  |- var x0
|  |_ int 3
|_ while
   |- cond !=
   |  |- var x0
   |  |_ int 0
   |_ body
      |_ program
         |- assign
         |  |- var x1
         |  |- var x1
         |  |_ int 1
         |_ if-else
            |- cond !=
            |  |- var x2
            |  |_ int 0
            |- then
            |  |_ program
            |     |_ assign
            |        |- var x2
            |        |- var x2
            |        |_ int -1
            |_ else
               |_ program
                  |_ assign
                     |- var x3
                     |- var x3
                     |_ int 0
```
