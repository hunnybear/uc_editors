'''
Created on Aug 28, 2011

@author: Tyler
'''

import string

ML_COMMENT = ( '/*', '*/' )
SL_COMMENT = ( '//', '\n' )

CLASS_DEC = ( 'class ', ';' )

CONST_DEC = ( 'const', ';' )
VAR_DEC = ( 'var', ';' )
STRUCT_DEC = ( 'struct', ';' )
LOCAL_DEC = ( 'local', ';' )

DEFAULT_PROPERTIES_DEC = ( 'defaultproperties', '}' )
DP_OBJECT_DEC = ( 'begin object', 'end object' )




#==============================================================================
# Terminals
#==============================================================================

CLASS_PARAMS = ['abstract',
                'native',
                'nativereplication',
                'safereplace',
                'perobjectconfig',
                'transient',
                'noexport',
                'exportstructs',
                'collapsecategories',
                'dontcollapsecategories',
                'placeable',
                'notplaceable',
                'editinlinenew',
                'noteditinlinenew' ]

# For now I'm ignoring the native function param
# TODO: Integrate 'native' support
FUNC_PARAMS = [ 'final',
                'iterator', 
                'latent',
                'simulated',
                'singular',
                'static',
                'exec',
                'protected',
                'private',
                'native' ] # Native is added, technically can have an (INT) after, but never seen it in practice 

VAR_PARAMS = [ 'config',
               'const',
               'editconst',
               'export',
               'globalconfig',
               'input',
               'localized',
               'native',
               'private',
               'protected',
               'transient',
               'travel',
               'editinline',
               'deprecated',
               'edfindable',
               'editinlineuse' ]

STATE_PARAMS = [ 'auto',
                 'simulated' ]

STATE_TYPES = [ 'state' ]

FUNC_TYPES = [ 'function',
               'event',
               'delegate' ]

OPERATOR_TYPES = [ 'operator',
                   'preoperator',
                   'postoperator' ]


ALPHA = string.ascii_letters
DIGIT = string.digits
HEXDIGIT = string.hexdigits
