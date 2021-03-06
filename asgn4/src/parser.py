#!/usr/bin/env python3

import sys
import ply.yacc as yacc
from lexer import *
import symbol_table as st
from copy import deepcopy as dp

if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    print("Use as python parser.py file.cs")
    sys.exit

env = st.environment()
# Precedence
precedence = (
    ('left', 'CONOR'),
    ('left', 'CONAND'),
    ('left', 'OR'),
    ('left', 'XOR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NE'),
    ('left', 'GT', 'GEQ', 'LT', 'LEQ'),
    ('left', 'RSHIFT', 'LSHIFT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('right', 'TILDE', 'LNOT'),
    ('left', 'MEMBERACCESS', 'INCREMENT', 'DECREMENT')
)

"""
TODO: Arrays in method headers, check for var existance in return and function call
"""
def p_start(p):
    """start : compilation_unit
    """
    # p[0] = ['start', p[1]]
    p[0] = dp(p[1])

def p_compilation_unit(p):
    """compilation_unit : class_declarations
    | using_directives class_declarations
    """
    p[0] = {}
    if len(p) == 2:
        # p[0] = ['compilation_unit', p[1]]
        p[0]['code'] = p[1]['code']
    else:
        # p[0] = ['compilation_unit', p[1], p[2]]
        p[0]['code'] = p[1]['code'] + p[2]['code']

# USING #############################################################################
def p_using_directives(p):
    """using_directives : using_directive
    | using_directives using_directive
    """
    p[0] = {}
    if len(p) == 2:
        # p[0] = ['using_directives', p[1]]
        p[0]['code'] = p[1]['code']
    else:
        # p[0] = ['using_directives', p[1], p[2]]
        p[0]['code'] = p[1]['code'] + p[2]['code']

def p_using_directive(p):
    """using_directive : USING identifier TERMINATOR
    """
    p[0] = {}
    # p[0] = ['using_directive', 'USING', p[2], ';']
    p[0]['code'] = [""]

# CLASS #############################################################################
def p_class_declarations(p):
    """class_declarations : class_declarations class_declaration
    | class_declaration
    """
    p[0] = {}
    if len(p) == 3:
        p[0]['code'] = p[1]['code'] + p[2]['code']
    else:
        p[0]['code'] = p[1]['code']

def p_class_declaration(p):
    """class_declaration : modifiers CLASS identifier class_body TERMINATOR
    | CLASS identifier class_body TERMINATOR
    | CLASS identifier class_body
    | modifiers CLASS identifier class_body
    """
    p[0] = {}
    p[0]['category'] = 'function'    
    if len(p) == 6:
        # p[0] = ['class_declaration', p[1], 'CLASS', p[3], p[4], ';']
        p[0]['code'] = p[4]['code']
    elif len(p) == 4:
        # p[0] = ['class_declaration', 'CLASS', p[2], p[3], ';']
        p[0]['code'] = p[3]['code']
    elif p[1] == 'CLASS':
        # p[0] = ['class_declaration', 'CLASS', p[2], p[3], ';']
        p[0]['code'] = p[3]['code']
    else:
        # p[0] = ['class_declaration', p[1], 'CLASS', p[3], p[4], ';'];
        p[0]['code'] = p[4]['code']

def p_class_body(p):
    """class_body : LBRACE class_member_declarations RBRACE
    | LBRACE RBRACE
    """
    p[0] = {}
    if len(p) == 3:
        p[0]['code'] = ['']
        # p[0] = ['class_body', '{', '}']
    else:
        p[0]['code'] = p[2]['code']
        # p[0] = ['class_body', '{', p[2], '}']
        pass


def p_identifier(p):
    """identifier : IDENTIFIER
    """
    # p[0] = ['identifier', str(p[1])]
    p[0] = {}
    p[0]['value'] = str(p[1])
    p[0]['code'] = ['']

    # print(p[0])

def p_class_member_declarations(p):
    """class_member_declarations : class_member_declaration
    | class_member_declarations class_member_declaration
    """
    p[0] = {}
    if len(p) == 2:
        p[0]['code'] = p[1]['code']
        # p[0] = ['class_member_declerations', p[1]]
    else:
        p[0]['code'] = p[1]['code'] + p[2]['code']
        # p[0] = ['class_member_declerations', p[1], p[2]]

def p_class_member_declaration(p):
    """class_member_declaration : field_declaration
    | method_declaration
    | constructor_declaration
    | destructor_declaration
    """
    # p[0] = ['class_member_declaration', p[1]]
    p[0] = dp(p[1])

def p_field_declaration(p):
    """field_declaration : modifiers type variable_declarators TERMINATOR
    | type variable_declarators TERMINATOR
    """
    p[0] = {}
    if len(p) == 4:
        p[0]['code'] = ['']
        p[0]['value'] = None
        print(p[1])
        print(p[2])
        for var in p[2]:
            p[0]['code'] += var['code']
            if env.pres_env.lookup(var['name']) is None:
                if not p[1].dict['isarray']:
                    env.pres_env.enter_var(var['name'], p[1])
                else:
                    env.pres_env.enter_var(var['name'], p[1], 'arr')
            else:
                print('Error, var declared again')
        print('---------------------')
        print(p[0])
    else:
        p[0]['code'] = ['']
        p[0]['value'] = None
        for var in p[3]:
            p[0]['code'] += var['code']
            if env.pres_env.lookup(var['name']) is None:
                env.pres_env.enter_var(var['name'], p[2])
            else:
                print('Error, var declared again')


def p_type(p):
    """type : reference_type
    | type_parameter
    """
    # p[0] = ['type', p[1]]
    p[0] = dp(p[1])

def p_reference_type(p):
    """reference_type : class_type
                        | array_type
    """
    # p[0] = ['reference_type', p[1]]
    p[0] = dp(p[1])
    #TODO: Put the type for the corresponding identifier

def p_class_type(p):
    """class_type : proper_identifier
    | OBJECT
    """
    # p[0] = ['class_type', p[1]]
    # TODO: Do check for object
    # TODO : Find the data_width for this case
    if p[1] == 'object':
        # p[0] =
        pass
    p[0] = st.type(p[1]['value'], False, False, None, None, None)

def p_proper_identifier(p):
    """proper_identifier : prefix identifier
    """
    # p[0] = ['proper_identifier', p[1], p[2]]
    p[0] = {}
    p[0]['value'] = p[1]['value'] + p[2]['value']
    p[0]['code'] = ['']

def p_prefix(p):
    """prefix : identifier MEMBERACCESS
            | prefix identifier MEMBERACCESS
    """
    if len(p) == 3:
        # p[0] = ['prefix', p[1], '.']
        p[0] = {}
        p[0]['value'] = p[1]['value'] + str(p[2])
    else:
        # p[0] = ['prefix', p[1], p[2], '.']
        p[0] = {}
        p[0]['value'] = p[1]['value'] + p[2]['value'] + str(p[3])
    p[0]['code'] = ['']

def p_array_type(p):
    """array_type : non_array_type LBRACKET RBRACKET
    """
    # p[0] = ['array_type', p[1], '[', ']']
    p[0] = st.type(p[1], False, True, None, None, p[1])

def p_non_array_type(p):
    """non_array_type : type
    """
    # p[0] = ['non_array_type', p[1]]
    p[0] = dp(p[1])

def p_type_parameter(p):
    """type_parameter : identifier
    | predefined_type
    """
    # p[0] = ['type_parameter', p[1]]
    if p[1] == 'int':
        p[0] = st.type(p[1], True, False, None, 4, None)
    elif p[1] == 'char':
        p[0] = st.type(p[1], True, False, None, 1, None)
    else:
        p[0] = st.type(p[1], False, False, None, 1, None)

def p_variable_declarators(p):
    """variable_declarators : variable_declarator
    | variable_declarators COMMA variable_declarator
    """
    if len(p) == 2:
        p[0] = [p[1]]
        # p[0] = ['variable_declarators', p[1]]
    else:
        # p[0] = ['variable_declarators', p[1], ',', p[3]]
        p[0] = p[1] + [p[3]]

def p_variable_declarator(p):
    """variable_declarator : identifier
    | identifier EQUALS variable_initializer
    """
    p[0] = {}
    p[0]['code'] = ['']
    if len(p) == 2:
        # p[0] = ['variable_declarator', p[1]]
        p[0]['name'] = p[1]['value']
    else:
        p[0]['code'] = ['=, ' + p[1]['value'] + ', ' + p[3]['value']]
        # p[0] = ['variable_declarator', p[1], '=', p[3]]
        p[0]['name'] = p[1]['value']

def p_variable_initializer(p):
    """variable_initializer : expression
    """
                                                    # | array_initializer
    # p[0] = ['variable_initializer', p[1]]
    p[0] = {}
    p[0]['value'] = p[1]['value']

# def p_array_initializer(p):
#     """array_initializer : LBRACE variable_initializer_list RBRACE
#                         | LBRACE RBRACE
#                         | LBRACE variable_initializer_list COMMA RBRACE
#     """
#     if len(p) == 3:
#         # p[0] = ['array_initializer', '{', '}']
# 	p[0] = {'code':[], 'value':p[1]}
#     # elif len(p) == 4:
#     #     p[0] = ['array_initializer', '{', p[1], '}']
#     else:
#         # p[0] = ['array_initializer', '{', p[1], ',', '}']
#         p[0] = dp(p[2])

def p_variable_initializer_list(p):
    """variable_initializer_list : variable_initializer
                                | variable_initializer_list COMMA variable_initializer
    """
    if len(p) == 2:
        p[0] = ['variable_initializer_list', p[1]]
    else:
        p[0] = ['variable_initializer_list', p[1], ',', p[3]]

def p_method_declaration(p):
    """method_declaration : method_header method_body
    """
    # p[0] = ['method_declaration', p[1]]
    return_type = p[1]['type']
    method_name = p[1]['name']
    method_params = p[1]['params']
    symtab = p[2]['symtab']
    p[0] = {'code':[], 'value':None}
    #if return_type != 'void':
    # TODO: Add arguments x86 code
    print('calling function', method_name)
    p[0]['code'] += ['fn_def, ' + method_name + ', ' + str(len(method_params)) + ', ' + ', '.join(x['value'] for x in method_params)]
    print(method_params)
    for x in method_params:
        print('==-=-=-=-=-')
        print(x['type'].dict)
        if x['type'].dict['isarray']:
            symtab.enter_var(x['value'], x['type'].dict['arr_elem_type'], 'arr')
        else:
            symtab.enter_var(x['value'], x['type'].dict['name'][1])
        #symtab.print_symbol_table()
    if method_params != None:
        for param in method_params:
            # parameters would have been pushed to the stack, so we just pop them off
            p[0]['code'] += ['pop, ' + param['value']]
    p[0]['code'] += p[2]['code']

#def p_qualified_identifier(p):
#    """qualified_identifier : identifier
#    | qualified_identifier MEMBERACCESS identifier
#    """
#    if len(p) == 2:
#        p[0] = ['qualified_identifier', p[1]]
#    else:
#        p[0] = ['qualified_identifier', p[1], p[2], p[3]]

def p_method_header(p):
    """method_header : type member_name LPAREN fixed_parameters RPAREN
                        | modifiers  type member_name LPAREN fixed_parameters RPAREN
                        | type member_name LPAREN RPAREN
                        | modifiers type member_name LPAREN RPAREN
                        | VOID member_name LPAREN fixed_parameters RPAREN
                        | modifiers  VOID member_name LPAREN fixed_parameters RPAREN
                        | VOID member_name LPAREN RPAREN
                        | modifiers VOID member_name LPAREN RPAREN
    """
    if len(p) == 7:
        # p[0] = ['method_header', p[1], p[2], p[3], '(', p[5], ')']
        p[0] = {}
        p[0]['type'] = p[2]
        p[0]['name'] = p[3]['value']
        p[0]['params'] = p[5]
        params = p[5]
        param_types = []
        # param_num = 0
        if params != None:
            param_types = [param['type'] for param in params]
        # param_num = len(params)
        env.pres_env.enter_function(p[3]['value'], p[2], param_types)
    elif len(p) == 5:
        # p[0] = ['method_header', p[1], p[2], '(', ')']
        p[0] = {}
        p[0]['type'] = p[1]
        p[0]['name'] = p[2]['value']
        p[0]['params'] = []
        params = []
        param_types = []
        # param_num = 0
        if params != None:
            param_types = [param['type'] for param in params]
        # param_num = len(params)
        env.pres_env.enter_function(p[2]['value'], p[1], param_types)
    elif p[3] == '(':
        # p[0] = ['method_header', p[1], p[2], '(', p[4], ')']
        p[0] = {}
        p[0]['type'] = p[1]
        p[0]['name'] = p[2]['value']
        p[0]['params'] = p[4]
        params = p[4]
        param_types = []
        # param_num = 0
        if params != None:
            param_types = [param['type'] for param in params]
        # param_num = len(params)
        env.pres_env.enter_function(p[2]['value'], p[1], param_types)
    else:
        # p[0] = ['method_header', p[1], p[2], p[3], '(', ')']
        p[0] = {}
        p[0]['type'] = p[2]
        p[0]['name'] = p[3]['value']
        p[0]['params'] = []
        params = []
        param_types = []
        # param_num = 0
        if params != None:
            param_types = [param['type'] for param in params]
        # param_num = len(params)
        env.pres_env.enter_function(p[3]['value'], p[2], param_types)

    p[0]['category'] = 'function'
def p_modifiers(p):
    """modifiers : modifier
                                            | modifiers modifier
    """
    p[0] = {}
    if len(p) == 2:
        p[0]['code'] = p[1]['code']
        # p[0] = ['modifiers', p[1]]
    else:
        p[0]['code'] = p[1]['code'] + p[2]['code']
        # p[0] = ['modifiers', p[1], p[2]]

def p_modifier(p):
    """modifier : PUBLIC
                                    | PRIVATE
    """
    p[0] = {}
    p[0]['code'] = ""
    # p[0] = ['modifier', p[1]]

# def p_return_type(p):
#     """return_type : type
#                     | VOID
#     """
#     p[0] = ['return_type', p[1]]

def p_member_name(p):
    """member_name : identifier
    """
    p[0] = dp(p[1])

# TODO: May need to do scope changing here
def p_method_body(p):
    """method_body : block
                    | TERMINATOR
    """
    # p[0] = ['method_body', p[1]]
    if p[1] == ';':
        p[0] = {'code':[], 'value':None}
    else:
        p[0] = dp(p[1])

def p_fixed_parameters(p):
    """fixed_parameters : fixed_parameter
                                            | fixed_parameters COMMA fixed_parameter
    """
    if len(p) == 2:
        #p[0] = ['fixed_parameters', p[1]]
        p[0] = [p[1]]
    else:
        #p[0] = ['fixed_parameters', p[1], ',', p[3]]
        p[0] = p[1] + [p[3]]

def p_fixed_parameter(p):
    """fixed_parameter : type identifier default_argument
                                            | type identifier
    """
    # TODO: Default argument
    p[0] = {}
    if len(p) == 3:
        #p[0] = ['fixed_parameter', p[1], p[2]]
        p[0]['type'] = p[1]
        p[0]['value'] = p[2]['value']
    else:
        #p[0] = ['fixed_parameter', p[1], p[2], p[3]]
        p[0]['type'] = p[1]
        p[0]['value'] = p[2]['value']

# TODO 
def p_default_argument(p):
    """default_argument : EQUALS expression
    """
    p[0] = ['default_argument', '=', p[2]]

def p_constructor_declaration(p):
    """constructor_declaration : constructor_declarator constructor_body
    """
    # p[0] = ['constructor_declaration', p[1], p[2]]
    p[0] = {'code': [""], 'value': None}

def p_constructor_declarator(p):
    """constructor_declarator : identifier LPAREN fixed_parameters RPAREN
                                                            | identifier LPAREN  RPAREN
    """
    # if len(p) == 4:
    #     p[0] = ['constructor_declarator', p[1], '(', ')']
    # else:
    #     p[0] = ['constructor_declarator', p[1], '(', p[3], ')']
    p[0] = {'code': [""], 'value': None}
    p[0]['category'] = 'function'


def p_constructor_body(p):
    """constructor_body : block
                                            | TERMINATOR
    """
    # if p[1] is ';':
    #     p[0] = ['constructor_body', ';']
    # else:
    #     p[0] = ['constructor_body', p[1]]
    p[0] = {'code': [""], 'value': None}

def p_destructor_declaration(p):
    """destructor_declaration : TILDE identifier LPAREN RPAREN destructor_body
    """
    # p[0] = ['destructor_declaration', p[1], p[2], p[3], p[4], p[5]]
    p[0] = {'code': [""], 'value': None}
    p[0]['category'] = 'function'


def p_destructor_body(p):
    """destructor_body : block
                                            | TERMINATOR
    """
    # p[0] = ['destructor_body', p[1]]
    p[0] = {'code': [""], 'value': None}


# STATEMENT #######################################################################
def p_block(p):
    """block : LBRACE RBRACE
            | LBRACE scope_marker statement_list RBRACE
    """
    # if len(p) == 3:
    #     p[0] = ['block', p[1], p[2]]
    # else:
    #     p[0] = ['block', p[1], p[2], p[3]]
    if len(p) == 3:
        p[0] = {}
        p[0]['code'] = ['']
        p[0]['value'] = None
        p[0]['symtab'] = None
    else:
        p[0] = dp(p[3])
        p[0]['symtab'] = p[2]
        env.close_scope()


def p_scope_marker(p):
    """scope_marker :
    """
    p[0] = None
    t = env.new_scope()
    p[0] = t
    #p[0]['params'] = p[-2]['params']
    print(t)
    if 'params' in p[-2]:
        for x in p[-2]['params']:
            print('==-=-=-=-=-')
            print(x['type'].dict)
            if x['type'].dict['isarray']:
                t.enter_var(x['value'], x['type'].dict['arr_elem_type'], 'arr')
            else:
                t.enter_var(x['value'], x['type'].dict['name'][1])
            #t.print_symbol_table()


def p_statement_list(p):
    """statement_list : statement
                        | statement_list statement
    """
    if len(p) == 2:
        # p[0] = ['statement_list', p[1]]
        p[0] = dp(p[1])
    else:
        # p[0] = ['statement_list', p[1], p[2]]
        p[0] = dp(p[1])
        p[0]['code'] += p[2]['code']
        p[0]['value'] = None


def p_statement(p):
    """statement : local_variable_declaration TERMINATOR
    | embedded_statement
    """
    # if len(p) == 2:
    #     p[0] = ['statement', p[1]]
    # else:
    #     p[0] = ['statement', p[1], p[2]]
    p[0] = dp(p[1])

def p_embedded_statement(p):
    """embedded_statement : block
    | TERMINATOR
    | statement_expression TERMINATOR
    | if_statement
    | iteration_statement
    | print_statement
    | break_statement
    | return_statement
    """
    # | continue_statement

    if p[1] == ';':
        p[0] = {}
        p[0]['code'] = ['']
        p[0]['value'] = None
    else:
        p[0] = dp(p[1])


def p_print_statement(p):
    """ print_statement : PRINT LPAREN expression RPAREN TERMINATOR
    """
    # print("asdadas")
    p[0] = {}
    p[0]['code'] = p[3]['code']
    # print(p[3]['value'], '^^^^^^^^^^^^^^^^^^^^^^^^^')
    if env.prev_lookup(p[3]['value'], env.pres_env):
        p[0]['code'] += ['print, ' + p[3]['value']]
    else:
        print(" variable to print not defined")
        exit()

def p_break_statement(p):
    """break_statement : BREAK TERMINATOR
    """
    
    p[0] = {'code': [""], 'value': None}
    if(p[-1] == None):
        # print "a"
        indx = -6
    elif(p[-2] == None):
        # print "b"
        indx = -7
    else:
        # print "c"
        indx = -4
    if 'category' not in p[indx]:
        print("error, break not allowed")
        exit()
    if p[indx]['category'] == 'while':
        p[0]['code'] += ['goto, ' + p[indx]['next']]
    elif p[indx]['category'] == 'if':
        p[0]['code'] += ['goto, ' + p[indx]['next']]
        
    p[0]['break'] = True
    # sys.exit()
    # p[0] = ['break_statement', 'BREAK', p[2]]
    
    #TODO: Implement

def p_continue_statement(p):
    """continue_statement : CONTINUE TERMINATOR
    """
    p[0] = ['continue_statement', 'CONTINUE', p[2]]
    #TODO: Implement

def p_return_statement(p):
    """return_statement : RETURN TERMINATOR
    | RETURN expression TERMINATOR
    """
    if len(p) == 3:
        # p[0] = ['return_statement', 'RETURN', p[2]]
        p[0] = {'code':[], 'value':None}
        p[0]['code'] = ['return']
    else:
        # p[0] = ['return_statement', 'RETURN', p[2], p[3]]
        if not env.prev_lookup(p[2]['value'], env.pres_env) and not p[2]['value'].isdigit():
            print("No var declared. Error in return")
            exit()
        p[0] = {'code':[], 'value':None}
        p[0]['code'] += p[2]['code']
        p[0]['value'] = p[2]['value']
        p[0]['code'] += ['return, ' + p[2]['value']]

def p_literal(p):
    """literal : INTCONST
    | STRCONST
    | CHARCONST
    """
    p[0] = {}
    p[0]['code'] = [""]
    p[0]['value'] = p[1]

def p_local_variable_declaration(p):
    """local_variable_declaration : type local_variable_declarators
    """
    #p[0] = ['local_variable_declaration', p[1], p[2]]
    p[0] = {'code': [''], 'value': None}
    typ = p[1]
    for var in p[2]:
        name, init, code = var['value'], var['init'], var['code']
        if env.pres_env.lookup(name) is None:
            p[0]['code'] += code
            if not init:
                env.pres_env.enter_var(name, typ)
            else:
                arr_flag = False
                if 'length' in init.keys():
                    # this means we have an array
                    el_typ = dp(typ)
                    typ.dict['isarray'] = True
                    typ.dict['arr_elem_type'] = el_typ
                    typ.dict['length'] = init['length']
                    arr_flag = True

                env.pres_env.enter_var(name, typ,arr=arr_flag)
                p[0]['code'] += ['=, ' + name + ', ' + init['value']]
        else:
            print('Double declaration')
            exit()

def p_local_variable_declarators(p):
    """local_variable_declarators : local_variable_declarator
    | local_variable_declarators COMMA local_variable_declarator
    """
    if len(p) == 2:
        # p[0] = ['local_variable_declarators', p[1]]
        p[0] = [p[1]]
    else:
        # p[0] = ['local_variable_declarators', p[1], p[2], p[3]]
        p[0] = p[1] + [p[3]]

def p_local_variable_declarator(p):
    """local_variable_declarator : identifier
    | identifier EQUALS local_variable_initializer
    """
    p[0] = {}
    if len(p) == 2:
        #p[0] = ['local_variable_declarator', p[1]]
        p[0]['value'] = p[1]['value']
        p[0]['init'] = None
        p[0]['code'] = p[1]['code']
    else:
        #p[0] = ['local_variable_declarator', p[1], p[2], p[3]]
        p[0]['value'] = p[1]['value']
        p[0]['init'] = p[3]
        print(p[3])
        p[0]['code'] = p[3]['code']

def p_local_variable_initializer(p): # TODO: Can be removed to reduce conflicts
    """local_variable_initializer : expression
    """
    #p[0] = ['local_variable_initializer', p[1]]
    p[0] = dp(p[1])

def p_statement_expression(p):
    """statement_expression : object_creation_expression
    | assignment
    | invocation_expression
    | post_increment_expression
    | post_decrement_expression
    """
    # p[0] = ['statement_expression' , p[1]]
    p[0] = dp(p[1])

def p_invocation_expression(p):
    """invocation_expression : primary_expression LPAREN argument_list RPAREN
    | primary_expression LPAREN RPAREN
    | identifier LPAREN RPAREN
    | identifier LPAREN argument_list RPAREN
    | proper_identifier LPAREN argument_list RPAREN
    | proper_identifier LPAREN RPAREN
    """
    if len(p) == 4:
        indx = -1
    #     p[0] = ['invocation_expression', p[1], p[2], p[3]]
    else:
        indx = 3
    #     p[0] = ['invocation_expression', p[1], p[2], p[3], p[4]]
    p[0] = {}
    p[0]['code'] = [""]
    p[0]['value'] = None
    function = env.prev_lookup(p[1]['value'], env.pres_env)
    if function is not False:
        if function['category'] == 'function':
            argc = 0
            if indx is not -1:
                argc = len(p[indx])
            if function['arg_num'] == argc:
                if argc > 0:
                    for arg in p[3]:
                        p[0]['code'] += arg['code']
                if function['type'] is not 'void':
                    t = env.mktemp(function['type'])
                    p[0]['value'] = t
                    code = 'fn_call_2, ' + p[1]['value'] + ', ' + str(argc)
                    if indx is not -1:
                        for arg in p[3]:
                            if not env.prev_lookup(arg['value'], env.pres_env) and not arg['value'].isdigit():
                                print("Undeclared vars in fn call")
                                exit()
                            code += ',' + arg['value']
                    p[0]['code'] += [code + ', ' + t]
                else:
                    code = 'fn_call_1, ' + p[1]['value'] + ', ' + str(argc)
                    if indx is not -1:
                        for arg in p[3]:
                            if not env.prev_lookup(arg['value'], env.pres_env) and not arg['value'].isdigit():
                                print("Undeclared vars in fn call")
                                exit()
                            code += ',' + arg['value']
                    p[0]['code'] += [code]
            else:
                print("error in Line No. ", p.lineno(1), "Function", p[1]['value'], "needs exactly", env.pres_env.entries[p[1]['value']]['arg_num'], "parameters, given", len(p[3]))
                print("Compilation Terminated")
                exit()
        else:
            print("error in Line No. ", p.lineno(1), "Function", p[1]['value'], "This is not defined as a function")
            print("Compilation Terminated")
            exit()
    else:
        print("error in Line No. ", p.lineno(1), "Function", p[1]['value'], "This is not a function")
        print("Compilation Terminated")
        exit()

def p_if_statement(p):
    """if_statement : if LPAREN expression RPAREN embedded_statement
    | if LPAREN expression RPAREN embedded_statement else embedded_statement
    """
    p[0] = {'code':[''], 'value':None}    
    if len(p) == 6:
        # p[0] = ['if_statement', p[1], p[2], p[3], p[4], p[5]]
        p[3]['True'] = p[1]['True']#env.mklabel()
        p[3]['False'] = p[1]['False']#env.mklabel()
        p[0]['code'] += p[1]['code']
        p[0]['code'] += p[3]['code']
        p[0]['code'] += ['conditional_goto, ==, 1, ' + p[3]['value'] + ", " + p[3]['True']]
        p[0]['code'] += ['goto, ' + p[3]['False']]
        p[0]['code'] += ['label, ' + p[3]['True']]
        p[0]['code'] += p[5]['code']
        p[0]['code'] += ['label, ' + p[3]['False']]
        if('break' in p[5]):
            print("Error, break allowed only in if part of if-else")
            exit()
    else:
        # p[0] = ['if_statement', p[1], p[2], p[3], p[4], p[5], p[6], p[7]]
        p[3]['True'] = p[1]['True']#env.mklabel()
        p[0]['next'] = p[1]['next']#env.mklabel()
        p[0]['code'] += p[1]['code']
        p[0]['code'] += p[3]['code']
        p[0]['code'] += ['conditional_goto, ==, 1, ' + p[3]['value'] + ", " + p[3]['True']]
        p[0]['code'] += p[7]['code']
        p[0]['code'] += ['goto, ' + p[0]['next']]
        p[0]['code'] += ['label, ' + p[3]['True']]
        p[0]['code'] += p[5]['code']
        p[0]['code'] += ['label, ' + p[0]['next']]

def p_if(p):
    """if : IF
    """
    p[0] = {'code': [''], 'value': None}
    p[0]['category'] = 'if'
    p[0]['True'] = env.mklabel()
    p[0]['False'] = env.mklabel()
    p[0]['begin'] = env.mklabel()
    p[0]['True'] = env.mklabel()
    p[0]['next'] = env.mklabel()

def p_else(p):
    """else : ELSE
    """
    p[0] = {'code': [''], 'value': None}
    # p[0]['category'] = 'if'


def p_iteration_statement(p):
    """iteration_statement : while LPAREN expression RPAREN embedded_statement
    """
    # p[0] = ['iteration_statement', p[1], p[2], p[3], p[4], p[5]]
    p[0] = {'code':[''], 'value':None}
    p[0]['begin'] = p[1]['begin']
    p[0]['next'] = p[1]['next']
    p[3]['True'] = p[1]['True']
    p[0]['code'] += ['label, ' + p[0]['begin']]
    p[0]['code'] += p[3]['code']
    p[0]['code'] += ['conditional_goto, ==, 1, ' + p[3]['value'] + ", " + p[3]['True']]
    p[0]['code'] += ['goto, ' + p[0]['next']]
    p[0]['code'] += ['label, ' + p[3]['True']]
    p[0]['code'] += p[5]['code']
    p[0]['code'] += ['goto, ' + p[0]['begin']]
    p[0]['code'] += ['label, ' + p[0]['next']]
    # print "----"
    # print p[0]['next']

def p_while(p):
    """while : WHILE
    """
    p[0] = {'code': [''], 'value': None}
    p[0]['category'] = 'while'
    p[0]['next'] = env.mklabel()
    p[0]['True'] = env.mklabel()
    p[0]['begin'] = env.mklabel()

# EXPRESSION #####################################################################################
def p_expression(p):
    """expression : non_assignment_expression
                    | assignment
    """
    # p[0] = ['expression', p[1]]
    p[0] = dp(p[1])

def p_assignment(p):
    """assignment : unary_expression assignment_operator expression
                    | identifier assignment_operator expression
    """
    #p[0] = ['assignment', p[1], p[2], p[3]]
    p[0] = {}
    print('========================')
    print(p[1]['value'])
    print(env.prev_lookup(p[1]['value'] , env.pres_env))
   # env.print_symbol_table(env.pres_env)
    print('========================')
    if env.prev_lookup(p[1]['value'] , env.pres_env):
        p[0]['value'] = p[1]['value']
        p[0]['code'] = dp(p[3]['code'])
        p[0]['code'] += p[1]['code']
        p[0]['code'] += ['=, ' + p[0]['value'] + ', ' + p[3]['value']]
        if('array_el' in p[1] and p[1]['array_el'] is True):
            p[0]['code'] += ["array_asgn, " + p[1]['par_arr'] + ", " + p[1]['index'] + ", " + p[1]['value']]

    else:
        print("ERROR: symbol '"+ p[1]['value'] +"' used without declaration")
        print("Compilation Terminated")
        exit()

def p_assignment_operator(p):
    """assignment_operator : EQUALS
    """
    #p[0] = ['assignment_operator', p[1]]
    p[0] = {}
    p[0]['value'] = p[1]
    p[0]['code'] = ['']

def p_unary_expression(p):
    """unary_expression : primary_expression
                        | PLUS unary_expression
                        | PLUS identifier
                        | MINUS unary_expression
                        | MINUS identifier
                        | LNOT unary_expression
                        | LNOT identifier
                        | TILDE unary_expression
                        | TILDE identifier
    """
    p[0] = {}
    if len(p) == 2:
        p[0] = dp(p[1])
    else:
        if p[1] == '+':
            p[0] = dp(p[2])
        elif p[1] == '-':
            t = env.mktemp('int')
            p[0]['value'] = t
            p[0]['code'] = dp(p[2]['code'])
            p[0]['code'] += ["-, " + p[0]['value'] + ", " + p[2]['value'] + ", 0"]
        elif p[1] is '~' or '!':
            t = env.mktemp('int')
            p[0]['value'] = t
            p[0]['code'] = dp(p[2]['code'])
            p[0]['code'] += ["~, " + p[0]['value'] + ", " + p[2]['value'] ]

def p_primary_expression(p):
    """primary_expression : primary_no_array_creation_expression
                            | array_creation_expression
    """
    # p[0] = ['primary_expression', p[1]]
    p[0] = dp(p[1])

def p_primary_no_array_creation_expression(p):
    """primary_no_array_creation_expression : literal
                                            | parenthesized_expression
                                            | member_access
                                            | element_access
                                            | post_increment_expression
                                            | invocation_expression
                                            | post_decrement_expression
                                            | object_creation_expression
                                            | typeof_expression
    """
    # p[0] = ['primary_no_array_creation_expression', p[1]]
    # Not Done - element_access THIS IS ELEMENT IN ARRAY ACCESS
    # Not Done - member_access
    # DOne - invocation_expression for functions
    # Done - post dec/inc
    # Not done - typeof
    # Not done - object creation
    p[0] = dp(p[1])

def p_parenthesized_expression(p):
    """parenthesized_expression : LPAREN expression RPAREN
    """
    # p[0] = ['parenthesized_expression', p[1], p[2], p[3]]
    p[0] = dp(p[2])

def p_member_access(p):
    """member_access : primary_expression MEMBERACCESS identifier
                                            | iMEMAi
                                            | predefined_type MEMBERACCESS identifier
    """
    if len(p) == 2:
        p[0] = ['member_access', p[1]]
    else:
        p[0] = ['member_access', p[1], p[2], p[3]]

def p_predefined_type(p):
    """predefined_type : INT
                                            | CHAR
    """
    p[0] = ['predefined_type', p[1]]
    # TODO : add support for types using the DS

def p_element_access(p):
    """element_access : primary_no_array_creation_expression LBRACKET expression_list RBRACKET
                                            | identifier LBRACKET expression_list RBRACKET
    """
    # p[0] = ['element_access', p[1], p[2], p[3], p[4]]
    p[0] = {}
    p[0]['code'] = [""]
    p[0]['value'] = None
    array = env.prev_lookup(p[1]['value'], env.pres_env)
    if array is not False:
        if array['category'] == 'arr' or array['type'].dict['isarray'] is True:
            if(len(p[3][1]['value'].split(',')) > 1):
                print("error in Line No. ", p.lineno(1), "array", p[1], "is not 1D")
            p[0]['code'] += p[3][1]['code']
            t1 = env.mktemp('int')
            t2 = env.mktemp('int')
            t = env.mktemp(array['type'].dict['arr_elem_type'])
            # check for p[3][1]['value']

            try:
                val = int(p[3][1]['value'])
            except ValueError:
                flag = env.prev_lookup(p[3][1]['value'],env.pres_env)
                if(flag is False):
                    print("Error: the index is not declared")
                    exit()

            p[0]['code'] += ['=, ' + t1 + ', ' + p[3][1]['value']]
            # add width feature !!!!!!!!!!!!!!!!!!!!!!!!!!
            p[0]['code'] += ['*, ' + t2 + ', ' + t1 + ', ' + str(array['type'].dict['arr_elem_type'].dict['data_width'])]
            p[0]['code'] += ['array_access, ' + t + ', ' + p[1]['value'] + ', ' + t2]
            p[0]['value'] = t
            p[0]['array_el'] = True
            p[0]['par_arr'] = p[1]['value']
            p[0]['index'] = t2
        else:
            print("error in Line No. ", p.lineno(1), "Function", p[1], "not defined as an array")
            print("Compilation Terminated")
            exit()
    else:
        print("error in Line No. ", p.lineno(1), ": symbol", p[0], "array doesnt exist")
        print("Compilation Terminated")
        exit()

# TODO : 
def p_expression_list(p):
    """expression_list : expression
                                            | expression_list COMMA expression
    """
    if len(p) == 2:
        p[0] = ['expression_list', p[1]]
    else:
        p[0] = ['expression_list', p[1], p[2], p[3]]

def p_post_increment_expression(p):
    """post_increment_expression : primary_expression INCREMENT
                                                                    | identifier INCREMENT
    """
    # p[0] = ['post_increment_expression', p[1], p[2]]
    p[0] = dp(p[1])
    p[0]['code'] += ["+, " + p[0]['value'] + ", 1, " + p[0]['value']]
    if('array_el' in p[1] and p[1]['array_el'] is True):
        p[0]['code'] += ["array_asgn, " + p[0]['par_arr'] + ", " + p[0]['index'] + ", " + p[0]['value']]


def p_post_decrement_expression(p):
    """post_decrement_expression : primary_expression DECREMENT
                                 | identifier DECREMENT
    """
    # p[0] = ['post_decrement_expression', p[1], p[2]]
    # t = symbol_table.maketemp('int', symbol_table.curr_table)
    p[0] = dp(p[1])
    p[0]['code'] += ["-, " + p[0]['value'] + ", 1, " + p[0]['value']]
    if('array_el' in p[1] and p[1]['array_el'] is True):
        p[0]['code'] += ["array_asgn, " + p[0]['par_arr'] +
                         ", " + p[0]['index'] + ", " + p[0]['value']]

def p_object_creation_expression(p):
    """object_creation_expression : NEW type LPAREN argument_list RPAREN object_or_collection_initializer
                                    | NEW type LPAREN argument_list RPAREN
                                    | NEW type LPAREN RPAREN
                                    | NEW type object_or_collection_initializer
    """
    # if len(p) == 4:
    #     p[0] = ['object_creation_expression', p[1], p[2], p[3]]
    # elif len(p) == 5:
    #     p[0] = ['object_creation_expression', p[1], p[2], p[3], p[4]]
    # elif len(p) == 6:
    #     p[0] = ['object_creation_expression', p[1], p[2], p[3], p[4], p[5]]
    # else:
    #     p[0] = ['object_creation_expression', p[1], p[2], p[3], p[4], p[5], p[6]]
    p[0] = {}
    p[0]['code'] = ['']
    p[0]['value'] = None


def p_argument_list(p):
    """ argument_list : argument
                      | argument_list COMMA argument
    """
    # if len(p) == 2:
    #     p[0] = ['argument_list', p[1]]
    # else:
    #     p[0] = ['argument_list', p[1], p[2], p[3]]
    if len(p) == 2:
        p[0] = [dp(p[1])]
    else:
        p[0] = dp(p[1]) + [dp(p[3])]

def p_argument(p):
#     """argument : argument_name argument_value
#                             | argument_value
#     """
#     if len(p) == 2:
#         p[0] = ['argument', p[1]]
#     else:
#         p[0] = ['argument', p[1], p[2]]

# def p_argument_name(p):
#     """argument_name : identifier COLON
#     """
#     # p[0] = ['argument_name', p[1], p[2]]


# def p_argument_value(p):
    """ argument : expression
    """
    # p[0] = ['argument_value', p[1]]
    p[0] = dp(p[1])

def p_object_or_collection_initializer(p):
    """object_or_collection_initializer : object_initializer
                                        | collection_initializer
    """
    p[0] = ['object_or_collection_initializer', p[1]]

def p_object_initializer(p):
    """object_initializer : LBRACE member_initializer_list RBRACE
                            | LBRACE RBRACE
                            | LBRACE member_initializer_list COMMA RBRACE
    """
    if len(p) == 3:
        p[0] = ['object_initializer', p[1], p[2]]
    elif len(p) == 4:
        p[0] = ['object_initializer', p[1], p[2], p[3]]
    else:
        p[0] = ['object_initializer', p[1], p[2], p[3], p[4]]

def p_member_initializer_list(p):
    """member_initializer_list : member_initializer
                                | member_initializer_list COMMA member_initializer
    """
    if len(p) == 2:
        p[0] = ['member_initializer_list', p[1]]
    else:
        p[0] = ['member_initializer_list', p[1], p[2], p[3]]

def p_member_initializer(p):
    """member_initializer : identifier EQUALS initializer_value
    """
    p[0] = ['member_initializer', p[1], p[2], p[3]]

def p_initializer_value(p):
    """initializer_value : expression
                            | object_or_collection_initializer
    """
    p[0] = ['initializer_value', p[1]]

def p_collection_initializer(p):
    """collection_initializer : LBRACE element_initializer_list RBRACE
                                | LBRACE element_initializer_list COMMA RBRACE
    """
    if len(p) == 4:
        p[0] = ['collection_initializer', p[1], p[2], p[3]]
    else:
        p[0] = ['collection_initializer', p[1], p[2], p[3], p[4]]

def p_element_initializer_list(p):
    """element_initializer_list : element_initializer
                                | element_initializer_list COMMA element_initializer
    """
    if len(p) == 2:
        p[0] = ['element_initializer_list', p[1]]
    else:
        p[0] = ['element_initializer_list', p[1], p[2], p[3]]

def p_element_initializer(p):
    """element_initializer : non_assignment_expression
                            | LBRACE expression_list RBRACE
    """

    if len(p) == 2:
        p[0] = ['element_initializer', p[1]]
    else:
        p[0] = ['element_initializer_list', p[1], p[2], p[3]]

def p_array_creation_expression(p):
    """array_creation_expression : NEW non_array_type LBRACKET expression RBRACKET
    """
                                # | NEW array_type array_initializer
    p[0] = {}
    if len(p) == 4:
        p[0] = ['array_creation_expression', p[1], p[2], p[3]]
    else:
        if(p[2].dict['name'][1] != 'int'):
            print("error, only array of type int are allowed")
            exit()
        else:
            p[0]['code'] = p[4]['code']
            p[0]['value'] = 'arr_init, ' + p[4]['value']
            p[0]['length'] =  p[4]['value']
            p[0]['array_el'] = True
        # p[0] = ['array_creation_expression', p[1], p[2], p[3], p[4], p[5]]

# TODO:
def p_typeof_expression(p):
    """typeof_expression : TYPEOF LPAREN type RPAREN
                        | TYPEOF LPAREN unbound_type_name RPAREN
                        | TYPEOF LPAREN VOID RPAREN
    """
    p[0] = ['typeof_expression', p[1], p[2], p[3], p[4]]

def p_unbound_type_name(p):
    """unbound_type_name : iMEMAi
                        | unbound_type_name MEMBERACCESS identifier
    """
    if len(p) == 2:
        p[0] = ['unbound_type_name', p[1]]
    else:
        p[0] = ['unbound_type_name', p[1], p[2], p[3]]

def p_iMEMAi(p):
    """iMEMAi : identifier MEMBERACCESS identifier
    """
    p[0] = ['iMEMAi', p[1], p[2], p[3]]

def p_non_assignment_expression(p):
    """non_assignment_expression : conditional_expression
    """
    #p[0] = ['non_assignment_expression', p[1]]

    p[0] = dp(p[1])

def p_conditional_expression(p):
    """conditional_expression : conditional_or_expression
    """
    #p[0] = ['conditional_expression', p[1]]
    p[0] = dp(p[1])

def p_conditional_or_expression(p):
    """conditional_or_expression : conditional_and_expression
                                    | conditional_or_expression CONOR conditional_and_expression
    """
    if len(p) == 2:
        # p[0] = ['conditional_or_expression', p[1]]
        p[0] = dp(p[1])
    else:
        # p[0] = ['conditional_or_expression', p[1], p[2], p[3]]
        p[0] = {}
        t = env.mktemp('int')
        if not p[1]['value'].isdigit() and env.prev_lookup(p[1]['value'], env.pres_env) is False:
            print("error in 1190")
            exit()
        if not p[3]['value'].isdigit() and env.prev_lookup(p[3]['value'], env.pres_env) is False:
            print("error in 1193")
            exit()
        p[0]['value'] = t
        p[0]['code'] = p[1]['code'] + p[3]['code']
        p[0]['code'] += ["||, " + t + ", " + p[1]['value'] + ", " + p[3]['value']]

def p_conditional_and_expression(p):
    """conditional_and_expression : inclusive_or_expression
                                    | conditional_and_expression CONAND inclusive_or_expression
    """
    if len(p) == 2:
        # p[0] = ['conditional_and_expression', p[1]]
        p[0] = dp(p[1])
    else:
        # p[0] = ['conditional_and_expression', p[1], p[2], p[3]]
        p[0] = {}
        t = env.mktemp('int')
        if not p[1]['value'].isdigit() and env.prev_lookup(p[1]['value'], env.pres_env) is False:
            print("error in 1211")
            exit()
        if not p[3]['value'].isdigit() and env.prev_lookup(p[3]['value'], env.pres_env) is False:
            print("error in 1214")
            exit()
        p[0]['value'] = t
        p[0]['code'] = p[1]['code'] + p[3]['code']
        p[0]['code'] += ["&&, " + t + ", " + p[1]['value'] + ", " + p[3]['value']]

def p_inclusive_or_expression(p):
    """inclusive_or_expression : exclusive_or_expression
                                | inclusive_or_expression OR exclusive_or_expression
    """
    if len(p) == 2:
        # p[0] = ['inclusive_or_expression', p[1]]
        p[0] = dp(p[1])
    else:
        # p[0] = ['inclusive_or_expression', p[1], p[2], p[3]]
        p[0] = {}
        t = env.mktemp('int')
        if not p[1]['value'].isdigit() and env.prev_lookup(p[1]['value'], env.pres_env) is False:
            print("error in 1232")
            exit()
        if not p[3]['value'].isdigit() and env.prev_lookup(p[3]['value'], env.pres_env) is False:
            print("error in 1235")
            exit()
        p[0]['value'] = t
        p[0]['code'] = p[1]['code'] + p[3]['code']
        p[0]['code'] += ["||, " + t + ", " + p[1]['value'] + ", " + p[3]['value']]

def p_exclusive_or_expression(p):
    """exclusive_or_expression : and_expression
                                | exclusive_or_expression XOR and_expression
    """
    if len(p) == 2:
        # p[0] = ['exclusive_or_expression', p[1]]
        p[0] = dp(p[1])
    else:
        # p[0] = ['exclusive_or_expression', p[1], p[2], p[3]]
        p[0] = {}
        t = env.mktemp('int')
        if not p[1]['value'].isdigit() and env.prev_lookup(p[1]['value'], env.pres_env) is False:
            print("error in 1253")
            exit()
        if not p[3]['value'].isdigit() and env.prev_lookup(p[3]['value'], env.pres_env) is False:
            print("error in 1256")
            exit()
        p[0]['value'] = t
        p[0]['code'] = p[1]['code'] + p[3]['code']
        p[0]['code'] += ["^, " + t + ", " + p[1]['value'] + ", " + p[3]['value']]

def p_and_expression(p):
    """and_expression : equality_expression
                        | and_expression AND equality_expression
    """
    if len(p) == 2:
        # p[0] = ['and_expression', p[1]]
        p[0] = dp(p[1])
    else:
        # p[0] = ['and_expression', p[1], p[2], p[3]]
        p[0] = {}
        t = env.mktemp('int')
        if not p[1]['value'].isdigit() and env.prev_lookup(p[1]['value'], env.pres_env) is False:
            print("error in line 1296")
            exit()
        if not p[3]['value'].isdigit() and env.prev_lookup(p[3]['value'], env.pres_env) is False:
            print("error in line 1299")
            exit()
        p[0]['value'] = t
        p[0]['code'] = p[1]['code'] + p[3]['code']
        p[0]['code'] += ["&, " + t + ", " + p[1]['value'] + ", " + p[3]['value']]


def p_equality_expression(p):
    """equality_expression : relational_expression
                            | equality_expression EQ relational_expression
                            | equality_expression NE relational_expression
    """
    # if len(p) == 2:
    #     p[0] = ['equality_expression', p[1]]
    # else:
    #     p[0] = ['equality_expression', p[1], p[2], p[3]]
    if len(p) == 2:
        p[0] = dp(p[1])
    else:
        p[0] = {}
        t = env.mktemp('int')
        p[0]['value'] = t
        p[0]['code'] = p[1]['code'] + p[3]['code']
        if p[2] == '==':
            if not p[1]['value'].isdigit() and env.prev_lookup(p[1]['value'], env.pres_env) is False:
                print("error in line 1324")
                exit()
            if not p[3]['value'].isdigit() and env.prev_lookup(p[3]['value'], env.pres_env) is False:
                print("error in 1327")
                exit()

            p[0]['code'] += ["==, " + t + ", " + p[1]['value'] + ", " + p[3]['value']]
        elif p[2] == '!=':
            if not p[1]['value'].isdigit() and env.prev_lookup(p[1]['value'], env.pres_env) is False:
                print("error in 1333")
                exit()
            if not p[3]['value'].isdigit() and env.prev_lookup(p[3]['value'], env.pres_env) is False:
                print("error in 1336")
                exit()

            p[0]['code'] += ["~=, " + t + ", " + p[1]['value'] + ", " + p[3]['value']]

def p_relational_expression(p):
    """ relational_expression : shift_expression
                                | relational_expression LT shift_expression
                                | relational_expression GT shift_expression
                                | relational_expression LEQ shift_expression
                                | relational_expression GEQ shift_expression
    """
    # if len(p) == 2:
    #     p[0] = ['relational_expression', p[1]]
    # else:
    #     p[0] = ['relational_expression', p[1], p[2], p[3]]
    if len(p) == 2:
        p[0] = dp(p[1])
    else:
        p[0] = {}
        t = env.mktemp('int')
        p[0]['value'] = t
        p[0]['code'] = p[1]['code'] + p[3]['code']
        if p[2] == '<':
            if not p[1]['value'].isdigit() and env.prev_lookup(p[1]['value'], env.pres_env) is False:
                print("error 1361")
                exit()
            if not p[3]['value'].isdigit() and env.prev_lookup(p[3]['value'], env.pres_env) is False:
                print("error in 1364")
                exit()

            p[0]['code'] += ["<, " + t + ", " + p[1]['value'] + ", " + p[3]['value']]
        elif p[2] == '>':
            if not p[1]['value'].isdigit() and env.prev_lookup(p[1]['value'], env.pres_env) is False:
                print("error in 1370")
                exit()
            if not p[3]['value'].isdigit() and env.prev_lookup(p[3]['value'], env.pres_env) is False:
                print("error in 1373")
                exit()

            p[0]['code'] += [">, " + t + ", " + p[1]['value'] + ", " + p[3]['value']]
        elif p[2] == '<=':
            if not p[1]['value'].isdigit() and env.prev_lookup(p[1]['value'], env.pres_env) is False:
                print("error in 1379")
                exit()
            if not p[3]['value'].isdigit() and env.prev_lookup(p[3]['value'], env.pres_env) is False:
                print("error in 1382")
                exit()

            p[0]['code'] += ["<=, " + t + ", " + p[1]['value'] + ", " + p[3]['value']]
        elif p[2] == '>=':
            if not p[1]['value'].isdigit() and env.prev_lookup(p[1]['value'], env.pres_env) is False:
                print("error in 1388")
                exit()
            if not p[3]['value'].isdigit() and env.prev_lookup(p[3]['value'], env.pres_env) is False:
                print("error in 1391")
                exit()

            p[0]['code'] += [">=, " + t + ", " + p[1]['value'] + ", " + p[3]['value']]

def p_shift_expression(p):
    """shift_expression : additive_expression
                        | shift_expression LSHIFT additive_expression
                        | shift_expression RSHIFT additive_expression
    """
    # if len(p) == 2:
    #     p[0] = ['shift_expression', p[1]]
    # else:
    #     p[0] = ['shift_expression', p[1], p[2], p[3]]
    if len(p) == 2:
        p[0] = dp(p[1])
    else:
        p[0] = {}
        t = env.mktemp('int')
        p[0]['value'] = t
        p[0]['code'] = p[1]['code'] + p[3]['code']
        if p[2] == '<<':
            if not p[1]['value'].isdigit() and env.prev_lookup(p[1]['value'], env.pres_env) is False:
                print("error")
                exit()
            if not p[3]['value'].isdigit() and env.prev_lookup(p[3]['value'], env.pres_env) is False:
                print("error")
                exit()

            p[0]['code'] += ["<<, " + t + ", " + p[3]['value'] + ", " + p[1]['value']]
        elif p[2] == '>>':
            if not p[1]['value'].isdigit() and env.prev_lookup(p[1]['value'], env.pres_env) is False:
                print("error")
                exit()
            if not p[3]['value'].isdigit() and env.prev_lookup(p[3]['value'], env.pres_env) is False:
                print("error")
                exit()

            p[0]['code'] += [">>, " + t + ", " + p[3]['value'] + ", " + p[1]['value']]

def p_additive_expression(p):
    """additive_expression : multiplicative_expression
                            | additive_expression PLUS multiplicative_expression
                            | additive_expression MINUS multiplicative_expression
    """
    # if len(p) == 2:
    #     p[0] = ['additive_expression', p[1]]
    # else:
    #     p[0] = ['additive_expression', p[1], p[2], p[3]]
    if len(p) == 2:
        p[0] = dp(p[1])
    else:
        p[0] = {}
        t = env.mktemp('int')
        p[0]['value'] = t
        p[0]['code'] = p[1]['code'] + p[3]['code']
        if p[2] == '+':
            if not p[1]['value'].isdigit() and env.prev_lookup(p[1]['value'], env.pres_env) is False:
                print("error")
                exit()
            if not p[3]['value'].isdigit() and env.prev_lookup(p[3]['value'], env.pres_env) is False:
                print("error")
                exit()
            p[0]['code'] += ["+, " + t + ", " + p[1]['value'] + ", " + p[3]['value']]
        elif p[2] == '-':
            if not p[1]['value'].isdigit() and env.prev_lookup(p[1]['value'], env.pres_env) is False:
                print("error")
                exit()
            if not p[3]['value'].isdigit() and env.prev_lookup(p[3]['value'], env.pres_env) is False:
                print("error")
                exit()
            p[0]['code'] += ["-, " + t + ", " + p[3]['value'] + ", " + p[1]['value']]

def p_multiplicative_expression(p):
    """multiplicative_expression : unary_expression
                                | identifier
                                | multiplicative_expression TIMES unary_expression
                                | multiplicative_expression DIVIDE unary_expression
                                | multiplicative_expression MOD unary_expression
                                | multiplicative_expression TIMES identifier
                                | multiplicative_expression DIVIDE identifier
                                | multiplicative_expression MOD identifier
    """
    if len(p) == 2:
        #p[0] = ['multiplicative_expression', p[1]]
        p[0] = dp(p[1])
    else:
        p[0] = {}
        t = env.mktemp('int')
        if p[2] == '*':
            if not p[1]['value'].isdigit() and env.prev_lookup(p[1]['value'], env.pres_env) is False:
                print("error")
                exit()
            if not p[3]['value'].isdigit() and env.prev_lookup(p[3]['value'], env.pres_env) is False:
                print("error")
                exit()
            p[0]['value'] = t
            p[0]['code'] = p[1]['code'] + p[3]['code']
            p[0]['code'] += ["*, " + t + ", " + p[1]['value'] + ", " + p[3]['value']]
        elif p[2] == '/':
            if not p[1]['value'].isdigit() and env.prev_lookup(p[1]['value'], env.pres_env) is False:
                print("error")
                exit()
            if not p[3]['value'].isdigit() and env.prev_lookup(p[3]['value'], env.pres_env) is False:
                print("error")
                exit()
            p[0]['value'] = t
            p[0]['code'] = p[1]['code'] + p[3]['code']
            p[0]['code'] += ["/, " + t + ", " + p[3]['value'] + ", " + p[1]['value']]
        elif p[2] == '%':
            if not p[1]['value'].isdigit() and env.prev_lookup(p[1]['value'], env.pres_env) is False:
                print("error")
                exit()
            if not p[3]['value'].isdigit() and env.prev_lookup(p[3]['value'], env.pres_env) is False:
                print("error")
                exit()
            p[0]['value'] = t
            p[0]['code'] = p[1]['code'] + p[3]['code']
            p[0]['code'] += ["%, " + t + ", " + p[3]['value'] + ", " + p[1]['value']]
        #p[0] = ['multiplicative_expression', p[1], p[2], p[3]]

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!", p)

##################################################################################################
# Build the parser now
parser = yacc.yacc(start='start', debug=True, optimize=False)

# Read the input program
inputfile = open(filename, 'r')
data = inputfile.read()
result = parser.parse(data, debug=0)
# print(result)

def print_tac(pclass):
    if pclass is None:
        print('Not parsable')
        exit(1)
    print("")
    print("1, fn_call_1, Main")
    c = 2
    for member in [pclass]:
        for line in member['code']:
            if line != "":
                print(str(c) + ", " + line)
                c = c + 1
    print(str(c) + ", exit")
print_tac(result)
