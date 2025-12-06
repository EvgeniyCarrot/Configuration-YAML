import sys
import yaml
from lexer import tokenize
from parser import Parser, ParseError

def main():
    if len(sys.argv) != 2:
        print("Usage: python config_parser.py <config_file>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], encoding='utf-8') as f:
        text = f.read()

    try:
        tokens = list(tokenize(text))
        print("Tokens:", tokens, file=sys.stderr) #отладка - вывод токенов 
        parser = Parser(tokens)
        result = parser.parse()
        yaml.safe_dump(result, sys.stdout, allow_unicode=True, sort_keys=False)
    except ParseError as e:
        print(f"Parse error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

