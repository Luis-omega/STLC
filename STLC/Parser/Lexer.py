from dataclasses import dataclass
from typing import Optional,TypeVar,Callable,Union

T = TypeVar("T")

Token = Union[
    "TokenVariable",
    "TokenBool",
    "TokenInt",
    "TokenUnit",
    "LParen",
    "RParen",
    "LambdaStart",
    "Arrow",
    "If",
    "Then",
    "Else",
    "Colon",
    "Operator",
    "Equal",
    "TokenTypeBool",
    "TokenTypeInt",
    "TokenTypeUnit",
    "TokenEOF",
    "TokenError",
        ]

@dataclass
class TokenVariable:
    name : str

@dataclass
class TokenBool:
    value: bool

@dataclass
class TokenInt:
    value : int

@dataclass 
class TokenUnit:
    pass

@dataclass
class LParen:
    pass

@dataclass
class RParen:
    pass

@dataclass
class LambdaStart:
    pass

@dataclass
class Arrow:
    pass

@dataclass
class If:
    pass

@dataclass
class Then:
    pass

@dataclass
class Else:
    pass

@dataclass
class Colon:
    pass

@dataclass
class Operator:
    value : str

@dataclass
class TokenTypeBool:
    pass

@dataclass
class TokenTypeInt:
    pass
    
@dataclass
class TokenTypeUnit:
    pass

@dataclass
class Equal:
    pass

@dataclass
class TokenEOF:
    pass

@dataclass
class TokenError:
    msg: str

def is_variable_char(stream:str)->bool:
    match stream:
        case "" :
            return False
        case _ :
            char = stream[0]
            return ("a"<= char and char <= "z") or ("A" <=char and char <="Z")

def variable(stream:str)->Optional[tuple[str,TokenVariable]]:
    match stream :
        case "" :
            return None
        case _ :
            if is_variable_char(stream[0]) or stream[0]=="_" :
                acc = [stream[0]]
                stream = stream[1:]
                while (stream and is_variable_char(stream[0])) :
                    acc.append(stream[0])
                    stream = stream[1:]
                return (stream,TokenVariable("".join(acc)))
            else:
                return None

def is_non_zero_digit(stream:str)->bool:
    match stream:
        case "": 
            return False
        case _ :
            char = stream[0]
            return "1"<=char and char <= "9" 

def is_zero_digit(stream:str)->bool:
    match stream:
        case "": 
            return False
        case _ :
            char = stream[0]
            return char=="0"

def is_digit(stream:str)->bool:
    match stream:
        case "": 
            return False
        case _ :
            char = stream[0]
            return is_non_zero_digit(char) or is_zero_digit(char)


def uint(stream:str)->Optional[tuple[str,int]]:
    match stream :
        case "" :
            return None
        case _ :
            if is_non_zero_digit(stream[0]):
                acc = [stream[0]]
                stream = stream[1:]
                while (stream and is_digit(stream[0])) :
                    acc.append(stream[0])
                    stream = stream[1:]
                return (stream,(int("".join(acc))))
            elif is_zero_digit(stream[0]):
                return (stream[1:],0)
            else:
                return None

def int_(stream:str)->Optional[tuple[str,TokenInt]]:
    match stream :
        case "" :
            return None
        case _ :
            char = stream[0]
            if char == "-":
                maybe_value = uint(stream[1:])
                if maybe_value is None:
                    return None
                else:
                    (new_stream,value) = maybe_value
                    return (new_stream,TokenInt(-value))
            else:
                maybe_value = uint(stream)
                if maybe_value is None:
                    return None
                else:
                    (new_stream,value) = maybe_value
                    return (new_stream,TokenInt(value))

def string(stream:str,to_lex:str,value:T)->Optional[tuple[str,T]]:
    match stream :
        case "" :
            return None
        case _:
            if stream.startswith(to_lex):
                return (stream[len(to_lex):],value)
            else:
                return None

def string_with(stream:str,to_lex:str,get_value:Callable[[str],T])->Optional[tuple[str,T]]:
    match stream :
        case "" :
            return None
        case _:
            if stream.startswith(to_lex):
                return (stream[len(to_lex):],get_value(stream[:len(to_lex)]))
            else:
                return None
            
def operator(stream:str)->Optional[tuple[str,Operator]]:
    for op in ["+","-","*","/","<=" , ">=","<", ">"  , "==" , "&" , "|" ,"~"]:
        maybe_lexed = string_with(stream,op,Operator)
        if maybe_lexed is not None:
            return maybe_lexed
    return None

boolTrue:Callable[[str],Optional[tuple[str,Token]]] = lambda stream: string(stream,"True",TokenBool(True))
boolFalse:Callable[[str],Optional[tuple[str,Token]]] = lambda stream: string(stream,"False",TokenBool(False))
unit:Callable[[str],Optional[tuple[str,Token]]] = lambda stream: string(stream,"unit",TokenUnit())
rparen:Callable[[str],Optional[tuple[str,Token]]] = lambda stream: string(stream,"(",RParen())
lparen:Callable[[str],Optional[tuple[str,Token]]] = lambda stream: string(stream,")",LParen())
lambdaStart:Callable[[str],Optional[tuple[str,Token]]] = lambda stream: string(stream,"\\",LambdaStart())
arrow:Callable[[str],Optional[tuple[str,Token]]] = lambda stream: string(stream,"->",Arrow())
if_:Callable[[str],Optional[tuple[str,Token]]] = lambda stream: string(stream,"if",If())
else_:Callable[[str],Optional[tuple[str,Token]]] = lambda stream: string(stream,"else",Else())
then:Callable[[str],Optional[tuple[str,Token]]] = lambda stream: string(stream,"then",Then())
colon:Callable[[str],Optional[tuple[str,Token]]] = lambda stream: string(stream,":",Colon())
boolType:Callable[[str],Optional[tuple[str,Token]]] = lambda stream: string(stream,"Bool",TokenTypeBool())
intType:Callable[[str],Optional[tuple[str,Token]]] = lambda stream: string(stream,"Int",TokenTypeInt())
unitType:Callable[[str],Optional[tuple[str,Token]]] = lambda stream: string(stream,"Unit",TokenTypeUnit())
equal:Callable[[str],Optional[tuple[str,Token]]] = lambda stream: string(stream,"=",Equal())
 

def spaces(stream:str)->str:
    while (stream and stream[0]==" "):
        stream = stream[1:]
    return stream


def one_of(stream:str,functions:list[Callable[[str],Optional[tuple[str,Token]]]])->Optional[tuple[str,Token]]:
    match functions:
        case [] : 
            return None
        case _ :
            for f in functions:
                result = f(stream)
                if result is not None:
                    return result
            return None

def lexer(stream:str)->list[Token]:
    lexers : list[Callable[[str],Optional[tuple[str,Token]]]] = [
        boolTrue,
        boolFalse,
        unit,
        rparen,
        lparen,
        lambdaStart,
        arrow,
        if_,
        else_,
        then,
        colon,
        boolType,
        intType,
        unitType,
        equal,
        variable,
        int_,
        operator
            ]
    acc : list[Token] = []
    while stream :
        result = one_of(stream,lexers)
        if result is None:
            if len(stream)>0:
                acc.append(TokenError(stream[0]))
            else:
                acc.append(TokenEOF())
            break
        else :
            stream,value = result 
            acc.append(value)
            stream = spaces(stream)
    if len(acc)==0:
        return [TokenEOF()]
    return acc

print(lexer("\\ x -> x +1 * unit Int Bool "))

