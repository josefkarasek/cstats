#!/usr/bin/env python3
#CST:xkaras27

import argparse, sys, os, re

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
        """
        Dle prepinace input urci soubory k prohledani
        """
        # S prohledavanim do hloubky.
        if self.arguments['nosubdir'] == False:
            # Soucasny adresar.
            if self.arguments['input'] == None:
                self.files = [os.path.join(r,f) for r,d,fs in os.walk(os.getcwd()) \
                for f in fs if f.endswith('.c') or f.endswith('.h')]
            # Adresar predany argumenty.
            elif os.path.isdir(self.arguments['input']):
                self.files = [os.path.abspath(os.path.join(r,f)) for r,d,fs in os.walk(self.arguments['input']) \
                for f in fs if f.endswith('.c') or f.endswith('.h')]
            # Soubor predany argumenty.
            else:
                self.files = [self.arguments['input']]
        # Bez prohledavani do hloubky.
        else:
            # Soucasny adresar.
            if self.arguments['input'] == None:
                self.files = [os.path.abspath(f) for f in os.listdir(os.getcwd()) \
                if os.path.isfile(f) and (f.endswith('.c') or f.endswith('.h'))]
            # Adresar predany argumenty.
            elif os.path.isdir(self.arguments['input']):
                self.files = [os.path.abspath(os.path.join(os.path.abspath(self.arguments['input']), f)) \
                for f in os.listdir(os.path.abspath(self.arguments['input'])) \
                if f.endswith('.c') or f.endswith('.h')] #TODO: nelze testovat, zda je soubor
            else:
                print('Bad parameters', file=sys.stderr)
                sys.exit(1)

    def process_input(self):
        result = 0
        total = 0
        for file in self.files:
            try:
                with open(file) as f:
                    file_content = f.read()
                    # self.delete_strings(file_content)
                    # print(str(self.find_pattern(file_content)))
                    # self.delete_macros(file_content)

                    result = self.find_comments(file_content)
                    total += result
                    out = file + " " + comments + "\nCELKEM: " + comments + '\n'

            
                    o.write(out)

                    
                    # print("CELKEM: " + comments)
            except EnvironmentError:
                print("Couldn't read input file [" + file + "]", file=sys.stderr)
                sys.exit(2)

    def print_result(self, output_string):
        if self.arguments['output'] == None:
            print(output_string)
        else:
            try:
                with open(self.arguments['output'], 'w') as o:
                    o.write(output_string)
            except EnvironmentError:
                print("Couldn't read output file [" + self.arguments['output'] + "]", file=sys.stderr)
                    sys.exit(3)



    def find_pattern(self, file_content):
        i = 0;
        regex = re.compile(self.arguments['pattern'])
        for line in file_content.split('\n'):
            found = regex.findall(line)
            if(found):
                i += len(found)
        return i

    def key_words(self, file_content):
        pass

    def delete_macros(self, file_content):
        multi_line_macro = re.compile(r'^\s*#.*\\\s*$')
        one_line_macro = re.compile(r'^\s*#.*$')
        continuous_macro = re.compile(r'^.*\\\s*$')
        final_string = ""
        # Bylo na predchozim radku makro?
        previous = False

        for line in file_content.split('\n'):
            if not previous:
                if(multi_line_macro.match(line)):
                    previous = True
                    continue

                if(one_line_macro.match(line)):
                    continue
            else:
                if(continuous_macro.match(line)):
                    continue
                else:
                    previous = False
                    continue
            final_string += line + '\n'
        return final_string

    def delete_strings(self, file_content):
        INIT = 0
        S_STRING = 1
        state = INIT
        final_string = ""

        for char in file_content:
            if state == INIT:
                if char == '"':
                    state = S_STRING
                else:
                    final_string += char

            elif state == S_STRING:
                if char == '"':
                    state = INIT
        return final_string

    def delete_literals(self, file_content):
        INIT = 0
        S_LITERAL = 1
        state = INIT
        final_string = ""

        for char in file_content:
            if state == INIT:
                if char == "'":
                    state = S_LITERAL
                else:
                    final_string += char

            elif state == S_LITERAL:
                if char == "'":
                    state = INIT
        return final_string

    def find_comments(self, file_content):
        i = 0
        INIT = 0
        COM1 = 1
        COM2 = 2
        COM3 = 3
        COM4 = 4
        COM5 = 5
        STRING_S = 6
        COM2_2 = 7
        state = INIT

        for char in file_content:

            if state == INIT:
                if char == '/':
                    state = COM1
                    i += 1
                elif char == '"':
                    state = STRING_S

            elif state == COM1:
                if char == '/':
                    state = COM2
                    i += 1
                elif char == '*':
                    state = COM3
                    i += 1
                elif char == '\\':
                    state = COM5
                    i += 1
                else:
                    state = INIT
                    i -= 1

            elif state == COM2:
                if char == '\n':
                    state = INIT
                    i += 1
                elif char == '\\':
                    state = COM2_2
                    i += 1
                else:
                    i += 1

            elif state == COM2_2:
                if char == ' ' or char == '\t':
                    i += 1
                else:
                    state = COM2
                    i += 1

            elif state == COM3:
                i += 1
                if char == '*':
                    state = COM4

            elif state == COM4:
                i += 1
                if char == '/':
                    state = INIT
                elif char == '*':
                    continue
                else:
                    state = COM3

            elif state == STRING_S:
                if char == '"':
                    state = INIT

            elif state == COM5:
                if char == ' ' or char == '\t':
                    continue
                elif char == '\n':
                    state = COM1
                else:
                    state = INIT

        return i
        # is_comment = False
        # One line comment --> True. Multiline --> False.
        # one_liner = True
        # previous = False
        # S_INIT = 0
        # S_1 = 1
        # S_2 = 2
        # S_3 = 3
        # S_4 = 4
        # S_STRING_S = 5
        # S_STRING_E = 6
        # S_2_S = 7

        # state = S_INIT

        # for char in file_content:
        #     # INIT
        #     if state == S_INIT:
        #         if char == '/':
        #             state = S_1
        #             i += 1
        #         elif char == '"':
        #             state = S_STRING_S

        #     # SCOM1
        #     elif state == S_1:
        #         if char == '/':
        #             i += 1
        #             state = S_2
        #         elif char == '*':
        #             i += 1
        #             state = S_3
        #         elif char == '\\':
        #             i += 1
        #             state = S_2_S
        #         else:
        #             i -= 1
        #             state = S_INIT

        #     # SCOM2
        #     elif state == S_2:
        #         if char == '\n':
        #             i += 1
        #             state = S_INIT
        #         elif char == '\\':
        #             i += 1
        #             state = S_2_S
        #         else:
        #             i += 1
        #             state = S_2

        #     # SCOM2_POM
        #     elif state == S_2_S:
        #         i += 1
        #         state = S_2


        #     elif state == S_3:
        #         if char == '*':
        #             i += 1
        #             state = S_4
        #         else:
        #             i += 1
        #             state = S_3

        #     elif state == S_4:
        #         if char == '/':
        #             i += 1
        #             state = S_INIT
        #         elif char == '*':
        #             i += 1
        #             state = S_4
        #         else:
        #             i += 1
        #             state = S_3


        #     elif state == S_STRING_S:
        #         if char == '"':
        #             state = S_INIT

        
            #     elif char == '\\':
            #         state = S_STRING_E

            # elif state == S_STRING_E:
            #     if char == '\n':
            #         state = S_STRING_S








        #     if char == '\n':
        #         print()
        #         print("Znaku: " + str(i))

        #     if not is_comment:
        #         if previous == False and char == '/':
        #             previous = True
        #         elif previous == True and char == '/':
        #             is_comment = True
        #             one_liner = True
        #             previous = False
        #             i += 2
        #             print("//", end="")
        #         elif previous == True and char == '*':
        #             is_comment = True
        #             one_liner = False
        #             previous = False
        #             i += 2
        #             print("/*", end="")
        #         elif previous == True and char != '*' and char != '/':
        #             previous = False
        #     else:
        #         i += 1
        #         print(char, end="")
        #         if one_liner and char == '\n':
        #             is_comment = False
        #         if not one_liner and char == '*':
        #             previous = True
        #         if previous and not one_liner and char == '/':
        #             is_comment = False
        #             previous = False



if __name__ == '__main__':
    initialiser = ProcessText()
    initialiser.check_input()
    initialiser.check_output()
    initialiser.process_input()
