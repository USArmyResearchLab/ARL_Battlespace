# Style Guide for Source Code in ARL BattleSpaceAI

## Game Design
 - Game rules: rules on changes between states
 - State rules: which states are legal including which units are allowed.
 - Unit rules: unit specific rules in particular what actions can be taken and what a unit can observe.
 - Agent rules: rules on choosing options of the units or state options.

## General conventions

 - Individual classes are to be deposited in their own files ending in `.py`.
 - Every function class and variable is to be documented with a documentation string.
 - There will be a free line after each code block, not just a change in indent.
 - All names will be descriptive and special characters (`_`, `!`, `$`, etc.)  and numerals are to be avoided.

## Naming Variables

Variables are to be named in [CamelCase](https://en.wikipedia.org/wiki/Camel_case) beginning with an upper case letter.

## Naming functions

Functions should start with a verb and use [camelCase](https://en.wikipedia.org/wiki/Camel_case) beginning with a lower case letter.

## Call backs

Call back functions begin with `callBack_` or end with `_CallBack`.

## Indentation

All blocks are indented by 4 spaces.

## Miscellanea
- Comprehensions include a space ` ` on either side between the body of the comprehension and the enclosing delimiters. E.g. `{ a: b, c: d }`
- Punctuation is followed by a space ` ` as in `f(x, y)`, `{ a: b }` unless followed by a new line.
- abstract classes need to implement their virtual methods and raise `NotImplementedError`
