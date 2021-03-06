# AnkiAutoCards
A simple CLI tool to convert markdown files to Anki notes through multiple templates.

This utility tool can be used to parse a file, find occurrences according to
templates such as lists, proper nouns or tables, and add cards to your Anki
collection to study what you wrote down.

## Installation
To install this script, simply download the code, enter the directory and run
'pip install .'. If you're missing any dependencies, they will be installed.

## How to use
Help can be found with the '-h' or '--help' flags.
Here are some examples of what you can do with this script :

```bash
ankiautocards add -d Mathematics --model cloze '{{c1::1::Number}} + 1 = 2' 'Hard'
```
Adds a new cloze card to the "Mathematics" deck, with a main field and an extra
field.

The first parsing features are a WIP; coming soon !

## Contributing
Do not hesitate to add to your convenience new pattern-matchers !
Please try to respect the same structure as other parsers (verbose messages,
structure...) and to be as consistent and concise for the patterns you search
(each different pattern must be a new option), and then make a pull request.
