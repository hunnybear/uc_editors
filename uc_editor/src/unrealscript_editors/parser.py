'''
Created on Aug 28, 2011

@author: Tyler
''' 
import uc_objects
import parser_grammar as pg
test_text = '/** true if we have been combo\'ed (so don\'t play normal explosion effects) */\nvar repnotify bool bComboed;\nvar Pawn ComboTarget;    // for AI use\n\nreplication\n{\n  if (Role == ROLE_Authority)\n    bComboed;\n}\n\nsimulated event ReplicatedEvent(name VarName)\n{\n  if (VarName == \'bComboed\')\n  {\n    bSuppressExplosionFX = true;\n  }\n  else\n  {\n    Super.ReplicatedEvent(VarName);\n  }\n}'
test_func = '\n  local int i;\n\n  For ( i=0; i<FireInterval.Length; i++ )\n  {\n    FireInterval[i] = FireInterval[i]/1.1;\n  }\n  EquipTime = EquipTime/1.1;\n  PutDownTime = PutDownTime/1.1;\n}\n'
test_full_func = "function int IncrementKillStat(name NewStatName)\n{\n  local int i, Len;\n  local IntStat NewStat;\n\n  Len = KillStats.Length;\n  for (i=0; i<Len; i++ )\n  {\n    if ( KillStats[i].StatName == NewStatName )\n    {\n      KillStats[i].StatValue++;\n      return KillStats[i].StatValue;\n    }\n  }\n\n  // didn't find it - add a new one\n  NewStat.StatName = NewStatName;\n  NewStat.StatValue = 1;\n  KillStats[Len] = NewStat;\n  return 1;\n}"

class UCParser( object ):
  def __init__( self ):
    self._class = uc_objects.Class( )
    self._parse_string = ''
  
  def parse( self, in_file ):

    with open( in_file, 'r' ) as parse_file:
      self.parse_from_string( parse_file.read( ) )
      
  def parse_from_string( self, parse_string ):
    self._parse_string = parse_string
    self._parser_helper( self._class )

  def _comment_parse( self, parse_string = None  ):
    """
    Parsing for comments and removing whitespace, things that need to happen
    inside of all parsing methods
    """
    new_comment = None
    if parse_string == None:
      parse_string = self._parse_string
    
    # Remove leading whitespace
    parse_string = parse_string.lstrip( )

    # Single Line Comments  
    if self._is_beginning( pg.SL_COMMENT ):
      print 'found sl comment'
      parse = self._parse_search( pg.SL_COMMENT )
      new_comment = uc_objects.Comment( parse[ 0 ] )
      parse_string = parse[ 1 ]

    # Multi-line comments    
    # Same as single line comments except for the "M" instead of "S" 
    elif self._is_beginning( pg.ML_COMMENT ):
      print 'found ml comment'
      parse = self._parse_search( pg.ML_COMMENT )
      
      print 'ml parse: {0}'.format( parse )
      new_comment = uc_objects.Comment( parse[ 0 ] )
      parse_string = parse[ 1 ]
      
    self._parse_string = parse_string
    return new_comment

  def _parser_helper( self, parent, block_end = None ):
    """
    The meat of the parsing.
    """
    print 'parser helper'
    
    while len( self._parse_string ) > 0: 
      while_string = self._parse_string
      
      new_comment = self._comment_parse( )
      if not new_comment == None:
        parent.add_child( new_comment ) 
      
      # Class declaration
      
      if self._is_beginning( pg.CLASS_DEC ):
        print 'classy!'
        self._parse_class_dec( )

      # Var declarations  
      elif self._is_beginning( pg.VAR_DEC ):
        parse = self._parse_search( pg.VAR_DEC )
        
        new_var = uc_objects.Variable( )
        parent.add_child( new_var )
        
        print 'var parse: {0}'.format( parse )
        
        split_dec = parse[ 0 ].split( )
        
        new_var.set_name( split_dec.pop( -1 ) )
        new_var.set_type( split_dec.pop( -1 ) )
        
        self._parse_string = parse[ 1 ]

      # Body Declarations
      elif self._is_param_beginning( ( pg.FUNC_PARAMS +
                                       pg.STATE_PARAMS +
                                       pg.FUNC_TYPES +
                                       pg.OPERATOR_TYPES +
                                       pg.STATE_TYPES ) ):
        
        new_dec = self._parse_body_dec( )
        parent.add_child( new_dec )
        
      
      # Default Properties
      elif self._is_beginning( pg.DEFAULT_PROPERTIES_DEC ):
        new_props = self._parse_default_properties( )
        parent.add_child( new_props )
        
      if while_string == self._parse_string:
        self._parse_string = self._parse_string[ 1: ]
        
  
   
  
  def _parse_declarations( self ):
    pass
  
  def _parse_body_dec_common( self, split_top, dec_object ):
    """
    Takes in a list of elements in the top block of a body declaration and
    does parsing operations that all body declarations have in common
    """
    
    # Name/Identifier
    dec_object.set_name( split_top.pop( - 1 ) )
    
    if isinstance( dec_object, uc_objects.Function ):
      params_tuple = pg.FUNC_PARAMS
    
    # Find, pop, and apply params  
    elif isinstance( dec_object, uc_objects.State ):
      params_tuple = pg.STATE_PARAMS
    params = [ ]  
    while split_top[ 0 ].lower( ) in params_tuple:
      params.append( split_top[ 0 ].lower( ) )
      split_top.pop( 0 )
    dec_object.set_params( params )
    
    
    return split_top
 
  
  
    
    
  def _parse_function_body( self, parse_string = None ):
    """
    parse the body of an individual function.  This will eventually become more
    complex and actually look at the contents, I believe, but not at this point.
    """
    
    if parse_string == None:
      parse_string = self._parse_string
    
    open_brac_count = 0
    i = 0
    while open_brac_count > 0 or not parse_string[ i ] == '}':
      if parse_string[ i ] == '{':
        open_brac_count = open_brac_count + 1
      if parse_string[ i ] == '}':
        open_brac_count = open_brac_count - 1
      i = i + 1
    
    self._parse_string = parse_string[ i + 1: ]
    print 'parse_string :'
    print i
    print parse_string[ i + 1: ]
    return( parse_string[ :i ] )

  #============================================================================
  # Grammar Element parsers
  # 
  # These methods all have an optional argument 'parse_string', in case
  # the user wants to use the method independent of a full UC parse.
  # 
  # All methods return the object created by the parse method.
  #============================================================================
  
  
  # The class
  def _parse_class_dec( self, parse_string = None ):
    """
    Parses the class declaration.  Returns the self._class object, since the 
    object that is having values assigned to it is already created
    """
    
    if parse_string == None:
      parse_string = self._parse_string
    
    EXTENDS = 'extends'
    
    # Splits the class dec and the rest of the text
    split_parse_text = self._parse_search( pg.CLASS_DEC )
    class_dec = split_parse_text[ 0 ]
    
    split_dec = class_dec.split( None, 1 )
    self._class.set_class_name( split_dec[ 0 ] )
    if len( split_dec ) > 1 :
      
      opt_dec = class_dec.split( None )[ 1: ]
      
      if opt_dec[ 0 ].lower( ) == EXTENDS:
        self._class.set_class_extends( opt_dec[ 1 ] )
        opt_dec = opt_dec[ 2: ]
    
    
    self._class.add_params( opt_dec )
    self._parse_string = class_dec = split_parse_text[ 1 ]
    # return non-parsed text
    return self._class
  
  
  # Body elements ( Functions, States, Operators )
  
  def _parse_body_dec( self, parse_string = None ):
    """
    Figures out what type of body declaration is being made and passes the 
    data to the appropriate constructor
    """
    
    if parse_string == None:
      parse_string = self._parse_string
    
    # Everything before the first '{', split at whitespaces
    test_split = parse_string.split( '{', 1 )[ 0 ].split( )
    
    for item in test_split:
      if item in pg.FUNC_TYPES:
        return self._parse_function( parse_string )
        
      if item in pg.OPERATOR_TYPES:
        return self._parse_operator( parse_string )
        
      if item in pg.STATE_TYPES:
        return self._parse_state( parse_string )
      
  def _parse_function( self, parse_string = None ):
    """
    Currently aiming to get a string of all function params.  I'm currently
    treating 'Native (INT)' as an edge case, until I need to implement it.
    """
    
    if parse_string == None:
      parse_string = self._parse_string
    
    new_func = uc_objects.NormalFunction( )
        
    body_split = parse_string.split( '{', 1 )
    top_block = body_split[ 0 ].strip( )
    
    
    if '(' in top_block:
      arg_split = top_block.split( '(' )
      args = arg_split[ 1 ].split( ')' )[ 0 ]
      top_block = arg_split[ 0 ].strip( )
      
    split_top = top_block.split( )
    
    split_top = self._parse_body_dec_common( split_top, new_func )
    
    # The rest should be localtype, if it exists
    if not len( split_top ) == 0:
      new_func.set_local_type( ' '.join( split_top ) )
    
    body_parse = self._parse_function_body( body_split[ 1 ] )
    new_func.set_body( body_parse )

    return new_func
  
  def _parse_state( self, parse_string = None ):
    
    if parse_string == None:
      parse_string = self._parse_string
    
    new_state = uc_objects.State( )
    
    body_split = parse_string.split( '{', 1 )
    top_block = body_split[ 0 ].strip( )
    
    if '(' in top_block:
      cfg_split = top_block.split( '(' )
      extends_split = cfg_split[ 1 ]( ')' )
      new_state.set_config_group( extends_split[ 0 ].strip( ) )
      
      extends = extends_split[ 1 ].split( )
      if len( extends ) == 2:
        if extends[ 0 ].lower( ) == 'extends':
          new_state.set_extends( extends [ 1 ] )
      
      top_block = cfg_split[ 0 ].strip( )
    
    split_top = top_block.split( )
    #TODO: get the state body parser working
    body_parse = self._parse_function_body( body_split[ 1 ] )
    #body_parse = self._parse_state_body( body_split[ 1 ] )
    new_state.set_body( body_parse[ 0 ] )
    remainder = body_parse[ 1 ]
    
    return new_state
  
  # Default Properties
  
  def _parse_default_properties( self, parse_string = None ):
    """
    parse the default properties block of the class
    """
    default_properties = uc_objects.DefaultProperites( )
    if parse_string == None:
      parse_string = self._parse_string
    

    prop_block_pre_split = parse_string.split( '{', 1 )[ 1 ].split( '}', 1 )
    
    self._parse_string = prop_block_pre_split[ 0 ].strip( )
    while len( self._parse_string ) > 0:
      
      new_comment = self._comment_parse( )
      if not new_comment == None:
        default_properties.add_child( new_comment )
         
         
      if self._is_beginning( pg.DP_OBJECT_DEC ):
        prop_object = self._parse_dp_object( )
        default_properties.add_child( prop_object )

      
      else:
        split_props = self._parse_string.split( '\n', 1 )
        new_prop = self._parse_dp_property( split_props[ 0 ] )
        default_properties.add_child( new_prop )
        if len( split_props ) > 1:
          self._parse_string = split_props[ 1 ]
        else:
          self._parse_string = ''
          
      
    print prop_block_pre_split
    self._parse_sting = prop_block_pre_split[ 1 ].strip( )
    return default_properties
  
  def _parse_dp_property( self, parse_string = None ):
    new_prop = uc_objects.DPProperty( )
    if parse_string == None:
      parse_string = self._parse_string
    
    
    self._parse_string = parse_string
    
    return new_prop
    
  def _parse_dp_object( self, parse_string = None ):
    """
    Parse an object declared in the default properties.  
    """
    
    
    new_obj = uc_objects.DPObject( )
    if parse_string == None:
      parse_string = self._parse_string
    
    new_comment = self._comment_parse( )
    if not new_comment == None:
      new_obj.add_child( new_comment )
    
    split_object = self._parse_search( pg.DP_OBJECT_DEC[ 1 ] )

    self._parse_string = split_object[ 1 ].strip( )
    return new_obj
    

  #============================================================================
  # Convenience Functions
  #============================================================================

  def _is_param_beginning( self,
                           params,
                           parse_string = None,
                           needs_whitespace = True ):
    """
    Returns True if the beginning of the parse string is one element in a list
    of possible elements
    """
    
    if parse_string == None:
      parse_string = self._parse_string
    
    for item in params:
      # Why reinvent the wheel? Use is beginning function from before
      if self._is_beginning( ( item, ),
                             parse_string = parse_string,
                             needs_whitespace = needs_whitespace ):
        return True
    return False

  def _is_beginning( self,
                     grammar_tuple,
                     parse_string = None,
                     needs_whitespace = False ):
    """
    Return True if the beginning of the parse string is the first element in
    the grammar tuple, otherwise return False.  Convenience function
    """
    if parse_string == None:
      parse_string = self._parse_string
    
    if needs_whitespace == True:
      prefix = '{0} '.format( grammar_tuple[ 0 ] )
    else:
      prefix = grammar_tuple[ 0 ]
    if parse_string[ :len( prefix ) ].lower( ) == prefix:
      return True
    return False
  
  def _parse_search( self, grammar_tuple, parse_string = None ):
    """
    Search through the parse string for the beginning and end of the given
    grammar tuple.  Used for leaves only, not something that might be recursed.
    return a list, first element is the grammar part's contents, the second
    element is the remainder of the parse_string.  The beginning and end
    identifiers are stripped
    """
    
    if parse_string == None:
      parse_string = self._parse_string

    
    first_split = parse_string.lower( ).split( grammar_tuple[ 0 ], 1  )

    second_split = first_split[ 1 ].split( grammar_tuple[ 1 ], 1 )
    
    i = [ len( first_split[ 0 ] ) + len( grammar_tuple[ 0 ] ) ]
    i.append( i[ 0 ] + len( second_split[ 0 ] ) )
    i.append( i[ 1 ] + len( grammar_tuple[ 1 ] ) )
    print i
    print len( parse_string )
    return_strings = [ parse_string[ i[ 0 ]: i[ 1 ] ], parse_string[ i[ 2 ]: ] ]
    
    
    return return_strings
  

test_parser = UCParser( )
print test_parser.parse( r'C:\Users\Tyler\Downloads\UT_Weaps\UTWeap_ShockRifle.uc')
#print test_parser._parse_function_body( test_func )
#print test_parser.parse_from_string( test_full_func )
#print type(test_parser._class._children )
print 'chidren:'
for obj in test_parser._class._children[ - 1 ]._children:
  print obj
        