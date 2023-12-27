I am trying to implement C parser within pure LR(1).
I want to find a balance point:
support C11 syntax as much as I can, while still stay in CFG.

Currently limitations:

* identifier is type iff starts with upper case letter,

* typedef not allowed(use defines)

* struct/union definition must be top level block and must use typedef syntax.

* enum not allowed

* comma(Expr15) not allowed in
init declare(x = {a, (b, c), d}) and
function call(Params directly goto Expr14)

* a very restricted preprocessing

* struct init only use designated
