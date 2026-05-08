#!/usr/bin/env python3
"""
Nova - A general-purpose interpreted language.
Syntax inspired by Python, designed for systems, automation, and game projects.
"""

import sys
import os
import re
import time
import json
import subprocess
import importlib
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Optional

VERSION = "0.1.0"

# ─────────────────────────────────────────────
#  HELP PAGES
# ─────────────────────────────────────────────

HELP_PAGES = {
    "index": """
Nova Language Help - v{ver}
===========================

Available help pages:
  help vars        - Variables and types
  help say         - Output to console
  help feed        - Feedback mode
  help exec        - Execute files and groups
  help wait        - Pause execution
  help get         - Package/resource fetching
  help flow        - if / elif / else / while / for
  help func        - def (functions)
  help group       - Code groups
  help macro       - varcd (macros / shortcuts)
  help math        - Arithmetic and expressions
  help strings     - String features (f-strings, /j)
  help input       - Reading user input
  help types       - Type casting
  help import      - Importing Nova modules
  help errors      - Error handling (try/catch)
  help os          - OS and shell integration
  help net         - HTTP requests
  help version     - Language version info

Type  help <page>  for details.
""".format(ver=VERSION),

    "vars": """
Variables
---------
Declare a variable:
  var <name> = <value>

Types: str, int, float, bool, list, dict, null

Examples:
  var name = "Alice"
  var age  = 30
  var pi   = 3.14
  var on   = true
  var data = [1, 2, 3]
  var cfg  = {key: "val"}
  var nothing = null

Reassign without var:
  name = "Bob"

Delete a variable:
  del <name>
""",

    "say": """
Output - say
------------
Print text or values to the console.

Usage:
  say("<text>")
  say(<var>)
  say("<text>" + <var> + "<text>")
  say(f"Hello {name}, you are {age} years old")

Multi-line form:
  say(
    "line one",
    var1,
    "line two"
  )

Line breaks:
  /j          - one newline
  /j*N        - N newlines  (e.g. /j*3)
  /t          - tab
""",

    "feed": """
Feedback Mode - feed
--------------------
Prints validation status after each statement.

  feed.on       - enable  (feed - Valid / feed - Invalid <error>)
  feed.off      - disable (default)
""",

    "exec": """
Execute - exec
--------------
Run a Nova file or an inline code variable or a group.

  exec <file.nv>            - run a Nova source file
  exec <var>                - run code stored in a variable
  exec <groupname>          - run a defined group

A group is a named block of code:
  group greet(
    say("Hello from group!")
    wait 1
  )
  exec greet
""",

    "wait": """
Wait - wait
-----------
Pause execution for a given number of seconds.

  wait <seconds>
  wait 0.5
  wait 2
""",

    "get": """
Package / Resource Fetching - get
----------------------------------
Install packages or fetch remote data.

Install from Nova registry (bundled extras):
  get <pkg> from source install

Install arbitrary Python package via pip:
  get <pkg> from pip install

Fetch from a Git repository:
  get <pkg> from git <url> install

Fetch URL and store in variable:
  get <varname> from url <url> var

Examples:
  get requests from pip install
  get mylib    from git https://github.com/user/repo install
  get data     from url https://api.example.com/data var
""",

    "flow": """
Control Flow
------------
if / elif / else:
  if <condition>(
    ...
  ) elif <condition>(
    ...
  ) else(
    ...
  )

while loop:
  while <condition>(
    ...
  )

for loop (range):
  for i in range(10)(
    say(i)
  )

for loop (list):
  for item in mylist(
    say(item)
  )

Break / continue:
  break
  continue
""",

    "func": """
Functions - def
---------------
Define:
  def greet(name)(
    say(f"Hello {name}")
    return "done"
  )

Call:
  greet("Alice")
  var result = greet("Bob")

Default params:
  def add(a, b = 0)(
    return a + b
  )
""",

    "group": """
Groups - group
--------------
Named blocks of reusable code (no parameters).

  group setup(
    say("Initializing...")
    wait 1
    say("Ready.")
  )

Run with exec:
  exec setup

Groups share the global scope.
""",

    "macro": """
Macros - varcd
--------------
Store a reusable code snippet as a shortcut.

  varcd <name> = <code expression>

Example:
  varcd greet_user = say(f"Hello {name}!/j")

Call like a statement:
  name = "Alice"
  greet_user
""",

    "math": """
Math and Expressions
--------------------
Operators: + - * / // % **
Comparison: == != < > <= >=
Logical: and or not

  var x = 10 + 5 * 2
  var y = x ** 2
  var ok = x > 5 and y < 1000

Built-in math functions:
  abs(x)  sqrt(x)  floor(x)  ceil(x)
  min(a, b)  max(a, b)  round(x, n)
  rand()       - random float 0..1
  randint(a,b) - random int
""",

    "strings": """
Strings
-------
Plain string:    "hello"  or  'hello'
F-string:        f"Hello {name}, age {age}"

Escape sequences inside any string:
  /j     - newline
  /j*N   - N newlines
  /t     - tab
  /r     - carriage return
  //     - literal slash

String operations:
  var s = "hello"
  var s2 = s.upper()
  var s3 = s.replace("l", "r")
  var n  = s.len()
  var b  = s.starts("he")
  var b2 = s.ends("lo")
  var p  = s.find("ll")
  var sl = s.slice(1, 3)
  var sp = s.split(",")
  var jn = ",".join(mylist)
""",

    "input": """
User Input - ask
----------------
  var name = ask("Enter your name: ")
  var age  = ask("Age: ").as_int()
""",

    "types": """
Type Casting
------------
  .as_int()    - convert to integer
  .as_float()  - convert to float
  .as_str()    - convert to string
  .as_bool()   - convert to boolean
  .as_list()   - convert string/dict to list

  var n = "42".as_int()
  var s = 3.14.as_str()
""",

    "import": """
Import Nova Modules
-------------------
Import another .nv file as a module:
  import <name> from <file.nv>

Then access its exported vars/groups:
  <name>.<var>
  exec <name>.<group>

Export from a module file using:
  export <var>
  export <group>
""",

    "errors": """
Error Handling - try / catch
-----------------------------
  try(
    var x = 1 / 0
  ) catch(err)(
    say(f"Error: {err}")
  )
""",

    "os": """
OS and Shell Integration
------------------------
Run a shell command and capture output:
  var out = shell("ls -la")

Get environment variable:
  var home = env("HOME")

Set environment variable:
  setenv("MY_VAR", "value")

Get current working directory:
  var cwd = getcwd()

Change directory:
  cd("/path/to/dir")

Check path exists:
  var ok = exists("/tmp/file.txt")

Read file:
  var text = readfile("data.txt")

Write file:
  writefile("out.txt", "hello")

Append to file:
  appendfile("log.txt", "new line")
""",

    "net": """
HTTP Requests
-------------
GET request:
  var res = http.get("https://api.example.com/data")

POST request:
  var res = http.post("https://api.example.com", {key: "val"})

res is a dict with:
  res["status"]  - HTTP status code
  res["body"]    - response text
  res["json"]    - parsed JSON (if available)

Headers:
  var res = http.get("https://...", {Authorization: "Bearer token"})
""",

    "version": """
Version
-------
Nova language interpreter v{ver}
Python {pyver}

Run  nova --version  or  nova -v  from the terminal.
""".format(ver=VERSION, pyver=sys.version.split()[0]),
}


# ─────────────────────────────────────────────
#  LEXER
# ─────────────────────────────────────────────

TT_INT      = "INT"
TT_FLOAT    = "FLOAT"
TT_STRING   = "STRING"
TT_FSTRING  = "FSTRING"
TT_PSTRING  = "PSTRING"
TT_BOOL     = "BOOL"
TT_NULL     = "NULL"
TT_IDENT    = "IDENT"
TT_KEYWORD  = "KEYWORD"
TT_OP       = "OP"
TT_LPAREN   = "LPAREN"
TT_RPAREN   = "RPAREN"
TT_LBRACKET = "LBRACKET"
TT_RBRACKET = "RBRACKET"
TT_LBRACE   = "LBRACE"
TT_RBRACE   = "RBRACE"
TT_COMMA    = "COMMA"
TT_COLON    = "COLON"
TT_DOT      = "DOT"
TT_NEWLINE  = "NEWLINE"
TT_EOF      = "EOF"

KEYWORDS = {
    "var", "varcd", "say", "exec", "wait", "get", "from", "import",
    "group", "def", "return", "if", "elif", "else", "while", "for",
    "in", "range", "break", "continue", "and", "or", "not",
    "true", "false", "null", "try", "catch", "del", "export",
    "install", "source", "pip", "git", "url", "var",
    "feed", "ask", "shell", "env", "setenv", "getcwd", "cd",
    "exists", "readfile", "writefile", "appendfile", "help",
    "clear", "exit", "quit",
}

class Token:
    def __init__(self, type_, value=None, line=0):
        self.type  = type_
        self.value = value
        self.line  = line
    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"

class LexerError(Exception):
    pass

class Lexer:
    def __init__(self, source: str):
        self.source  = source
        self.pos     = 0
        self.line    = 1
        self.tokens  = []

    def error(self, msg):
        raise LexerError(f"[Line {self.line}] Lexer error: {msg}")

    def peek(self, offset=0):
        p = self.pos + offset
        return self.source[p] if p < len(self.source) else None

    def advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
        return ch

    def skip_whitespace(self):
        while self.pos < len(self.source) and self.peek() in (" ", "\t", "\r"):
            self.advance()

    def skip_comment(self):
        while self.pos < len(self.source) and self.peek() != "\n":
            self.advance()

    def read_string(self, quote, fstring=False):
        self.advance()  # skip opening quote
        buf = ""
        while self.pos < len(self.source):
            ch = self.peek()
            if ch == "\\":
                self.advance()
                esc = self.advance()
                buf += {"n": "\n", "t": "\t", "r": "\r", "\\": "\\"}.get(esc, esc)
            elif ch == quote:
                self.advance()
                break
            elif ch == "\n":
                self.error("Unterminated string")
            else:
                buf += self.advance()
        return buf

    def make_token(self, type_, value=None):
        return Token(type_, value, self.line)

    def tokenize(self):
        src = self.source
        while self.pos < len(src):
            self.skip_whitespace()
            if self.pos >= len(src):
                break

            ch = self.peek()

            # newline
            if ch == "\n":
                self.advance()
                self.tokens.append(self.make_token(TT_NEWLINE))
                continue

            # comment
            if ch == "#":
                self.skip_comment()
                continue

            # f-string
            if ch in ("f", "F") and self.peek(1) in ('"', "'"):
                self.advance()
                q = self.peek()
                s = self.read_string(q, fstring=True)
                self.tokens.append(self.make_token(TT_FSTRING, s))
                continue

            # p-string (prompt string)
            if ch in ("p", "P") and self.peek(1) in ('"', "'"):
                self.advance()
                q = self.peek()
                s = self.read_string(q)
                self.tokens.append(self.make_token(TT_PSTRING, s))
                continue

            # string
            if ch in ('"', "'"):
                s = self.read_string(ch)
                self.tokens.append(self.make_token(TT_STRING, s))
                continue

            # number
            if ch.isdigit() or (ch == "-" and self.peek(1) and self.peek(1).isdigit()
                                 and (not self.tokens or self.tokens[-1].type in
                                      (TT_OP, TT_COMMA, TT_LPAREN, TT_NEWLINE, TT_EOF, TT_KEYWORD))):
                num = ""
                if ch == "-":
                    num += self.advance()
                while self.pos < len(src) and self.peek() and (self.peek().isdigit()):
                    num += self.advance()
                if self.pos < len(src) and self.peek() == ".":
                    num += self.advance()
                    while self.pos < len(src) and self.peek() and self.peek().isdigit():
                        num += self.advance()
                    self.tokens.append(self.make_token(TT_FLOAT, float(num)))
                else:
                    self.tokens.append(self.make_token(TT_INT, int(num)))
                continue

            # identifier / keyword
            if ch.isalpha() or ch == "_":
                ident = ""
                while self.pos < len(src) and self.peek() and (self.peek().isalnum() or self.peek() in ("_",)):
                    ident += self.advance()
                if ident == "true":
                    self.tokens.append(self.make_token(TT_BOOL, True))
                elif ident == "false":
                    self.tokens.append(self.make_token(TT_BOOL, False))
                elif ident == "null":
                    self.tokens.append(self.make_token(TT_NULL, None))
                elif ident in KEYWORDS:
                    self.tokens.append(self.make_token(TT_KEYWORD, ident))
                else:
                    self.tokens.append(self.make_token(TT_IDENT, ident))
                continue

            # operators (two-char first)
            two = src[self.pos:self.pos+2]
            if two in ("==", "!=", "<=", ">=", "**", "//", "+=", "-=", "*=", "/="):
                self.pos += 2
                self.tokens.append(self.make_token(TT_OP, two))
                continue

            one_ops = set("+-*/%<>=!&|^~")
            if ch in one_ops:
                self.tokens.append(self.make_token(TT_OP, self.advance()))
                continue

            if ch == "(":
                self.advance(); self.tokens.append(self.make_token(TT_LPAREN)); continue
            if ch == ")":
                self.advance(); self.tokens.append(self.make_token(TT_RPAREN)); continue
            if ch == "[":
                self.advance(); self.tokens.append(self.make_token(TT_LBRACKET)); continue
            if ch == "]":
                self.advance(); self.tokens.append(self.make_token(TT_RBRACKET)); continue
            if ch == "{":
                self.advance(); self.tokens.append(self.make_token(TT_LBRACE)); continue
            if ch == "}":
                self.advance(); self.tokens.append(self.make_token(TT_RBRACE)); continue
            if ch == ",":
                self.advance(); self.tokens.append(self.make_token(TT_COMMA)); continue
            if ch == ":":
                self.advance(); self.tokens.append(self.make_token(TT_COLON)); continue
            if ch == ".":
                self.advance(); self.tokens.append(self.make_token(TT_DOT)); continue

            self.error(f"Unknown character: {ch!r}")

        self.tokens.append(self.make_token(TT_EOF))
        return self.tokens


# ─────────────────────────────────────────────
#  AST NODES
# ─────────────────────────────────────────────

class Node:
    pass

class NumberNode(Node):
    def __init__(self, value): self.value = value

class StringNode(Node):
    def __init__(self, value): self.value = value

class FStringNode(Node):
    def __init__(self, value): self.value = value   # raw template

class PStringNode(Node):
    def __init__(self, value): self.value = value   # prompt string template

class BoolNode(Node):
    def __init__(self, value): self.value = value

class NullNode(Node):
    pass

class ListNode(Node):
    def __init__(self, items): self.items = items

class DictNode(Node):
    def __init__(self, pairs): self.pairs = pairs   # list of (key_node, val_node)

class IdentNode(Node):
    def __init__(self, name): self.name = name

class BinOpNode(Node):
    def __init__(self, left, op, right): self.left=left; self.op=op; self.right=right

class UnaryOpNode(Node):
    def __init__(self, op, operand): self.op=op; self.operand=operand

class AssignNode(Node):
    def __init__(self, name, value, declare=False):
        self.name=name; self.value=value; self.declare=declare

class AugAssignNode(Node):
    def __init__(self, name, op, value): self.name=name; self.op=op; self.value=value

class DelNode(Node):
    def __init__(self, name): self.name = name

class SayNode(Node):
    def __init__(self, args): self.args = args

class WaitNode(Node):
    def __init__(self, duration): self.duration = duration

class FeedNode(Node):
    def __init__(self, mode): self.mode = mode   # "on" or "off"

class ExecNode(Node):
    def __init__(self, target): self.target = target  # str or IdentNode

class GetNode(Node):
    def __init__(self, name, source, mode, extra=None):
        self.name=name; self.source=source; self.mode=mode; self.extra=extra

class HelpNode(Node):
    def __init__(self, page): self.page = page

class IfNode(Node):
    def __init__(self, branches, else_body):
        self.branches=branches    # list of (condition, body)
        self.else_body=else_body  # body or None

class WhileNode(Node):
    def __init__(self, condition, body): self.condition=condition; self.body=body

class ForNode(Node):
    def __init__(self, var, iterable, body): self.var=var; self.iterable=iterable; self.body=body

class BreakNode(Node): pass
class ContinueNode(Node): pass

class ReturnNode(Node):
    def __init__(self, value): self.value = value

class FuncDefNode(Node):
    def __init__(self, name, params, defaults, body):
        self.name=name; self.params=params; self.defaults=defaults; self.body=body

class GroupDefNode(Node):
    def __init__(self, name, body): self.name=name; self.body=body

class MacroDefNode(Node):
    def __init__(self, name, code): self.name=name; self.code=code

class MacroCallNode(Node):
    def __init__(self, name): self.name = name

class CallNode(Node):
    def __init__(self, func, args, kwargs=None):
        self.func=func; self.args=args; self.kwargs=kwargs or {}

class AttrNode(Node):
    def __init__(self, obj, attr): self.obj=obj; self.attr=attr

class MethodCallNode(Node):
    def __init__(self, obj, method, args): self.obj=obj; self.method=method; self.args=args

class IndexNode(Node):
    def __init__(self, obj, index): self.obj=obj; self.index=index

class TryCatchNode(Node):
    def __init__(self, try_body, err_var, catch_body):
        self.try_body=try_body; self.err_var=err_var; self.catch_body=catch_body

class ImportNode(Node):
    def __init__(self, alias, filepath): self.alias=alias; self.filepath=filepath

class ExportNode(Node):
    def __init__(self, name): self.name = name

class ShellNode(Node):
    def __init__(self, cmd): self.cmd = cmd

class ProgramNode(Node):
    def __init__(self, statements): self.statements = statements


# ─────────────────────────────────────────────
#  PARSER
# ─────────────────────────────────────────────

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos    = 0

    def cur(self): return self.tokens[self.pos]
    def peek(self, offset=1): return self.tokens[min(self.pos+offset, len(self.tokens)-1)]

    def advance(self):
        t = self.tokens[self.pos]
        if self.pos < len(self.tokens)-1:
            self.pos += 1
        return t

    def skip_newlines(self):
        while self.cur().type == TT_NEWLINE:
            self.advance()

    def expect(self, type_, value=None):
        t = self.cur()
        if t.type != type_:
            raise ParseError(f"[Line {t.line}] Expected {type_}, got {t.type} ({t.value!r})")
        if value is not None and t.value != value:
            raise ParseError(f"[Line {t.line}] Expected {value!r}, got {t.value!r}")
        return self.advance()

    def match(self, type_, value=None):
        t = self.cur()
        if t.type != type_:
            return False
        if value is not None and t.value != value:
            return False
        return True

    def consume_if(self, type_, value=None):
        if self.match(type_, value):
            return self.advance()
        return None

    # ---- block: ( ... )
    def parse_block(self):
        self.expect(TT_LPAREN)
        self.skip_newlines()
        stmts = []
        while not self.match(TT_RPAREN) and not self.match(TT_EOF):
            s = self.parse_statement()
            if s:
                stmts.append(s)
            self.skip_newlines()
        self.expect(TT_RPAREN)
        return stmts

    def parse_program(self):
        stmts = []
        self.skip_newlines()
        while not self.match(TT_EOF):
            s = self.parse_statement()
            if s:
                stmts.append(s)
            self.skip_newlines()
        return ProgramNode(stmts)

    def parse_statement(self):
        t = self.cur()

        # skip bare newlines
        if t.type == TT_NEWLINE:
            self.advance()
            return None

        # keywords
        if t.type == TT_KEYWORD:
            kw = t.value

            if kw == "var":
                return self.parse_var()
            if kw == "varcd":
                return self.parse_varcd()
            if kw == "say":
                return self.parse_say()
            if kw == "wait":
                return self.parse_wait()
            if kw == "feed":
                return self.parse_feed()
            if kw == "exec":
                return self.parse_exec()
            if kw == "get":
                return self.parse_get()
            if kw == "help":
                return self.parse_help()
            if kw == "if":
                return self.parse_if()
            if kw == "while":
                return self.parse_while()
            if kw == "for":
                return self.parse_for()
            if kw == "break":
                self.advance(); return BreakNode()
            if kw == "continue":
                self.advance(); return ContinueNode()
            if kw == "return":
                self.advance()
                val = self.parse_expr() if not self.match(TT_NEWLINE) and not self.match(TT_EOF) else NullNode()
                return ReturnNode(val)
            if kw == "def":
                return self.parse_func()
            if kw == "group":
                return self.parse_group()
            if kw == "del":
                self.advance()
                name = self.expect(TT_IDENT).value
                return DelNode(name)
            if kw == "try":
                return self.parse_try()
            if kw == "import":
                return self.parse_import()
            if kw == "export":
                self.advance()
                name = self.expect(TT_IDENT).value
                return ExportNode(name)

        # ident could be assignment, augmented assign, macro call, or expr
        if t.type == TT_IDENT:
            # look ahead
            nxt = self.peek()
            if nxt.type == TT_OP and nxt.value == "=":
                # simple assign
                name = self.advance().value
                self.advance()  # =
                val  = self.parse_expr()
                return AssignNode(name, val, declare=False)
            if nxt.type == TT_OP and nxt.value in ("+=", "-=", "*=", "/="):
                name = self.advance().value
                op   = self.advance().value
                val  = self.parse_expr()
                return AugAssignNode(name, op, val)
            # check macro call (ident on its own line)
            # We'll handle via expr and let interpreter deal with it

        # expression statement (covers calls, etc.)
        expr = self.parse_expr()

        # augmented assign on attr/index would appear here — skip for now
        return expr

    # ── var ──────────────────────────────────
    def parse_var(self):
        self.expect(TT_KEYWORD, "var")
        name = self.expect(TT_IDENT).value
        self.expect(TT_OP, "=")
        val  = self.parse_expr()
        return AssignNode(name, val, declare=True)

    # ── varcd ─────────────────────────────────
    def parse_varcd(self):
        self.expect(TT_KEYWORD, "varcd")
        name = self.expect(TT_IDENT).value
        self.expect(TT_OP, "=")
        # rest of line is raw code
        code_tokens = []
        while not self.match(TT_NEWLINE) and not self.match(TT_EOF):
            code_tokens.append(self.advance())
        # reconstruct minimal source from tokens
        code = self._tokens_to_source(code_tokens)
        return MacroDefNode(name, code)

    def _tokens_to_source(self, toks):
        parts = []
        for t in toks:
            if t.type == TT_STRING:
                parts.append(f'"{t.value}"')
            elif t.type == TT_FSTRING:
                parts.append(f'f"{t.value}"')
            elif t.type in (TT_INT, TT_FLOAT):
                parts.append(str(t.value))
            elif t.type == TT_BOOL:
                parts.append("true" if t.value else "false")
            elif t.type == TT_NULL:
                parts.append("null")
            elif t.type in (TT_IDENT, TT_KEYWORD):
                parts.append(str(t.value))
            elif t.type == TT_OP:
                parts.append(t.value)
            elif t.type == TT_LPAREN:
                parts.append("(")
            elif t.type == TT_RPAREN:
                parts.append(")")
            elif t.type == TT_COMMA:
                parts.append(",")
            elif t.type == TT_DOT:
                parts.append(".")
            elif t.type == TT_LBRACKET:
                parts.append("[")
            elif t.type == TT_RBRACKET:
                parts.append("]")
            elif t.type == TT_LBRACE:
                parts.append("{")
            elif t.type == TT_RBRACE:
                parts.append("}")
            elif t.type == TT_COLON:
                parts.append(":")
        return " ".join(parts)

    # ── say ──────────────────────────────────
    def parse_say(self):
        self.expect(TT_KEYWORD, "say")
        args = self.parse_call_args_inline()
        return SayNode(args)

    # ── wait ─────────────────────────────────
    def parse_wait(self):
        self.expect(TT_KEYWORD, "wait")
        dur = self.parse_expr()
        return WaitNode(dur)

    # ── feed ─────────────────────────────────
    def parse_feed(self):
        self.expect(TT_KEYWORD, "feed")
        self.expect(TT_DOT)
        mode_tok = self.advance()
        if mode_tok.value not in ("on", "off"):
            raise ParseError(f"feed expects .on or .off")
        return FeedNode(mode_tok.value)

    # ── exec ─────────────────────────────────
    def parse_exec(self):
        self.expect(TT_KEYWORD, "exec")
        if self.match(TT_IDENT):
            target = self.advance().value
            # could be module.group
            if self.match(TT_DOT):
                self.advance()
                sub = self.expect(TT_IDENT).value
                target = target + "." + sub
        elif self.match(TT_STRING):
            target = self.advance().value
        else:
            raise ParseError("exec expects a name or file string")
        return ExecNode(target)

    # ── get ──────────────────────────────────
    def parse_get(self):
        self.expect(TT_KEYWORD, "get")
        name = self.expect(TT_IDENT).value
        self.expect(TT_KEYWORD, "from")
        source_tok = self.advance()
        source = source_tok.value
        mode_tok = self.advance()
        mode = mode_tok.value
        extra = None
        if mode == "url":
            extra = self.advance().value if self.match(TT_STRING) else self.advance().value
            mode = "url"
        elif mode == "git":
            extra = self.advance().value if self.match(TT_STRING) else None
            nxt = self.advance()  # install or var
            mode = nxt.value
        return GetNode(name, source, mode, extra)

    # ── help ─────────────────────────────────
    def parse_help(self):
        self.expect(TT_KEYWORD, "help")
        page = "index"
        # Accept any token as page name (ident or keyword like feed, group, etc.)
        if not self.match(TT_NEWLINE) and not self.match(TT_EOF):
            page = self.advance().value
        return HelpNode(page)

    # ── condition (stops at block-opening paren) ─────
    def parse_condition(self):
        return self._cond_logical()

    def _cond_logical(self):
        left = self._cond_comparison()
        while self.match(TT_KEYWORD, "and") or self.match(TT_KEYWORD, "or"):
            op = self.advance().value
            right = self._cond_comparison()
            left = BinOpNode(left, op, right)
        return left

    def _cond_comparison(self):
        if self.match(TT_KEYWORD, "not"):
            self.advance()
            return UnaryOpNode("not", self._cond_comparison())
        left = self._cond_add()
        while self.match(TT_OP) and self.cur().value in ("==","!=","<",">","<=",">="):
            op = self.advance().value
            right = self._cond_add()
            left = BinOpNode(left, op, right)
        return left

    def _cond_add(self):
        left = self._cond_mul()
        while self.match(TT_OP) and self.cur().value in ("+", "-"):
            op = self.advance().value
            right = self._cond_mul()
            left = BinOpNode(left, op, right)
        return left

    def _cond_mul(self):
        left = self._cond_unary()
        while self.match(TT_OP) and self.cur().value in ("*", "/", "//", "%"):
            op = self.advance().value
            right = self._cond_unary()
            left = BinOpNode(left, op, right)
        return left

    def _cond_unary(self):
        if self.match(TT_OP, "-"):
            self.advance()
            return UnaryOpNode("-", self._cond_unary())
        return self._cond_postfix()

    def _cond_postfix(self):
        """Postfix that does NOT consume a bare ( as a call (it is a block delimiter)."""
        node = self.parse_primary()
        while True:
            if self.match(TT_DOT):
                self.advance()
                attr = self.advance().value
                if self.match(TT_LPAREN):
                    args = self.parse_call_args_inline()
                    node = MethodCallNode(node, attr, args)
                else:
                    node = AttrNode(node, attr)
            elif self.match(TT_LBRACKET):
                self.advance()
                idx = self.parse_expr()
                self.expect(TT_RBRACKET)
                node = IndexNode(node, idx)
            else:
                break
        return node

    # ── if ───────────────────────────────────
    def parse_if(self):
        self.expect(TT_KEYWORD, "if")
        cond  = self.parse_condition()
        body  = self.parse_block()
        branches = [(cond, body)]
        self.skip_newlines()
        while self.match(TT_KEYWORD, "elif"):
            self.advance()
            c = self.parse_condition()
            b = self.parse_block()
            branches.append((c, b))
            self.skip_newlines()
        else_body = None
        if self.match(TT_KEYWORD, "else"):
            self.advance()
            else_body = self.parse_block()
        return IfNode(branches, else_body)

    # ── while ────────────────────────────────
    def parse_while(self):
        self.expect(TT_KEYWORD, "while")
        cond = self.parse_condition()
        body = self.parse_block()
        return WhileNode(cond, body)

    # ── for ──────────────────────────────────
    def parse_for(self):
        self.expect(TT_KEYWORD, "for")
        var = self.expect(TT_IDENT).value
        self.expect(TT_KEYWORD, "in")
        iterable = self._cond_postfix()
        body = self.parse_block()
        return ForNode(var, iterable, body)

    # ── def ──────────────────────────────────
    def parse_func(self):
        self.expect(TT_KEYWORD, "def")
        name = self.expect(TT_IDENT).value
        self.expect(TT_LPAREN)
        params   = []
        defaults = {}
        while not self.match(TT_RPAREN):
            p = self.expect(TT_IDENT).value
            params.append(p)
            if self.consume_if(TT_OP, "="):
                defaults[p] = self.parse_expr()
            self.consume_if(TT_COMMA)
        self.expect(TT_RPAREN)
        body = self.parse_block()
        return FuncDefNode(name, params, defaults, body)

    # ── group ────────────────────────────────
    def parse_group(self):
        self.expect(TT_KEYWORD, "group")
        name = self.expect(TT_IDENT).value
        body = self.parse_block()
        return GroupDefNode(name, body)

    # ── try/catch ────────────────────────────
    def parse_try(self):
        self.expect(TT_KEYWORD, "try")
        try_body = self.parse_block()
        self.skip_newlines()
        self.expect(TT_KEYWORD, "catch")
        self.expect(TT_LPAREN)
        err_var = self.expect(TT_IDENT).value
        self.expect(TT_RPAREN)
        catch_body = self.parse_block()
        return TryCatchNode(try_body, err_var, catch_body)

    # ── import ───────────────────────────────
    def parse_import(self):
        self.expect(TT_KEYWORD, "import")
        alias = self.expect(TT_IDENT).value
        self.expect(TT_KEYWORD, "from")
        fp = self.advance().value
        return ImportNode(alias, fp)

    # ── call args (inline or multiline) ──────
    def parse_call_args_inline(self):
        """Parse (arg, arg, ...) or multiline ( \n arg \n arg \n )"""
        self.expect(TT_LPAREN)
        self.skip_newlines()
        args = []
        while not self.match(TT_RPAREN) and not self.match(TT_EOF):
            args.append(self.parse_expr())
            self.skip_newlines()
            self.consume_if(TT_COMMA)
            self.skip_newlines()
        self.expect(TT_RPAREN)
        return args

    # ── expressions ──────────────────────────
    def parse_expr(self):
        return self.parse_logical()

    def parse_logical(self):
        left = self.parse_comparison()
        while self.match(TT_KEYWORD, "and") or self.match(TT_KEYWORD, "or"):
            op = self.advance().value
            right = self.parse_comparison()
            left = BinOpNode(left, op, right)
        return left

    def parse_comparison(self):
        if self.match(TT_KEYWORD, "not"):
            self.advance()
            return UnaryOpNode("not", self.parse_comparison())
        left = self.parse_addition()
        while self.match(TT_OP) and self.cur().value in ("==","!=","<",">","<=",">="):
            op = self.advance().value
            right = self.parse_addition()
            left = BinOpNode(left, op, right)
        return left

    def parse_addition(self):
        left = self.parse_multiplication()
        while self.match(TT_OP) and self.cur().value in ("+", "-"):
            op = self.advance().value
            right = self.parse_multiplication()
            left = BinOpNode(left, op, right)
        return left

    def parse_multiplication(self):
        left = self.parse_power()
        while self.match(TT_OP) and self.cur().value in ("*", "/", "//", "%"):
            op = self.advance().value
            right = self.parse_power()
            left = BinOpNode(left, op, right)
        return left

    def parse_power(self):
        left = self.parse_unary()
        if self.match(TT_OP, "**"):
            self.advance()
            right = self.parse_power()
            return BinOpNode(left, "**", right)
        return left

    def parse_unary(self):
        if self.match(TT_OP, "-"):
            self.advance()
            return UnaryOpNode("-", self.parse_unary())
        return self.parse_postfix()

    def parse_postfix(self):
        node = self.parse_primary()
        while True:
            if self.match(TT_DOT):
                self.advance()
                attr = self.advance().value
                if self.match(TT_LPAREN):
                    args = self.parse_call_args_inline()
                    node = MethodCallNode(node, attr, args)
                else:
                    node = AttrNode(node, attr)
            elif self.match(TT_LBRACKET):
                self.advance()
                idx = self.parse_expr()
                self.expect(TT_RBRACKET)
                node = IndexNode(node, idx)
            elif self.match(TT_LPAREN):
                # function call
                args = self.parse_call_args_inline()
                node = CallNode(node, args)
            else:
                break
        return node

    def parse_primary(self):
        t = self.cur()

        if t.type == TT_INT:   self.advance(); return NumberNode(t.value)
        if t.type == TT_FLOAT: self.advance(); return NumberNode(t.value)
        if t.type == TT_BOOL:  self.advance(); return BoolNode(t.value)
        if t.type == TT_NULL:  self.advance(); return NullNode()
        if t.type == TT_STRING: self.advance(); return StringNode(t.value)
        if t.type == TT_FSTRING: self.advance(); return FStringNode(t.value)
        if t.type == TT_PSTRING: self.advance(); return PStringNode(t.value)

        if t.type == TT_LPAREN:
            self.advance()
            self.skip_newlines()
            expr = self.parse_expr()
            self.skip_newlines()
            self.expect(TT_RPAREN)
            return expr

        if t.type == TT_LBRACKET:
            return self.parse_list()

        if t.type == TT_LBRACE:
            return self.parse_dict()

        if t.type == TT_IDENT:
            self.advance()
            return IdentNode(t.value)

        # keyword-as-call builtins: ask, shell, env, setenv, getcwd, cd, exists, readfile, writefile, appendfile
        if t.type == TT_KEYWORD and t.value in (
            "ask","shell","env","setenv","getcwd","cd",
            "exists","readfile","writefile","appendfile",
            "abs","sqrt","floor","ceil","min","max","round",
            "rand","randint","len","str","int","float","bool","type",
            "clear","exit","quit",
        ):
            name = self.advance().value
            if self.match(TT_LPAREN):
                args = self.parse_call_args_inline()
                return CallNode(IdentNode(name), args)
            return IdentNode(name)

        raise ParseError(f"[Line {t.line}] Unexpected token: {t.type} ({t.value!r})")

    def parse_list(self):
        self.expect(TT_LBRACKET)
        self.skip_newlines()
        items = []
        while not self.match(TT_RBRACKET) and not self.match(TT_EOF):
            items.append(self.parse_expr())
            self.skip_newlines()
            self.consume_if(TT_COMMA)
            self.skip_newlines()
        self.expect(TT_RBRACKET)
        return ListNode(items)

    def parse_dict(self):
        self.expect(TT_LBRACE)
        self.skip_newlines()
        pairs = []
        while not self.match(TT_RBRACE) and not self.match(TT_EOF):
            key = self.parse_primary()
            self.expect(TT_COLON)
            val = self.parse_expr()
            pairs.append((key, val))
            self.skip_newlines()
            self.consume_if(TT_COMMA)
            self.skip_newlines()
        self.expect(TT_RBRACE)
        return DictNode(pairs)


# ─────────────────────────────────────────────
#  RUNTIME VALUES & SCOPE
# ─────────────────────────────────────────────

class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass
class ReturnSignal(Exception):
    def __init__(self, value): self.value = value

class NovaFunction:
    def __init__(self, name, params, defaults, body, closure):
        self.name=name; self.params=params; self.defaults=defaults
        self.body=body; self.closure=closure

class NovaGroup:
    def __init__(self, name, body): self.name=name; self.body=body

class NovaModule:
    def __init__(self, scope): self.scope = scope

class Scope:
    def __init__(self, parent=None):
        self.vars   = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Undefined variable: '{name}'")

    def set(self, name, value):
        if name in self.vars:
            self.vars[name] = value
            return
        if self.parent and self.parent.has(name):
            self.parent.set(name, value)
            return
        self.vars[name] = value   # create in current scope

    def declare(self, name, value):
        self.vars[name] = value

    def has(self, name):
        if name in self.vars:
            return True
        if self.parent:
            return self.parent.has(name)
        return False

    def delete(self, name):
        if name in self.vars:
            del self.vars[name]
        elif self.parent:
            self.parent.delete(name)


# ─────────────────────────────────────────────
#  INTERPRETER
# ─────────────────────────────────────────────

class RuntimeError_(Exception):
    pass

class Interpreter:
    def __init__(self, source_dir="."):
        self.source_dir  = source_dir
        self.global_scope = Scope()
        self.feed_mode   = False
        self.macros      = {}   # name -> raw code string
        self.groups      = {}   # name -> NovaGroup
        self.modules     = {}   # alias -> NovaModule
        self._setup_builtins()

    def _setup_builtins(self):
        import math, random
        self._math  = math
        self._random = random

    # ── Process escape sequences (/j /t /r)
    def _process_escapes(self, s: str) -> str:
        # /j*N
        s = re.sub(r'/j\*(\d+)', lambda m: "\n" * int(m.group(1)), s)
        # /j
        s = s.replace("/j", "\n")
        s = s.replace("/t", "\t")
        s = s.replace("/r", "\r")
        s = s.replace("//", "/")
        return s

    # ── Evaluate f-string
    def _eval_fstring(self, template: str, scope: Scope) -> str:
        def replacer(m):
            expr_src = m.group(1)
            try:
                toks  = Lexer(expr_src).tokenize()
                node  = Parser(toks).parse_expr()
                val   = self.eval_expr(node, scope)
                return self._to_str(val)
            except Exception as e:
                return f"<error:{e}>"
        result = re.sub(r'\{([^}]+)\}', replacer, template)
        return self._process_escapes(result)

    def _to_str(self, val) -> str:
        if val is None:   return "null"
        if val is True:   return "true"
        if val is False:  return "false"
        if isinstance(val, list): return "[" + ", ".join(self._to_str(v) for v in val) + "]"
        if isinstance(val, dict): return "{" + ", ".join(f"{k}: {self._to_str(v)}" for k,v in val.items()) + "}"
        return str(val)

    def _to_bool(self, val) -> bool:
        if val is None or val is False: return False
        if val == 0 or val == "" or val == [] or val == {}: return False
        return True

    # ── String method dispatch
    def _string_method(self, s, method, args):
        if method == "upper":   return s.upper()
        if method == "lower":   return s.lower()
        if method == "strip":   return s.strip()
        if method == "len":     return len(s)
        if method == "replace": return s.replace(args[0], args[1])
        if method == "split":   return s.split(args[0]) if args else s.split()
        if method == "starts":  return s.startswith(args[0])
        if method == "ends":    return s.endswith(args[0])
        if method == "find":    return s.find(args[0])
        if method == "slice":   return s[args[0]:args[1]]
        if method == "join":    return s.join([self._to_str(x) for x in args[0]])
        if method == "contains": return args[0] in s
        if method == "as_int":  return int(s)
        if method == "as_float": return float(s)
        if method == "as_str":  return s
        if method == "as_bool": return bool(s)
        raise RuntimeError_(f"Unknown string method: {method}")

    # ── List method dispatch
    def _list_method(self, lst, method, args):
        if method == "append":  lst.append(args[0]); return None
        if method == "pop":     return lst.pop(args[0] if args else -1)
        if method == "len":     return len(lst)
        if method == "contains": return args[0] in lst
        if method == "reverse": lst.reverse(); return None
        if method == "sort":    lst.sort(); return None
        if method == "slice":   return lst[args[0]:args[1]]
        if method == "join":    return (args[0] if args else "").join(self._to_str(x) for x in lst)
        if method == "index":   return lst.index(args[0])
        if method == "remove":  lst.remove(args[0]); return None
        if method == "as_str":  return self._to_str(lst)
        raise RuntimeError_(f"Unknown list method: {method}")

    # ── Dict method dispatch
    def _dict_method(self, d, method, args):
        if method == "keys":    return list(d.keys())
        if method == "values":  return list(d.values())
        if method == "items":   return [[k,v] for k,v in d.items()]
        if method == "get":     return d.get(args[0], args[1] if len(args)>1 else None)
        if method == "set":     d[args[0]] = args[1]; return None
        if method == "has":     return args[0] in d
        if method == "delete":  del d[args[0]]; return None
        if method == "len":     return len(d)
        if method == "as_str":  return self._to_str(d)
        raise RuntimeError_(f"Unknown dict method: {method}")

    # ── Number method dispatch
    def _number_method(self, n, method, args):
        if method == "as_str":   return str(n)
        if method == "as_int":   return int(n)
        if method == "as_float": return float(n)
        if method == "abs":      return abs(n)
        raise RuntimeError_(f"Unknown number method: {method}")

    # ── Built-in functions
    def _call_builtin(self, name, args, scope):
        m = self._math
        r = self._random
        if name == "abs":      return abs(args[0])
        if name == "sqrt":     return m.sqrt(args[0])
        if name == "floor":    return m.floor(args[0])
        if name == "ceil":     return m.ceil(args[0])
        if name == "min":      return min(args[0], args[1]) if len(args)==2 else min(args[0])
        if name == "max":      return max(args[0], args[1]) if len(args)==2 else max(args[0])
        if name == "round":    return round(args[0], args[1] if len(args)>1 else 0)
        if name == "rand":     return r.random()
        if name == "randint":  return r.randint(int(args[0]), int(args[1]))
        if name == "len":      return len(args[0])
        if name == "str":      return self._to_str(args[0])
        if name == "int":      return int(args[0])
        if name == "float":    return float(args[0])
        if name == "bool":     return self._to_bool(args[0])
        if name == "type":
            v = args[0]
            if v is None: return "null"
            if isinstance(v, bool): return "bool"
            if isinstance(v, int): return "int"
            if isinstance(v, float): return "float"
            if isinstance(v, str): return "str"
            if isinstance(v, list): return "list"
            if isinstance(v, dict): return "dict"
            return "unknown"
        if name == "clear":
            print("\033[2J\033[H", end="", flush=True)
            return None
        if name == "exit" or name == "quit":
            import sys as _sys
            _sys.exit(0)
        if name == "ask":
            prompt = self._to_str(args[0]) if args else ""
            return input(self._process_escapes(prompt))
        if name == "shell":
            cmd = self._to_str(args[0])
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return res.stdout.rstrip()
        if name == "env":
            return os.environ.get(self._to_str(args[0]), "")
        if name == "setenv":
            os.environ[self._to_str(args[0])] = self._to_str(args[1])
            return None
        if name == "getcwd":
            return os.getcwd()
        if name == "cd":
            os.chdir(self._to_str(args[0]))
            return None
        if name == "exists":
            return os.path.exists(self._to_str(args[0]))
        if name == "readfile":
            with open(self._to_str(args[0]), "r", encoding="utf-8") as f:
                return f.read()
        if name == "writefile":
            with open(self._to_str(args[0]), "w", encoding="utf-8") as f:
                f.write(self._to_str(args[1]))
            return None
        if name == "appendfile":
            with open(self._to_str(args[0]), "a", encoding="utf-8") as f:
                f.write(self._to_str(args[1]))
            return None
        # http namespace
        if name == "http.get":
            return self._http_get(args)
        if name == "http.post":
            return self._http_post(args)
        return None

    def _http_get(self, args):
        url = self._to_str(args[0])
        headers = args[1] if len(args) > 1 else {}
        req = urllib.request.Request(url, headers=headers if isinstance(headers, dict) else {})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read().decode("utf-8")
                status = resp.status
                try: j = json.loads(body)
                except: j = None
                return {"status": status, "body": body, "json": j}
        except Exception as e:
            return {"status": 0, "body": str(e), "json": None}

    def _http_post(self, args):
        url  = self._to_str(args[0])
        data = args[1] if len(args) > 1 else {}
        body = json.dumps(data).encode("utf-8") if isinstance(data, dict) else self._to_str(data).encode()
        req  = urllib.request.Request(url, data=body,
               headers={"Content-Type": "application/json"},
               method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                rb   = resp.read().decode("utf-8")
                try: j = json.loads(rb)
                except: j = None
                return {"status": resp.status, "body": rb, "json": j}
        except Exception as e:
            return {"status": 0, "body": str(e), "json": None}

    # ── Evaluate expression
    def eval_expr(self, node, scope: Scope):
        if isinstance(node, NumberNode): return node.value
        if isinstance(node, StringNode): return self._process_escapes(node.value)
        if isinstance(node, FStringNode): return self._eval_fstring(node.value, scope)
        if isinstance(node, PStringNode): return self._eval_fstring(node.value, scope)  # prompt string with interpolation
        if isinstance(node, BoolNode):   return node.value
        if isinstance(node, NullNode):   return None

        if isinstance(node, ListNode):
            return [self.eval_expr(i, scope) for i in node.items]

        if isinstance(node, DictNode):
            d = {}
            for k, v in node.pairs:
                kv = self.eval_expr(k, scope)
                vv = self.eval_expr(v, scope)
                d[kv] = vv
            return d

        if isinstance(node, IdentNode):
            name = node.name
            # http namespace
            if name == "http":
                return "__http__"
            # builtin constants
            if name in ("abs","sqrt","floor","ceil","min","max","round","rand","randint",
                        "len","str","int","float","bool","type",
                        "ask","shell","env","setenv","getcwd","cd",
                        "exists","readfile","writefile","appendfile"):
                return f"__builtin__{name}"
            try:
                return scope.get(name)
            except NameError:
                raise RuntimeError_(f"Undefined: '{name}'")

        if isinstance(node, BinOpNode):
            return self._eval_binop(node, scope)

        if isinstance(node, UnaryOpNode):
            v = self.eval_expr(node.operand, scope)
            if node.op == "-": return -v
            if node.op == "not": return not self._to_bool(v)

        if isinstance(node, AttrNode):
            obj = self.eval_expr(node.obj, scope)
            if isinstance(obj, dict): return obj.get(node.attr)
            if isinstance(obj, NovaModule): return obj.scope.get(node.attr)
            if obj == "__http__": return f"__builtin__http.{node.attr}"
            raise RuntimeError_(f"Cannot get attribute '{node.attr}' on {type(obj).__name__}")

        if isinstance(node, MethodCallNode):
            obj    = self.eval_expr(node.obj, scope)
            method = node.method
            args   = [self.eval_expr(a, scope) for a in node.args]
            if isinstance(obj, str):    return self._string_method(obj, method, args)
            if isinstance(obj, list):   return self._list_method(obj, method, args)
            if isinstance(obj, dict):   return self._dict_method(obj, method, args)
            if isinstance(obj, (int, float)): return self._number_method(obj, method, args)
            raise RuntimeError_(f"No method '{method}' on {type(obj).__name__}")

        if isinstance(node, IndexNode):
            obj = self.eval_expr(node.obj, scope)
            idx = self.eval_expr(node.index, scope)
            if isinstance(obj, (list, str)): return obj[int(idx)]
            if isinstance(obj, dict):        return obj[idx]
            raise RuntimeError_(f"Cannot index {type(obj).__name__}")

        if isinstance(node, CallNode):
            func = self.eval_expr(node.func, scope)
            args = [self.eval_expr(a, scope) for a in node.args]
            return self._call_value(func, args, scope)

        raise RuntimeError_(f"Cannot evaluate node: {type(node).__name__}")

    def _eval_binop(self, node, scope):
        op = node.op
        # short-circuit
        if op == "and":
            l = self.eval_expr(node.left, scope)
            return l if not self._to_bool(l) else self.eval_expr(node.right, scope)
        if op == "or":
            l = self.eval_expr(node.left, scope)
            return l if self._to_bool(l) else self.eval_expr(node.right, scope)

        l = self.eval_expr(node.left, scope)
        r = self.eval_expr(node.right, scope)

        if op == "+":
            if isinstance(l, str) or isinstance(r, str):
                return self._to_str(l) + self._to_str(r)
            return l + r
        if op == "-":  return l - r
        if op == "*":
            if isinstance(l, str) and isinstance(r, int): return l * r
            return l * r
        if op == "/":  return l / r
        if op == "//": return l // r
        if op == "%":  return l % r
        if op == "**": return l ** r
        if op == "==": return l == r
        if op == "!=": return l != r
        if op == "<":  return l < r
        if op == ">":  return l > r
        if op == "<=": return l <= r
        if op == ">=": return l >= r
        raise RuntimeError_(f"Unknown operator: {op}")

    def _call_value(self, func, args, scope):
        if isinstance(func, str) and func.startswith("__builtin__"):
            name = func[len("__builtin__"):]
            return self._call_builtin(name, args, scope)
        if isinstance(func, NovaFunction):
            return self._call_function(func, args)
        if callable(func):
            return func(*args)
        raise RuntimeError_(f"Not callable: {func!r}")

    def _call_function(self, func: NovaFunction, args):
        local = Scope(func.closure)
        for i, p in enumerate(func.params):
            if i < len(args):
                local.declare(p, args[i])
            elif p in func.defaults:
                local.declare(p, self.eval_expr(func.defaults[p], func.closure))
            else:
                raise RuntimeError_(f"Missing argument: '{p}'")
        try:
            self.exec_body(func.body, local)
        except ReturnSignal as r:
            return r.value
        return None

    # ── Execute a list of statements
    def exec_body(self, stmts, scope: Scope):
        for stmt in stmts:
            self.exec_stmt(stmt, scope)

    # ── Execute one statement
    def exec_stmt(self, node, scope: Scope):
        try:
            result = self._exec_stmt_inner(node, scope)
            if self.feed_mode:
                print("feed - Valid")
            return result
        except (BreakSignal, ContinueSignal, ReturnSignal):
            raise
        except Exception as e:
            if self.feed_mode:
                print(f"feed - Invalid {e}")
            else:
                raise

    def _exec_stmt_inner(self, node, scope: Scope):

        if isinstance(node, AssignNode):
            val = self.eval_expr(node.value, scope)
            if node.declare:
                scope.declare(node.name, val)
            else:
                scope.set(node.name, val)
            return val

        if isinstance(node, AugAssignNode):
            cur = scope.get(node.name)
            val = self.eval_expr(node.value, scope)
            op  = node.op[0]  # + - * /
            new = BinOpNode(NumberNode(cur), op, NumberNode(val))
            # direct calc
            if op == "+": res = cur + val
            elif op == "-": res = cur - val
            elif op == "*": res = cur * val
            elif op == "/": res = cur / val
            else: raise RuntimeError_(f"Unknown aug op: {node.op}")
            scope.set(node.name, res)
            return res

        if isinstance(node, DelNode):
            scope.delete(node.name)
            return None

        if isinstance(node, SayNode):
            parts = []
            for a in node.args:
                v = self.eval_expr(a, scope)
                parts.append(self._to_str(v))
            print("".join(parts))
            return None

        if isinstance(node, WaitNode):
            t = self.eval_expr(node.duration, scope)
            time.sleep(float(t))
            return None

        if isinstance(node, FeedNode):
            self.feed_mode = (node.mode == "on")
            return None

        if isinstance(node, ExecNode):
            return self._exec_target(node.target, scope)

        if isinstance(node, GetNode):
            return self._exec_get(node, scope)

        if isinstance(node, HelpNode):
            page = node.page.lower()
            content = HELP_PAGES.get(page, HELP_PAGES.get("index"))
            print(content)
            return None

        if isinstance(node, IfNode):
            for cond, body in node.branches:
                if self._to_bool(self.eval_expr(cond, scope)):
                    local = Scope(scope)
                    self.exec_body(body, local)
                    return None
            if node.else_body is not None:
                local = Scope(scope)
                self.exec_body(node.else_body, local)
            return None

        if isinstance(node, WhileNode):
            while self._to_bool(self.eval_expr(node.condition, scope)):
                local = Scope(scope)
                try:
                    self.exec_body(node.body, local)
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue
            return None

        if isinstance(node, ForNode):
            iterable = self.eval_expr(node.iterable, scope)
            if not hasattr(iterable, "__iter__"):
                raise RuntimeError_(f"Not iterable")
            for item in iterable:
                local = Scope(scope)
                local.declare(node.var, item)
                try:
                    self.exec_body(node.body, local)
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue
            return None

        if isinstance(node, BreakNode):    raise BreakSignal()
        if isinstance(node, ContinueNode): raise ContinueSignal()
        if isinstance(node, ReturnNode):
            raise ReturnSignal(self.eval_expr(node.value, scope))

        if isinstance(node, FuncDefNode):
            fn = NovaFunction(node.name, node.params, node.defaults, node.body, scope)
            scope.declare(node.name, fn)
            return fn

        if isinstance(node, GroupDefNode):
            g = NovaGroup(node.name, node.body)
            self.groups[node.name] = g
            scope.declare(node.name, g)
            return g

        if isinstance(node, MacroDefNode):
            self.macros[node.name] = node.code
            return None

        if isinstance(node, TryCatchNode):
            try:
                local = Scope(scope)
                self.exec_body(node.try_body, local)
            except (BreakSignal, ContinueSignal, ReturnSignal):
                raise
            except Exception as e:
                local = Scope(scope)
                local.declare(node.err_var, str(e))
                self.exec_body(node.catch_body, local)
            return None

        if isinstance(node, ImportNode):
            return self._exec_import(node, scope)

        if isinstance(node, ExportNode):
            # no-op in runtime; handled by module loader
            return None

        # Macro call (ident that matches a macro, before eval_expr raises undefined)
        if isinstance(node, IdentNode) and node.name in self.macros:
            self._run_macro(node.name, scope)
            return None

        # Bare keyword builtins: clear, exit, quit (no parens needed)
        if isinstance(node, IdentNode) and node.name in ("clear", "exit", "quit"):
            return self._call_builtin(node.name, [], scope)

        # Expression statement
        result = self.eval_expr(node, scope)
        return result

    def _exec_target(self, target: str, scope: Scope):
        # macro
        if target in self.macros:
            self._run_macro(target, scope)
            return None

        # module.group
        if "." in target:
            mod_name, group_name = target.split(".", 1)
            if mod_name in self.modules:
                mod = self.modules[mod_name]
                g   = mod.scope.vars.get(group_name)
                if isinstance(g, NovaGroup):
                    self.exec_body(g.body, self.global_scope)
                    return None
            raise RuntimeError_(f"Module '{mod_name}' or group '{group_name}' not found")

        # group
        if target in self.groups:
            self.exec_body(self.groups[target].body, scope)
            return None

        # variable holding code string
        if scope.has(target):
            val = scope.get(target)
            if isinstance(val, str):
                self.run_source(val)
                return None
            if isinstance(val, NovaGroup):
                self.exec_body(val.body, scope)
                return None

        # file
        filepath = target if target.endswith(".nv") else target + ".nv"
        candidates = [filepath, os.path.join(self.source_dir, filepath)]
        for c in candidates:
            if os.path.exists(c):
                with open(c, "r", encoding="utf-8") as f:
                    self.run_source(f.read())
                return None
        raise RuntimeError_(f"Cannot exec '{target}': not a group, variable, or file")

    def _exec_get(self, node: GetNode, scope: Scope):
        if node.source == "pip":
            subprocess.run([sys.executable, "-m", "pip", "install", node.name], check=True)
        elif node.source == "source":
            print(f"[nova] Installing '{node.name}' from Nova registry (stub)...")
        elif node.source == "git":
            url = node.extra or ""
            subprocess.run(["git", "clone", url, node.name], check=True)
        elif node.source == "url":
            url = node.extra or node.name
            try:
                with urllib.request.urlopen(url, timeout=10) as r:
                    body = r.read().decode("utf-8")
                if node.mode == "var":
                    scope.declare(node.name, body)
            except Exception as e:
                raise RuntimeError_(f"GET request failed: {e}")
        return None

    def _exec_import(self, node: ImportNode, scope: Scope):
        filepath = node.filepath
        candidates = [filepath, os.path.join(self.source_dir, filepath)]
        for c in candidates:
            if os.path.exists(c):
                with open(c, "r", encoding="utf-8") as f:
                    src = f.read()
                sub = Interpreter(source_dir=os.path.dirname(c))
                sub.run_source(src)
                mod = NovaModule(sub.global_scope)
                self.modules[node.alias] = mod
                scope.declare(node.alias, mod)
                return None
        raise RuntimeError_(f"Cannot import '{node.filepath}': file not found")

    def _run_macro(self, name, scope):
        code = self.macros[name]
        self.run_source(code, scope=scope)

    def run_source(self, source: str, scope: Scope = None):
        if scope is None:
            scope = self.global_scope
        try:
            tokens = Lexer(source).tokenize()
            tree   = Parser(tokens).parse_program()
            for stmt in tree.statements:
                self.exec_stmt(stmt, scope)
        except (BreakSignal, ContinueSignal):
            pass
        except ReturnSignal as r:
            return r.value


# ─────────────────────────────────────────────
#  REPL
# ─────────────────────────────────────────────

def run_repl():
    print(f"Nova {VERSION}  (type 'help' for help, Ctrl+C to exit)")
    interp = Interpreter(source_dir=".")
    buf = []
    depth = 0
    while True:
        try:
            prompt = "... " if buf else ">>> "
            line   = input(prompt)
        except KeyboardInterrupt:
            print("\nBye.")
            break
        except EOFError:
            break

        depth += line.count("(") - line.count(")")
        buf.append(line)

        if depth <= 0:
            source = "\n".join(buf)
            buf    = []
            depth  = 0
            if source.strip():
                try:
                    interp.run_source(source)
                except Exception as e:
                    print(f"Error: {e}")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(f"Nova {VERSION}")
        print("Usage:")
        print("  nova <file.nv>     Run a Nova source file")
        print("  nova               Start the REPL")
        print("  nova -v            Show version")
        return

    if args[0] in ("-v", "--version"):
        print(f"Nova {VERSION}")
        return

    filepath = args[0]
    if not os.path.exists(filepath):
        print(f"nova: file not found: {filepath}")
        sys.exit(1)

    source_dir = str(Path(filepath).parent.resolve())
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    interp = Interpreter(source_dir=source_dir)
    try:
        interp.run_source(source)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        run_repl()
    else:
        main()
