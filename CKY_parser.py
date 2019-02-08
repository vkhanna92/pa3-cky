# -*- coding: utf-8 -*-
"""
Created on Wed Oct 24 17:42:46 2018

@author: vkhanna
"""

import sys


def get_grammar(filename):
    '''
    get grammer from a file with specified format. In this case, the format of rules is as follows:
        S  NP VP\t 0.3...
    :param filename : grammer file name from the args
    :return: dictionary of parsed grammar rules
    '''
    with open(filename, 'r') as f:
        lines = f.readlines()
        grammar = [tuple(line.strip().split('\t')) for line in lines]
        
        
    grammar =tuple(tuple(b.rstrip() for b in a) for a in grammar)
    grammar = [tuple(filter(None, tp)) for tp in grammar]
    #print(grammar)
    dict_grammar = dict(grammar)
    return dict_grammar
    

def get_non_terminals(grammar):
    '''
    get_non_terms() returns a set of the non-terminal symbols from the grammar rules
    :param grammar: dictionary of grammar rules
    :return: a set of non_terms from the grammar
    '''
    non_terms = set()
    terms = set()
    for rules in grammar.keys():
        rule = rules.split(' ')
        rule = list(filter(None,rule))
        for r in rule:
            if r.isupper():
                non_terms.add(r)
            else:
                terms.add(r)
    #print("non-terms",non_terms)
    #print(terms)
    return non_terms

def init_parse_triangle(number_of_words,number_of_nonterm, fill_value=0):
    '''
    :param number_of_words:
    :param number_of_nonterm:
    :param fill_value: the value used to fill the parse triangle
    :return: a parse triangle with the params used as dimensions
    '''
    return [[[fill_value for i in range(number_of_nonterm)] for j in range(number_of_words)] for k in range(number_of_words)]

def get_binary_rules(grammar):
    '''
    get_binary_rules() searches through the grammar binary rules and returns them in a list
    :param grammar: dictionary of grammar rules
    :return: list of binary grammar rules
    '''
    bin_set = set()
    for rules in grammar:
        #print(rules.split(' '))
        if len(rules.split(' ')) == 4:
            rules = rules.split(' ')
            b, c = rules[2],rules[3]
            bin_set.add((rules[0],b,c))
            bin_set.add((rules[0], c, b))
    #print("bin set is ",bin_set)
    return list(bin_set)

def cky_parse(words,grammar):
    ''' 
    main CKY parsing algorithm
    cky_parse() takes a sentence as a bag of words and parses it according to the provided grammar.
    :param words: words in the sentence (list)
    :param grammar: list of grammar rule
    '''
    non_terms = list(get_non_terminals(grammar)) 

    score = init_parse_triangle(len(words)+1,len(non_terms))
    back = init_parse_triangle(len(words)+1,len(non_terms),-1)
    
    rule_index = {}
   
    #print("non_terms {0}".format(non_terms))
    
    #print("grammar {0}".format(grammar));\
    '''
    Get productions for terminals
    '''
    for i,word in enumerate(words):
        rules_used = []
        rules_not_used = []
        terminals_used = dict()
        s_list = list()
        for j,A in enumerate(non_terms):
            r = A + "  " + word
            #print("r is ",r)
            if r in grammar:
                #print(grammar[r])
                score[i][i+1][j] = float(grammar[r])
                if word in terminals_used.keys():
                    terminals_used[word].append(r)
                else:
                    s_list.append(r)
                    terminals_used[word] = s_list
                    
                rules_used.append(j)
                rule_index[A] = j
            else:
                score[i][i+1][j] = 0.0
                rules_not_used.append(j)
                rule_index[A] = j
        #print(terminals_used)
        
        '''Get production for Unary rules '''
        rules_used_temp = rules_used[:]
        rules_not_used_temp = rules_not_used[:]
        
        added = True
        while added:
            added = False
            for a in rules_not_used:
                for b in rules_used:
                    r = non_terms[a] + '  '+ non_terms[b]
                    
                    if r in grammar:
                       
                        prob = float(grammar[r]) * score[i][i+1][b]
                        if prob > score[i][i+1][a]:
                            '''set max score and backpointer associated '''
                            score[i][i+1][a] = prob
                            back[i][i+1][a] = b
                            rules_used_temp.append(a)
                            try:
                                rules_not_used_temp.remove(a)
                                rules_used_temp.remove(b)
                            except ValueError:
                                pass
                           
                            added = True

            rules_used = rules_used_temp[:]
            rules_not_used =rules_not_used_temp[:]

    binary_rules = get_binary_rules(grammar)
   # print(binary_rules)
    '''Get production for Binary rules '''
    for span in range(2,len(words)+1):
        for begin in range(len(words)+1-span):
            rules_used = []
            end = begin + span
            for split in range(begin+1, end):
                for rule in binary_rules:
                    a, b, c = rule_index[rule[0]], rule_index[rule[1]], rule_index[rule[2]]
                    concat_rule = rule[0] + '  ' + (rule[1] + ' ' + rule[2])
                    
                    if concat_rule in grammar:
                        #print("CONCAT ",concat_rule)
                        prob = float(score[begin][split][b]) * float(score[split][end][c])
                        prob = prob * float(grammar[concat_rule])
                    else:
                        continue
                    if prob > score[begin][end][a]:
                        '''set max score and backpointer associated '''
                        score[begin][end][a] = prob
                        back[begin][end][a] = split, b, c
                        rules_used.append(a)
                    #print("For i ",i," j ",i+1,"rule ",r, " prob ",prob)
    
            ### Handle Unaries
    added = True
    while added:
                added = False
                for a in range(len(non_terms)):
                    for b in rules_used:
                        r = non_terms[a] + '  ' + non_terms[b]
                        if r in grammar:
                            prob = float(grammar[r]) * score[begin][end][b]
                            if prob > score[begin][end][a]:
                                score[begin][end][a] = prob
                                back[begin][end][a] = b
                                added = True
                                
    pretty_print_matrix(score,len(words)+1,words,rules_used,non_terms,back,grammar)
    


def pretty_print_matrix(score,rows,words,rules_used,non_terms,back,grammar):
    '''Prints score and back pointer matrix according to given output'''
    row_temp = rows
    j = 0
    
    unique_rules = set(rules_used)
    for k in range(rows-1):
        flag = 1
        for i in range(row_temp):
                
                   if i+j+1 >= rows:
                        break
                   else:
                    print()
                           
                    print("SPAN: ",end = " ")
                    for m in range(i,i+j+1):
                        print(words[m], end=" ")
                    print()
                    #for a in unique_rules:
                    item = score[i][i+j+1]
                    if flag and (j+i+1)-i == 1:
                        word = words[i]
                        for a in non_terms:
                            rule = a + '  ' + word
                            if rule in grammar:
                                print("P(",rule,")=",grammar[rule])
                        
                                    
                    for a in unique_rules:
                        #print(b)
                        if item[a] > 0.0:
                            b = back[i][i+j+1][a]
                            if type(b) is not int:
                                f = b[1]
                                g = b[2]
                                print("P(",non_terms[a],")=",str(format(item[a], '.10f')).ljust(5),"(BackPointer =",b[0],",",non_terms[f],",",non_terms[g],")")
                            else:
                                print("P(",non_terms[a],")=",str(format(item[a], '.10f')).ljust(5),"(BackPointer =",non_terms[b],")")
                                  #"BACK POINTER(",non_terms[b],")",)
        row_temp = row_temp-1
        j = j + 1
        #print("rwotemp:",row_temp)

if __name__ == '__main__':
    grammar_file = sys.argv[1]
    sentence_file = sys.argv[2]
    #print(grammar_file)
    grammar = get_grammar(grammar_file)
    
    with open(sentence_file) as f:
        for line in f:
            words = line.strip().split()
            print("PROCESSING SENTENCE :",line)
            cky_parse(words,grammar)
    