#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#CST:xkaras27

import argparse, sys, os, re, codecs

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
        self.parser = argparse.ArgumentParser(add_help=False, \
            description='Process CStats commands')
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

        self.parser.add_argument('--input', action='append')
        self.parser.add_argument('--output', action='append')
        self.parser.add_argument('--nosubdir', action='append_const', const='1')
        self.parser.add_argument('-p', action='append_const', const='1')

        self.action_group = self.parser.add_mutually_exclusive_group(required=True)
        self.action_group.add_argument('-k', action='append_const', const='k', dest='switch')
        self.action_group.add_argument('-o', action='append_const', const='o', dest='switch')
        self.action_group.add_argument('-i', action='append_const', const='i', dest='switch')
        self.action_group.add_argument('-w', action='append', dest='pattern')
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
                print('Switch [-' + self.arguments.switch[0] + '] was given more than once.', \
                    file=sys.stderr)
                sys.exit(1)

        #absolutni cesta
        if self.arguments.p != None:
            if len(self.arguments.p) == 1:
                self.result_values['p'] = True
            else:
                print('Switch [-' + self.arguments.p[0] + '] was given more than once.', \
                    file=sys.stderr)
                sys.exit(1)

        #pattern
        if self.arguments.pattern != None:
            if len(self.arguments.pattern) == 1:
                self.result_values['pattern'] = self.arguments.pattern[0]
            else:
                print('Switch [-w] was given more than once.', \
                    file=sys.stderr)
                sys.exit(1)

        #input
        if self.arguments.input != None:
            if len(self.arguments.input) == 1:
                self.result_values['input'] = self.arguments.input[0]
            else:
                print('Switch [--input] was given more than once.', \
                    file=sys.stderr)
                sys.exit(1)
        #output
        if self.arguments.output != None:
            if len(self.arguments.output) == 1:
                self.result_values['output'] = self.arguments.output[0]
            else:
                print('Switch [--output] was given more than once.', \
                    file=sys.stderr)
                sys.exit(1)

        #nosubdir
        if self.arguments.nosubdir != None:
            if len(self.arguments.nosubdir) == 1:
                self.result_values['nosubdir'] = True
            else:
                print('Switch [--nosubdir] was given more than once.', file=sys.stderr)
                sys.exit(1)

        return self.result_values


class ProcessText():
    """
    Nastaveni pozadovanych akci i samotne prochazeni textu.
    """
    key_words = ['auto', 'break', 'case', 'char', 'const', 'continue',
                 'default', 'do', 'double', 'else', 'enum', 'extern',
                 'float', 'for', 'goto','if', 'inline', 'int', 'long',
                 'register', 'restrict', 'return', 'short', 'signed',
                 'sizeof', 'static', 'struct', 'switch','typedef',
                 'union', 'unsigned', 'void', 'volatile', 'while',
                 '_Bool', '_Complex', '_Imaginary' ]



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
                self.files = [os.path.abspath(os.path.join(r,f)) for r,d,fs in \
                os.walk(self.arguments['input']) \
                for f in fs if f.endswith('.c') or f.endswith('.h')]
            # Soubor predany argumenty.
            else:
                self.files = [os.path.abspath(self.arguments['input'])]
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
        """
        Pruchod analizovanymi soubory a volani metod
        k provedeni analizy nad danym souborem.
        """
        result = 0
        self.total = 0
        self.data = {}
        for source_file in self.files:
            try:
                with codecs.open(source_file, 'r', 'iso-8859-2') as f:
                    file_content = f.read()

                    # Pattern.
                    if self.arguments['pattern'] != None:
                        result = self.find_pattern(file_content)
                    # Klicova slova.
                    elif self.arguments['switch'] == 'k':
                        self.find_comments(file_content)
                        result = self.find_id_or_key(self.delete_backslash(self.delete_strings(self.delete_macros(self.delete_literals(self.no_comments)))), False)
                    # Identifikatory
                    elif self.arguments['switch'] == 'i':
                        self.find_comments(file_content)
                        result = self.find_id_or_key(self.delete_backslash(self.delete_strings(self.delete_macros(self.no_comments))), True)
                        
                        # result = self.key_words(self.delete_strings(self.delete_macros(self.no_comments)))
                    # Komentare.
                    elif self.arguments['switch'] == 'c':
                        result = self.find_comments(file_content)
                    elif self.arguments['switch'] == 'o':
                        self.find_comments(file_content)
                        result = self.find_operators(self.delete_literals(self.delete_strings(self.delete_macros(self.no_comments))))
                    # Aktualizace poctu vyskytu.
                    self.data[source_file] = result
                    self.total += result

            except EnvironmentError:
                print("Couldn't read input file [" + source_file + "]", file=sys.stderr)
                if os.path.isdir(self.arguments['input']):
                    sys.exit(21)
                else:    
                    sys.exit(2)

    def form_output(self):
        """
        Vytvoreni vystupniho retezce programu.
        """
        max_key = 0
        max_value = 0
        final_string = ""

        # Pokud byl zadan prepina -p, oreze se cesta souboru.
        if self.arguments['p']:
            temp = {}
            for key, value in self.data.items():
                temp[key.split('/')[-1]] = value
            self.data = temp

        # Nalezeni nejdelsiho radku.
        for key, value in self.data.items():
            if max_key < len(key):
                max_key = len(key)
            if max_value < len(str(value)):
                max_value = len(str(value))

        # Pokud je radek prilis kratky, pouzije se imlicitni hodnota.
        if max_key < 7:
            max_key = 7
        if max_value < len(str(self.total)):
            max_value = len(str(self.total))

        # Serazeni vystupu.
        for key in sorted(self.data.keys()):
            final_string += key  + ' ' * int(max_key-len(key)+1) + ' ' \
            * int(max_value - len(str(self.data[key]))) + str(self.data[key]) + '\n'
        
        final_string += "CELKEM: " + ' ' *  int(max_key-len("CELKEM: ")+1) + ' ' \
                        * int(max_value - len(str(self.total))) + str(self.total) + '\n'
        return final_string

    def print_output(self):
        """
        Vytisknuti vystupu programu bud na STDOUT
        nebo do souboru.
        """
        output_string = self.form_output()

        if self.arguments['output'] == None:
            print(output_string)
        else:
            try:
                with open(os.path.abspath(self.arguments['output']), 'w') as o:
                    o.write(output_string)
            except EnvironmentError:
                print("Couldn't read output file [" + self.arguments['output'] + "]", file=sys.stderr)
                sys.exit(3)
 
    def find_pattern(self, file_content):
        """
        Prepinac -w.
        """
        if self.arguments['pattern'] != '':
            return file_content.count(self.arguments['pattern'])
        else:
            return 0

    def find_operators(self, file_content):
        """

        """
        print(file_content)
        return 0

    def find_id_or_key(self, file_content, to_be_returned):
        """
        Spocitani vyskytu identifikatoru nebo klicovych slov.
        Implementovano pomoci konecneho automatu.
        Nejprve jsou odstraneny vsechny nezadouci operatory.
        Pote jsou hledany vsechny identifikatory. Nalezene
        identifkatory jsou porovnany s tabulkou klicovych
        slov. Pocita se tedy vyskyt identifikatoru i klicovych
        slov zaroven.

        @param to_be_returned Pokud je True, vraci se identifkatory,
        jinak se vraci pocet vyskytu klicovych slov.
        """
        INIT = 0
        IDENTIFIER = 1
        state = INIT
        clean_text = ""

        for line in file_content.split('\n'):
            line = re.sub(r'\(', r' ', line)
            line = re.sub(r'\)', r' ', line)
            line = re.sub(r'\{', r' ', line)
            line = re.sub(r'\}', r' ', line)
            line = re.sub(r'\*', r' ', line)
            line = re.sub(r';', r' ', line)
            line = re.sub(r',', r' ', line)
            line = re.sub(r']', r' ', line)
            line = re.sub(r'\[', r' ', line)
            line = re.sub(r'\.', r' ', line)
            line = re.sub(r'-', r' ', line)
            line = re.sub(r'\+', r' ', line)
            line = re.sub(r':', r' ', line)
            line = re.sub(r'!', r' ', line)
            line = re.sub(r'\|', r' ', line)
            line = re.sub(r'/', r' ', line)
            line = re.sub(r'>', r' ', line)
            line = re.sub(r'<', r' ', line)
            line = re.sub(r'%', r' ', line)
            line = re.sub(r'\^', r' ', line)
            line = re.sub(r'&', r' ', line)
            line = re.sub(r'=', r' ', line)
            line = re.sub(r'\?', r' ', line)
            line = re.sub(r'~', r' ', line)

            clean_text += line

        found_words = []
        for word in clean_text.split():
            for i in range(len(word)):

                if state == INIT:
                    if i == 0 and len(word) == 1 and (word[0].isalpha() or word[0] == '_'):

                        # Je to identifikator.
                        found_words.append(word)

                    elif word[i].isalpha() or word[i] == '_':
                        state = IDENTIFIER
                    else:
                        break

                elif state == IDENTIFIER:
                    if i == len(word)-1:
                        if word[i].isalnum() or word[i] == '_':
                            # Je to identifikator.
                            found_words.append(word)
                            state = INIT
                        else:
                            state = INIT
                    else:
                        if word[i].isalnum() or word[i] == '_':
                            pass # Je to identifikator. 
                        else:
                            state = INIT

        found_key_words = 0
        found_identifiers = 0
        for i in found_words:
            if i in self.key_words:
                found_key_words += 1
            else:
                found_identifiers += 1

        if to_be_returned:
            return found_identifiers
        else:
            return found_key_words

    def delete_backslash(self, file_content):
        """
        Odstraneni zpetnych lomitek (escape sekvenci).
        Pred volanim teto metody je treba odstranit stringy.
        """
        INIT = 0
        BACKSLASH = 1
        state = INIT
        final_string = ""

        for char in file_content:
            if state == INIT:
                if char == '\\':
                    state = BACKSLASH
                else:
                    final_string += char
            elif state == BACKSLASH:
                if char == '\n':
                    state = INIT

        # print(final_string)
        return final_string

    def delete_macros(self, file_content):
        """
        Odstraneni maker ze zdrojoveho kodu.
        Implementovano pomoci regularnich
        vyrazu jazyka Python.
        """
        multi_line_macro = re.compile(r'^\s*#.*\\\s*$')
        one_line_macro = re.compile(r'^\s*#.*$')
        continuous_macro = re.compile(r'^.*\\\s*$')
        final_string = ""
        # Bylo na predchozim radku makro?
        previous = False

        for line in file_content.split('\n'):
            # Pokud soucasny radek neni pokracovanim
            # makra z predchoziho radku.
            if not previous:
                if(multi_line_macro.match(line)):
                    previous = True
                    continue

                if(one_line_macro.match(line)):
                    continue
            # Je pokracovanim z predchoziho radku.
            else:
                if(continuous_macro.match(line)):
                    continue
                else:
                    previous = False
                    continue
            final_string += line + '\n'
        return final_string

    def delete_strings(self, file_content):
        """
        Odstraneni retezcu ze zdrojoveho kodu.
        Implementovano pomoci DFA.
        """
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
        """
        Odstraneni znakovych literalu ze zdrojoveho kodu.
        Implementovano pomoci DFA.
        """
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
        """
        Spocitani znaku komentare.
        Implementovano pomoci DFA.
        Zaroven je formovan retezec neobsahujici komentare.
        """
        i = 0
        i_aux = 0
        final_string = ""
        INIT = 0
        COM1 = 1
        COM2 = 2
        COM3 = 3
        COM4 = 4
        COM5 = 5
        STRING_S = 6
        COM2_2 = 7
        state = INIT
        flag = False  # V hranicnim pripade dovoluje snizit promennou i.

        for char in file_content:

            # Zacatek v INIT.
            if state == INIT:
                final_string += char
                if char == '/':
                    state = COM1
                    i += 1
                elif char == '"':
                    state = STRING_S

            # Jedno lomitko '/'.
            elif state == COM1:
                if char == '/':
                    final_string = final_string[:-1]
                    if flag:
                        final_string = final_string[:-i_aux]
                        i += i_aux
                        i_aux = 0
                        flag = False
                    state = COM2
                    i += 1
                elif char == '*':
                    final_string = final_string[:-1]
                    state = COM3
                    i += 1
                elif char == '\\':
                    final_string += char
                    state = COM5
                    i += 1
                else:
                    state = INIT
                    i -= 1

            # Dve lomitka '/'.
            elif state == COM2:
                if char == '\n':
                    state = INIT
                    i += 1
                elif char == '\\':
                    state = COM2_2
                    i += 1
                else:
                    i += 1

            # Pokracovani na dalsim radku.
            elif state == COM2_2:
                if char == ' ' or char == '\t':
                    i += 1
                else:
                    state = COM2
                    i += 1

            # Viceradkovy komentar - zacatek.
            elif state == COM3:
                i += 1
                if char == '*':
                    state = COM4

            # Viceradkovy komentar - konec.
            elif state == COM4:
                i += 1
                if char == '/':
                    state = INIT
                elif char == '*':
                    pass
                else:
                    state = COM3

            # Preskoceni retezcu
            elif state == STRING_S:
                final_string += char
                if char == '"':
                    state = INIT

            # Specialni pripad pouziti lomitka '\'
            elif state == COM5:
                if char == ' ' or char == '\t':
                    final_string += char
                    pass
                elif char == '\n':
                    final_string += char
                    flag = True
                    i_aux += 1
                    state = COM1
                else:
                    final_string += char
                    state = INIT
                #     i -= 1
        self.no_comments = final_string
        return i


if __name__ == '__main__':
    initialiser = ProcessText()
    initialiser.check_input()
    initialiser.process_input()
    initialiser.print_output()

