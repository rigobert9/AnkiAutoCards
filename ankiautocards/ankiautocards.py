#!/usr/bin/env python3.10
# General-purpose Anki card-creating script, with parsing of notes or quick
# adding

# Create a new config file id it does not exist, and import it to use aliases
# for decks (for example).
from os import path
from sys import exit
from subprocess import check_output
from anki.storage import Collection
import argparse
import re

# The parsers' short name, long name, their default value, help string and regex
PARSERS = [
        ("V", "vocabulary", "Basic",
        "search for vocabulary tables (word |translation), uses 'Basic' by \
        default"),
        ]
# The expressions associated with each parsers' name
EXPRESSIONS = {
        "vocabulary": re.compile(r''),
        }

def getDefaultHome() -> str:
    # Find the Anki directory
    # To Do: Add support for AnkiDroid
    home = path.expanduser("~")
    anki_home = path.join(home, '.local',  'share',  'Anki2', 'User 1')
    anki_collection_path = path.join(anki_home, "collection.anki2")
    return anki_collection_path

def preprocess(func):
    def wrapper(args):
        # 0. Check for the verbose option
        if args.v:
            def info(message):
                print(message)
        else:
            def info(message):
                pass
        info(f"Passed arguments : {args}")

        # 1. Load the anki collection
        if args.path is None:
            args.path = getDefaultHome()
        info(f"Getting collection from {args.path}")
        col = Collection(args.path, log=True)

        # 2. Select the deck
        deck = col.decks.by_name(args.deck)
        col.decks.select(deck['id'])

        # 3. Create the cards, according to the action
        func(args, col, deck, info)

        # 4. Save changes
        if args.dry_run:
            info("Discarding changes")
        else:
            info("Saving collection.")
            col.save()
    return wrapper

@preprocess
def note(args, col, deck, info) -> None:
    # Getting the model used
    modelBasic = col.models.by_name(args.model)
    col.decks.current()['mid'] = modelBasic['id']
    # Check if number of fields corresponds to the number of fields
    info("Creating note")
    note = col.newNote()
    info("Checking number of fields")
    if (maxfields := len(note.fields)) >= len(args.fields):
        for i in range(len(args.fields)):
            note.fields[i] = args.fields[i]
        col.add_note(note, deck['id'])
    else:
        print(f"Number of fields given is inadequate : {maxfields} fields were \
                expected but {len(args.fields)} were given.")
        exit(1)

@preprocess
def parse(args, col, deck, info) -> None:
    # To put in expressions ?
    re.M = True # Try multiline regexes ?
    re.S = True # . matches newline
    re.X = True # commented regexes
    expressions = []
    for fil in args.files:
        with open(fil) as text:
            for parser in args.parsers:
                info(f"Getting the card model {parser[1]}")
                modelBasic = col.models.by_name(parser[1])
                col.decks.current()['mid'] = modelBasic['id']
                results = EXPRESSIONS[parser[0]].findall(text)
                # To do: check for the number of fields
                for result in results:
                    info(f"Creating note with data: {result}")
                    note = col.newNote()
                    for i in range(len(result)):
                        note.fields[i] = result[i]
                    col.add_note(note, deck['id'])

# Action class for argparser to deal with custom models for cards in parsers
class ActionCustomModel(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super().__init__(option_strings, dest, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, self.dest + [(values)])

def main():
    # Getting args
    argparser = argparse.ArgumentParser(\
            formatter_class = argparse.RawDescriptionHelpFormatter,
            description = \
"""Add, delete and parse files for Anki flashcards.""")
    argparser.add_argument("-d", "--deck", type=str, default='Default', \
            help="the deck to interact with")
    argparser.add_argument("-p", "--path", type=str, \
            help="the path to the database")
    argparser.add_argument("-v", action='store_true', \
            help="activate verbose mode")
    argparser.add_argument('--dry-run', action='store_true', \
            help="perform a dry run")

    # Subparsers for the subcommands
    subparsers = argparser.add_subparsers(help="actions to choose from")
    ## note
    parser_note = subparsers.add_parser('note', \
            help="create a new note to generate cards")
    parser_note.add_argument('fields', nargs='+', \
            help="the fields of the new note to create")
    parser_note.add_argument("-m", "--model", type=str, default='Basic', \
            help="the card model to use")
    parser_note.set_defaults(func=note)
    ## parse
    parser_parse = subparsers.add_parser('parse', \
            description=\
            "Use the parsing options to create notes from a markdown text.\
            Each parser option has a ~1 option, which can be followed by a \
            model of your choice, instead of the default template fit for \
            the parser.")
    for PARSER in PARSERS: # Create all parsers
        parser_parse.add_argument(f"-{PARSER[0]}", f"--{PARSER[1]}",\
                action='append_const', const=(PARSER[1],PARSER[2]), \
                dest="parsers", \
                help=f"{PARSER[3]}")
        parser_parse.add_argument(f"--{PARSER[0]}1", type=str, \
                action=ActionCustomModel, \
                default=f"{PARSER[2]}", metavar='model', \
                dest="parsers")
    # args.parsers ends up being a list of tuple, containing the type of parser
    # and the name of the model to use
    parser_parse.add_argument('files', nargs='+', \
            help="the list of files to parse")
    parser_parse.set_defaults(func=parse)

    # Parsing all arguments
    args = argparser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
