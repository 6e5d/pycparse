I am trying to implement C parser within pure LR(1).
A lot of restrictions are applied(without harming expressivity though):

* types must be CamelCase, var must be snake_case,
typedef of simple types ([struct/union/enum] T) is the only exception.

* all procedures must be surrounded by braces(avoid dangling else)

* ?: and ,(as operator) are not allowed

* static variable is not allowed

* global variable is not allowed

* only use // comment, only as independent line

* multiline string(backslash) is not allowed. use `"str1"\n"str2"`

* always use parenthese for sizeof
