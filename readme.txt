I am trying to implement C parser within pure LR(1).
A lot of restrictions are applied(without harming expressivity though):

* Function pointer type must be typedef-ed, instead of directly use in types.

* to handle * ambiguity, `a*` as multiplication
is not allowed to appear at begin of statement (handled during lexing)

* all procedures must be surrounded by braces.

* comma and tenary operators are not allowed.

However, it is not finished because of a really troublesome case of ambiguity:

`foo(*p)[10]` interpreted as function call returning pointer,
or declaration when foo is type.

The clean solution is to identify type vs var in lexer stage,
by enforcing CamelCase naming for custom types.
Types in external libraries are scanned or manually provided.
Then we can also solve the * ambiguity.
