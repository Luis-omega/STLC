# Language Spec

## Gammar for core language

```ebnf
expression : variable
    | literal 
    | "(" expression expression ")"
    |"\" variable "->"  expression
    | "(" expression operator expression ")"
    | "if" expression "then" expression "else" expression

variable_character : "a" | ... | "z" | "A" | ... | "Z"
variable : "_" variable_character+ | variable_character+

literal : bool_literal | int_literal | "unit"

bool_literal : True | False

int_literal : 0 | 1 | -1 | 2 | -2 | ...

operator: "+" | "-" | "*" | "/" | "<" | ">" | "<=" | ">=" | "==" | "&" | "|" |"~"

type : "Bool" | "Int" | "Unit" | "(" type "->" type ")"

variable_definition : variable "=" expression
variable_declaration : variable ":" type
```

## Factorized Grammar for expression

```ebnf
expression : variable
    | literal 
    | "(" expression expression_paren
    |"\" variable "->"  expression
    | "if" expression "then" expression "else" expression

expression_paren :  expression ")"
    | operator expression ")"
    | ":" type ")"
```

## Typing rules 

We use $\Gamma$ as a set of "x:t" .

$$\dfrac{ v:t \in \Gamma }{\Gamma \vdash v:t}$$

$$\dfrac{ }{\Gamma \vdash True :Bool}$$

$$\dfrac{ }{\Gamma \vdash False :Bool}$$

$$\dfrac{ }{\Gamma \vdash int literal :Int}$$

$$\dfrac{ }{\Gamma \vdash unit :Unit}$$

$$\dfrac{ op \in \{+,-,*,/ \} }{\Gamma \vdash op : (Int ->Int->Int) }$$

$$\dfrac{ op \in \{<,>,<=,>=,==\} }{\Gamma \vdash op : (Int->Int->Bool)}$$

```math
\dfrac{ op \in \{ \& ,|,~\} }{\Gamma \vdash op : (Bool->Bool->Bool)}
```

$$\dfrac{\Gamma, x : t_1 \vdash e : t_2 }{\Gamma (\vdash x ->  e ) : (t_1 -> t_2) }$$

$$\dfrac{\Gamma \vdash e_1 : (t_1 -> t_2)   \qquad \qquad \qquad \Gamma \vdash e_2 : t_1 }{\Gamma \vdash ( e_1 e_2 ) : t_2 }$$

$$\dfrac{\Gamma \vdash e_1 : Bool \qquad \qquad \Gamma \vdash e_2 : t \qquad \qquad \Gamma \vdash e_3 : t  }{\Gamma \vdash (if e_1 then e_2 else e_3) : t }$$

$$\dfrac{\Gamma \vdash (e:t) }{\Gamma \vdash ((e:t):t) }$$


## Evaluation rules
TODO

$$\dfrac{}{True => True}$$

$$\dfrac{}{False => False}$$

$$\dfrac{}{int literal => int literal}$$

$$\dfrac{}{unit => unit}$$

$$\dfrac{Env[x := y]}{x => y}$$

