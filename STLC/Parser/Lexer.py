from dataclasses import dataclass
from typing import Optional,TypeVar,Callable

T = TypeVar("T")

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

boolTrue = lambda stream: string(stream,"True",TokenBool(True))
boolFalse = lambda stream: string(stream,"False",TokenBool(False))
rparen = lambda stream: string(stream,"(",RParen())
lparen = lambda stream: string(stream,")",LParen())
lambdaStart = lambda stream: string(stream,"\\",LambdaStart())
arrow = lambda stream: string(stream,"->",Arrow())
if_ = lambda stream: string(stream,"if",If())
else_ = lambda stream: string(stream,"else",Else())
then = lambda stream: string(stream,"then",Then())
colon = lambda stream: string(stream,":",Colon())
boolType = lambda stream: string(stream,"Bool",TokenTypeBool())
intType = lambda stream: string(stream,"Int",TokenTypeInt())
unitType = lambda stream: string(stream,"Unit",TokenTypeUnit())
equal = lambda stream: string(stream,"=",Equal())
 
# TODO: Implement `one of` and use it to define the lexer
