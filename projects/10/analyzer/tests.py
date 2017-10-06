from unittest import TestCase
from mock import patch

from tokenizer import tokenize, Token
from jack_parser import Parser
from constants import KEYWORDS, SYMBOLS

class TestParser(TestCase):

    @staticmethod
    def _dummy_parse(self):
        self.idx += 1
        return Token('dummy', 'dummy')


    def test_class_no_body(self):
        tokens = (
            Token('keyword', 'class'), 
            Token('identifier', 'Main'), 
            Token('symbol', '{'),
            Token('symbol', '}'),
        )

        expected = Token('class', [
                Token('keyword', 'class'), 
                Token('identifier', 'Main'), 
                Token('symbol', '{'),
                Token('symbol', '}'),
        ])

        actual = Parser(tokens).parse_class()
        self.assertEqual(expected, actual)

    @patch('jack_parser.Parser.parse_class_var_declaration', autospec=True)
    def test_class_with_body(self, mock_parse):
        tokens = (
            Token('keyword', 'class'), 
            Token('identifier', 'Main'), 
            Token('symbol', '{'),
            Token('keyword', 'static'),
            Token('symbol', '}'),
        )

        expected = Token('class', [
                Token('keyword', 'class'), 
                Token('identifier', 'Main'), 
                Token('dummy', 'dummy'),
                Token('symbol', '{'),
                Token('symbol', '}'),
        ])

        parser = Parser(tokens)

        mock_parse = self._dummy_parse(parser)

        actual = parser.parse_class()
        self.assertEqual(expected, actual)

    def test_class_no_body(self):
        tokens = (
            Token('keyword', 'class'), 
            Token('identifier', 'Main'), 
            Token('symbol', '{'),
            Token('symbol', '}'),
        )

        expected = Token('class', [
                Token('keyword', 'class'), 
                Token('identifier', 'Main'), 
                Token('symbol', '{'),
                Token('symbol', '}'),
        ])

        actual = Parser(tokens).parse_class()
        self.assertEqual(expected, actual)
            
class TestTokenizer(TestCase):
    maxDiff = None
    def test_tokenize(self):
        jack_text = """
        class Main {
            static boolean test;    // Added for testing -- there is no static keyword
                                    // in the Square files.
            function void main() {
              var SquareGame game;
              let game = SquareGame.new();
              do game.run();
              do game.dispose();
              return;
            }

            function void test() {  // Added to test Jack syntax that is not use in
                var int i, j;       // the Square files.
                var String s;
                var Array a;
                if (false) {
                    let s = "string constant";
                    let s = null;
                    let a[1] = a[2];
                }
                else {              // There is no else keyword in the Square files.
                    let i = i * (-j);
                    let j = j / (-2);   // note: unary negate constant 2
                    let i = i | j;
                }
                return;
            }
        }
        """
        actual = tokenize(jack_text)
        expected = [
            Token('keyword', 'class'), 
            Token('identifier', 'Main'), 
            Token('symbol', '{'),
            Token('keyword', 'static'),
            Token('keyword', 'boolean'),
            Token('identifier', 'test'),
            Token('symbol', ';'),
            Token('keyword', 'function'),
            Token('keyword', 'void'),
            Token('identifier', 'main'),
            Token('symbol', '('),
            Token('symbol', ')'),
            Token('symbol', '{'),
            Token('keyword', 'var'),
            Token('identifier', 'SquareGame'),
            Token('identifier', 'game'),
            Token('symbol', ';'),
            Token('keyword', 'let'),
            Token('identifier', 'game'),
            Token('symbol', '='),
            Token('identifier', 'SquareGame'),
            Token('symbol', '.'),
            Token('identifier', 'new'),
            Token('symbol', '('),
            Token('symbol', ')'),
            Token('symbol', ';'),
            Token('keyword', 'do'),
            Token('identifier', 'game'),
            Token('symbol', '.'),
            Token('identifier', 'run'),
            Token('symbol', '('),
            Token('symbol', ')'),
            Token('symbol', ';'),
            Token('keyword', 'do'),
            Token('identifier', 'game'),
            Token('symbol', '.'),
            Token('identifier', 'dispose'),
            Token('symbol', '('),
            Token('symbol', ')'),
            Token('symbol', ';'),
            Token('keyword', 'return'),
            Token('symbol', ';'),
            Token('symbol', '}'),
            Token('keyword', 'function'),
            Token('keyword', 'void'),
            Token('identifier', 'test'),
            Token('symbol', '('),
            Token('symbol', ')'),
            Token('symbol', '{'),
            Token('keyword', 'var'),
            Token('keyword', 'int'),
            Token('identifier', 'i'),
            Token('symbol', ','),
            Token('identifier', 'j'),
            Token('symbol', ';'),
            Token('keyword', 'var'),
            Token('identifier', 'String'),
            Token('identifier', 's'),
            Token('symbol', ';'),
            Token('keyword', 'var'),
            Token('identifier', 'Array'),
            Token('identifier', 'a'),
            Token('symbol', ';'),
            Token('keyword', 'if'),
            Token('symbol', '('),
            Token('keyword', 'false'),
            Token('symbol', ')'),
            Token('symbol', '{'),
            Token('keyword', 'let'),
            Token('identifier', 's'),
            Token('symbol', '='),
            Token('stringConstant', 'string constant'),
            Token('symbol', ';'),
            Token('keyword', 'let'),
            Token('identifier', 's'),
            Token('symbol', '='),
            Token('keyword', 'null'),
            Token('symbol', ';'),
            Token('keyword', 'let'),
            Token('identifier', 'a'),
            Token('symbol', '['),
            Token('integerConstant', '1'),
            Token('symbol', ']'),
            Token('symbol', '='),
            Token('identifier', 'a'),
            Token('symbol', '['),
            Token('integerConstant', '2'),
            Token('symbol', ']'),
            Token('symbol', ';'),
            Token('symbol', '}'),
            Token('keyword', 'else'),
            Token('symbol', '{'),
            Token('keyword', 'let'),
            Token('identifier', 'i'),
            Token('symbol', '='),
            Token('identifier', 'i'),
            Token('symbol', '*'),
            Token('symbol', '('),
            Token('symbol', '-'),
            Token('identifier', 'j'),
            Token('symbol', ')'),
            Token('symbol', ';'),
            Token('keyword', 'let'),
            Token('identifier', 'j'),
            Token('symbol', '='),
            Token('identifier', 'j'),
            Token('symbol', '/'),
            Token('symbol', '('),
            Token('symbol', '-'),
            Token('integerConstant', '2'),
            Token('symbol', ')'),
            Token('symbol', ';'),
            Token('keyword', 'let'),
            Token('identifier', 'i'),
            Token('symbol', '='),
            Token('identifier', 'i'),
            Token('symbol', '|'),
            Token('identifier', 'j'),
            Token('symbol', ';'),
            Token('symbol', '}'),
            Token('keyword', 'return'),
            Token('symbol', ';'),
            Token('symbol', '}'),
            Token('symbol', '}'),
        ]
        self.assertEqual(expected, actual)

    def test_symbol(self):
        for symbol in SYMBOLS:
            tokens = tokenize(symbol)
            expected = Token('symbol', symbol)
            self.assertEqual(expected, tokens[0])

    def test_keyword(self):
        for keyword in KEYWORDS:
            tokens = tokenize(keyword)
            expected = Token('keyword', keyword)
            self.assertEqual(expected, tokens[0])

    def test_string(self):
        jack_text = 'let foo = "this is a string";'
        tokens = tokenize(jack_text)
        expected = Token('stringConstant', 'this is a string')
        self.assertEqual(expected, tokens[3])

    def test_int(self):
        jack_text = 'let foo = 1234'
        tokens = tokenize(jack_text)
        expected = Token('integerConstant', '1234')
        self.assertEqual(expected, tokens[3])