import unittest
import os
from src.parsers.python_parser import parse_python_with_ast
from src.parsers.js_parser import parse_js
from src.parsers.java_parser import parse_java
from src.parsers.markdown_parser import markdown_split

class TestParsers(unittest.TestCase):
    def setUp(self):
        # Create dummy files for testing
        with open("test.py", "w") as f:
            f.write("def hello_world():\n    print('Hello, world!')\n\nclass MyClass:\n    pass")
        with open("test.js", "w") as f:
            f.write("function hello() { console.log('Hello'); }\n\nclass MyClass {}")
        with open("test.java", "w") as f:
            f.write("public class Test { public static void main(String[] args) { System.out.println('Hello'); } }")
        with open("test.md", "w") as f:
            f.write("# Header 1\n\nSome text.\n\n## Header 2\n\nMore text.")

    def tearDown(self):
        # Clean up dummy files
        os.remove("test.py")
        os.remove("test.js")
        os.remove("test.java")
        os.remove("test.md")

    def test_python_parser(self):
        chunks = parse_python_with_ast("test.py")
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0]['type'], 'function')
        self.assertEqual(chunks[1]['type'], 'class')

    def test_js_parser(self):
        chunks = parse_js("test.js")
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0]['type'], 'function')
        self.assertEqual(chunks[1]['type'], 'class')

    def test_java_parser(self):
        chunks = parse_java("test.java")
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]['type'], 'class')

    def test_markdown_parser(self):
        with open("test.md", "r") as f:
            content = f.read()
        chunks = markdown_split(content)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0]['metadata']['Header 1'], 'Header 1')
        self.assertEqual(chunks[1]['metadata']['Header 2'], 'Header 2')

if __name__ == "__main__":
    unittest.main()