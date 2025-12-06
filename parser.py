from typing import Any, Dict, List, Tuple
from lexer import tokenize

class ParseError(Exception):
    def __init__(self, msg: str, pos: int):
        super().__init__(f"{msg} at position {pos}")
        self.pos = pos

class Parser:
    def __init__(self, tokens: List[Tuple[str, str, int]]):
        self.tokens = tokens
        self.pos = 0
        self.constants: Dict[str, Any] = {}

    def peek(self, offset=0):
        if self.pos + offset >= len(self.tokens):
            return None, None, None
        return self.tokens[self.pos + offset]
    
    def consume(self, expected_kind=None):
        kind, value, pos = self.peek()
        if expected_kind and kind != expected_kind:
            raise ParseError(f"Expected {expected_kind}, got {kind}", pos)
        self.pos += 1
        return value

    def parse(self) -> Dict[str, Any]:
        config = {}
        while self.pos < len(self.tokens):
            name = self.consume('NAME')
            self.consume('IS')
            value = self.parse_value()
            config[name] = value
            self.constants[name] = value
        return config
    
    def parse_value(self):
        kind, value, pos = self.peek()
        if kind == 'NUMBER':
            self.consume()
            if '.' in value or 'e' in value.lower():
                return float(value)
            else:
                return int(value)
        elif kind == 'QSTRING':
            return self.consume('QSTRING')
        elif kind == 'LBRACE':
            return self.parse_array()
        elif kind == 'QUESTION':
            self.consume('QUESTION')
            if self.peek()[0] != 'LBRACK':
                raise ParseError("Expected '[' after '?'", pos)
            return self.eval_expression()
        elif kind == 'NAME':
            return self.consume('NAME')
        else:
            raise ParseError(f"Unexpected token {kind}", pos)
    
    def parse_array(self):
        self.consume('LBRACE')
        items = []
        while True:
            kind, _, _ = self.peek()
            if kind == 'RBRACE':
                break
            items.append(self.parse_value())
            if self.peek()[0] == 'RBRACE':
                break
            self.consume('DOT')
        self.consume('RBRACE')
        return items
    
    def eval_expression(self):
        self.consume('LBRACK')
        op_or_func = self.consume()
        args = []
        while self.peek()[0] != 'RBRACK':
            args.append(self.parse_value())
        self.consume('RBRACK')

        if op_or_func in ('+', '-', '*', '/'):
            if len(args) != 2:
                raise ParseError(f"Binary operator {op_or_func} expects 2 args", -1)
            a, b = args
            a = self.resolve_const(a)
            b = self.resolve_const(b)
            if op_or_func == '+': return a + b
            if op_or_func == '-': return a - b
            if op_or_func == '*': return a * b
            if op_or_func == '/': return a / b
        elif op_or_func == 'len':
            if len(args) != 1:
                raise ParseError("len expects 1 arg", -1)
            arg = self.resolve_const(args[0])
            return len(arg)
        elif op_or_func == 'mod':
            if len(args) != 2:
                raise ParseError("mod expects 2 args", -1)
            a, b = args
            a = self.resolve_const(a)
            b = self.resolve_const(b)
            return a % b
        else:
            raise ParseError(f"Unknown op/func {op_or_func}", -1)
    
    def resolve_const(self, val):
        if isinstance(val, str) and val in self.constants:
            return self.constants[val]
        return val