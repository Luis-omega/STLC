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

$$\dfrac{\Gamma, x : t_1 \vdash e : t_2 }{\Gamma \vdash (\textbackslash x ->  e ) : (t_1 -> t_2) }$$

$$\dfrac{\Gamma \vdash e_1 : (t_1 -> t_2)   \qquad \qquad \qquad \Gamma \vdash e_2 : t_1 }{\Gamma \vdash ( e_1 e_2 ) : t_2 }$$

$$\dfrac{\Gamma \vdash e_1 : Bool \qquad \qquad \Gamma \vdash e_2 : t \qquad \qquad \Gamma \vdash e_3 : t  }{\Gamma \vdash (if e_1 then e_2 else e_3) : t }$$

$$\dfrac{\Gamma \vdash (e:t) }{\Gamma \vdash ((e:t):t) }$$


## Free variables

$$Free(x) = \{ x \}$$

$$Free(literal) = \emptyset$$

$$Free((e_1 e_2)) = Free(e_1) \cup Free(e_2)$$

$$Free(\textbackslash x -> e ) = Free(e) \textbackslash \{ x \}$$

$$Free(e_1 op e_2) = Free(e_1) \cup Free(e_2)$$

$$Free(if e_1 then e_2 else e_3) = Free(e_1) \cup Free(e_2) \cup Free(e_3)$$


## Substitution

- $x[x := r] = r$

- $y[x := r] = y$ if $x \neq y$ 

- $(e_1 e_2)[x:=r] = ((e_1[ x:= r])(e_2[x:=r]))$

- $(\textbackslash x -> e)[x:=r] = (\textbackslash x->e)$

- $(\textbackslash y -> e)[x:=r] = (\textbackslash y -> (e[y:=z])[x:=r])$ provided $x \neq y$ and $z \notin Free(e)$

- $(e_1 op e_2)[x:=r] = ((e_1[x:=r]) op (e_2[x:=r]))$

- $(if e_1 then e_2 else e_3)[x:=r] = if e_1[x:=r] then e_2[x:=r] else e_3[x:=r]$


## Evaluation rules

Let $E$ be a set of definitions `variable = expression`. 

We would assume that for every $(x = e) \in E$ the $Free(x)$ are all defined in $E$. 

Let $E[x]$ denote that $x$ is defined in $E$ with definition $E[x]$.

$V$ denotes the set of values, this means that it contains `True,False,unit,0,1,-1,-2,...`, lambda expressions of the form `\ x -> e` and operator expressions `v_1 op v_2` where $v_1,v_2 \in V$ .

$$\dfrac{}{(True,E) => (True,E)}$$

$$\dfrac{}{(False,E) => (False,E)}$$

$$\dfrac{}{(int literal,E) => (int literal,E)}$$

$$\dfrac{}{(unit,E) => (unit,E)}$$

$$\dfrac{}{(\ x -> e,E) => (\ x -> e,E)}$$

$$\dfrac{(x=e) \in E }{(x,E) => (e,E)}$$

$$\dfrac{(y,E) => (e,E)}{(x y,E) => (x e,E)}$$

$$\dfrac{v \in V \qquad (x=\ y -> e) \in E}{(x v,E) => (e[y:=v],E)}$$

$$\dfrac{(x,E) => (e,E)}{((x op y),E) => (e op y,E)}$$

$$\dfrac{v \in V \qquad (y,E) => (e,E)}{((v op y),E) => (v op e,E)}$$

$$\dfrac{(e_1,E) => (e_4 ,E)}{(if e_1 then e_2 else e_3, E) =>(if e_4 then e_2 else e_3, E) }$$

$$\dfrac{}{(if True then e_2 else e_3, E) =>(e_2, E) }$$

$$\dfrac{}{(if False then e_2 else e_3, E) =>(e_3, E) }$$
