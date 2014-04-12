#!/usr/bin/env python3
#CST:xkaras27

import argparse, sys, os

class Parsing():
    """
    Zpracovani argumentu prikazove radky.
    """

    def __init__(self):
        """
        Pri instanciaci je vytvoren objekt ArgumentParser
        a slovnik, ve kterem jsou ulozeny konkretni
        parametry programu.
        """
        self.parser = argparse.ArgumentParser(add_help=False, description='Process CStats commands')
        self.result_values = { 'input' : None,
                               'output' : None,
                               'nosubdir' : False,
                               'p' : False,
                               'switch' : None,
                               'pattern' : None }

    def run(self):
        """
        Provadi zpracovani argumentu prikazove radky
        pomoci modulu argparse.

        argparse pri chybe defaultne pise na STDERR
        a vraci kod 2. Proto je treba odchytit vyjimku
        a vratit kod odpovidajici zadani.  
        """
        if len(sys.argv) == 2 and sys.argv[1] == '--help':
            print("""usage: cst.py [-h] [--input INPUT] [--output OUTPUT] [--nosubdir] [-p]
              (-k | -o | -i | -w PATTERN | -c)""")

            sys.exit(0)

        self.parser.add_argument('--input', nargs=1, action='store')
        self.parser.add_argument('--output', nargs=1, action='store')
        self.parser.add_argument('--nosubdir', action='append_const', const='1')
        self.parser.add_argument('-p', action='append_const', const='1')

        self.action_group = self.parser.add_mutually_exclusive_group(required=True)
        self.action_group.add_argument('-k', action='append_const', const='k', dest='switch')
        self.action_group.add_argument('-o', action='append_const', const='o', dest='switch')
        self.action_group.add_argument('-i', action='append_const', const='i', dest='switch')
        self.action_group.add_argument('-w', nargs=1, action='store', dest='pattern')
        self.action_group.add_argument('-c', action='append_const', const='c', dest='switch')

        try:
            self.arguments = self.parser.parse_args()
        except :
            sys.exit(1)

        #prepinace
        if self.arguments.switch != None:
            if len(self.arguments.switch) == 1:
                self.result_values['switch'] = self.arguments.switch[0]
            else:
                print('Switch [-' + self.arguments.switch[0] + '] is ambiguous', file=sys.stderr)
                sys.exit(1)

        #absolutni cesta
        if self.arguments.p != None:
            if len(self.arguments.p) == 1:
                self.result_values['p'] = True
            else:
                print('Switch [-' + self.arguments.p[0] + '] is ambiguous', file=sys.stderr)
                sys.exit(1)

        #pattern
        if self.arguments.pattern != None:
            if len(self.arguments.pattern) == 1:
                self.result_values['pattern'] = self.arguments.pattern[0]
            else:
                print('Switch [-' + self.arguments.p[0] + '] is ambiguous', file=sys.stderr)
                sys.exit(1)

        #input
        if self.arguments.input != None:
            self.result_values['input'] = self.arguments.input[0]

        #output
        if self.arguments.output != None:
            self.result_values['output'] = self.arguments.output[0]

        #nosubdir
        if self.arguments.nosubdir != None:
            if len(self.arguments.nosubdir) == 1:
                self.result_values['nosubdir'] = True
            else:
                print('Switch [--nosubdir] is ambiguous', file=sys.stderr)
                sys.exit(1)

        return self.result_values


class ProcessText():
    """
    Nastaveni pozadovanych akci i samotne prochazeni textu.
    """
    def __init__(self):
        self.parse = Parsing()
        self.arguments = self.parse.run()

    def check_input(self):
        if self.arguments['nosubdir'] == False:
            if self.arguments['input'] == None:
                self.files = [os.path.join(r,f) for r,d,fs in os.walk(os.getcwd()) for f in fs if f.endswith('.c') or f.endswith('.h')]
            elif os.path.isdir(self.arguments['input']):
                self.files = [os.path.abspath(os.path.join(r,f)) for r,d,fs in os.walk(self.arguments['input']) for f in fs if os.path.isfile(f) and f.endswith('.c') or f.endswith('.h')]
            else:
                self.files = [self.arguments['input']]
        else:
            if self.arguments['input'] == None:
                self.files = [os.path.abspath(f) for f in os.listdir(os.getcwd()) if os.path.isfile(f) and (f.endswith('.c') or f.endswith('.h'))]
            elif os.path.isdir(self.arguments['input']):
                self.files = [os.path.abspath(f) for f in os.listdir(self.arguments['input']) if f.endswith('.c') or f.endswith('.h')] #TODO: nelze testovat, zda je soubor
            else:
                print('--input=file & --nosubdir cannot be combined', file=sys.stderr)
                sys.exit(1)
        
    def check_output(self):
        if self.arguments['output'] == None:
            self.output = 'sys.stdout'
        else:
            self.output = os.path.abspath(self.arguments['output'])

    def process_input(self):
        

    def find_pattern(self):
        pass

if __name__ == '__main__':
    initialiser = ProcessText()
    initialiser.check_input()
    initialiser.check_output()
