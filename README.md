# STLC
Simple typed lambda calculus with recursion in python

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

We use $\Gamma$ as a set of `variable:type` declarations .

$$\dfrac{ v:t \in \Gamma }{\Gamma \vdash v:t}$$

$$\dfrac{ }{\Gamma \vdash True :Bool}$$

$$\dfrac{ }{\Gamma \vdash False :Bool}$$

$$\dfrac{ }{\Gamma \vdash int literal :Int}$$

$$\dfrac{ }{\Gamma \vdash unit :Unit}$$

```math
\dfrac{ op \in \{+,-,*,/ \} \qquad \qquad \Gamma \vdash (e_1:Int) \qquad \qquad \Gamma \vdash (e_2:Int) }{\Gamma \vdash (e_1 \quad op \quad e_2:Int) }
```

```math
\dfrac{ op \in \{<,>,<=,>=,==\} \qquad \qquad \Gamma \vdash (e_1:Int) \qquad \qquad \Gamma \vdash (e_2:Int) }{\Gamma \vdash (e_1 \quad op \quad e_2:Bool)}
```

```math
\dfrac{ op \in \{ \& ,|,~\}  \qquad \qquad \Gamma \vdash (e_1:Bool) \qquad \qquad \Gamma \vdash (e_2:Bool)}{\Gamma \vdash (e_1 \quad op \quad e_2 : Bool)}
```

$$\dfrac{\Gamma, x : t_1 \vdash e : t_2 }{\Gamma \vdash (\textbackslash x ->  e ) : (t_1 -> t_2) }$$

$$\dfrac{\Gamma \vdash e_1 : (t_1 -> t_2)   \qquad \qquad \qquad \Gamma \vdash e_2 : t_1 }{\Gamma \vdash ( e_1 \quad e_2 ) : t_2 }$$

$$\dfrac{\Gamma \vdash e_1 : Bool \qquad \qquad \Gamma \vdash e_2 : t \qquad \qquad \Gamma \vdash e_3 : t  }{\Gamma \vdash (if \quad e_1 \quad then \quad e_2 \quad else \quad e_3) : t }$$

$$\dfrac{\Gamma \vdash (e:t) }{\Gamma \vdash ((e:t):t) }$$


## Free variables

```math
Free(x) = \{x\}
```

$$Free(literal) = \emptyset$$

$$Free((e_1 e_2)) = Free(e_1) \cup Free(e_2)$$

```math
Free(\textbackslash x -> e ) = Free(e) \textbackslash \{x\}
```

$$Free(e_1 op e_2) = Free(e_1) \cup Free(e_2)$$

$$Free(if \quad e_1 \quad then \quad e_2 \quad else \quad e_3) = Free(e_1) \cup Free(e_2) \cup Free(e_3)$$


## Substitution

- $x[x := r] = r$

- $y[x := r] = y$ if $x \neq y$ 

- $(e_1 \quad e_2)[x:=r] = ((e_1[ x:= r])(e_2[x:=r]))$

- $(\textbackslash x -> e)[x:=r] = (\textbackslash x->e)$

- $(\textbackslash y -> e)[x:=r] = (\textbackslash y -> (e[y:=z])[x:=r])$ provided $x \neq y$ and $z \notin Free(e)$

- $(e_1 \quad op \quad e_2)[x:=r] = ((e_1[x:=r]) \quad op \quad (e_2[x:=r]))$

- $(if \quad e_1 \quad then \quad e_2 \quad else \quad e_3)[x:=r] = if e_1[x:=r] then e_2[x:=r] else e_3[x:=r]$


## Evaluation rules

Let $E$ be a set of definitions `variable = expression`. 

$V$ denotes the set of values, this means that it contains `True,False,unit,0,1,-1,-2,...`, lambda expressions of the form `\ x -> e` and operator expressions `v_1 op v_2` where $v_1,v_2 \in V$ .

$$\dfrac{}{(True,E) => (True,E)}$$

$$\dfrac{}{(False,E) => (False,E)}$$

$$\dfrac{}{(int literal,E) => (int literal,E)}$$

$$\dfrac{}{(unit,E) => (unit,E)}$$

$$\dfrac{}{(\ x -> e,E) => (\ x -> e,E)}$$

$$\dfrac{(x=e) \in E }{(x,E) => (e,E)}$$

$$\dfrac{(y,E) => (e,E)}{(x \quad y,E) => (x \quad e,E)}$$

$$\dfrac{v \in V \qquad (x=\ y -> e) \in E}{(x \quad v,E) => (e[y:=v],E)}$$

$$\dfrac{(x,E) => (e,E)}{((x \quad op \quad y),E) => (e \quad op \quad y,E)}$$

$$\dfrac{v \in V \qquad (y,E) => (e,E)}{((v \quad op \quad y),E) => (v \quad op \quad e,E)}$$

$$\dfrac{(e_1,E) => (e_4 ,E)}{(if \quad e_1 \quad then \quad e_2 \quad else \quad e_3, E) =>(if \quad e_4 \quad then \quad e_2 \quad else \quad e_3, E) }$$

$$\dfrac{}{(if \quad True \quad then \quad e_2 \quad else \quad e_3, E) =>(e_2, E) }$$

$$\dfrac{}{(if \quad False \quad then \quad e_2 \quad else \quad e_3, E) =>(e_3, E) }$$
