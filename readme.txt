I am trying to implement C parser within pure LR(1).
A lot of restrictions are applied(without harming expressivity though):

* types must be CamelCase, var must be snake_case,
typedef of simple types ([struct/union/enum] T) is the only exception.

* all procedures must be surrounded by braces(avoid dangling else)
