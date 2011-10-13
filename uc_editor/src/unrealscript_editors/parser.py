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
  
  def parse( self, in_file ):

    with open( in_file, 'r' ) as parse_file:
      return self.parse_from_string( parse_file.read( ) )
      
  def parse_from_string( self, parse_string ):
    return self._parser_helper( self._class, parse_string )

  def _comment_split( self, parse_string ):
    
    # Remove leading whitespace
    parse_string = parse_string.lstrip( )

    # Single Line Comments  
    if self._is_beginning( pg.SL_COMMENT, parse_string ):
      return  self._parse_search( pg.SL_COMMENT, parse_string )
    
    elif self._is_beginning( pg.ML_COMMENT, parse_string ):
      return self._parse_search( pg.ML_COMMENT, parse_string )
    
    else:
      return False
  
  
  def _comment_parse( self, parse_string ):
    """
    Parsing for comments and removing whitespace, things that need to happen
    inside of all parsing methods
    """
    
    if self._is_beginning( pg.SL_COMMENT, parse_string ):
      text = self._parse_search( pg.SL_COMMENT, parse_string, strip=True )[ 0 ]
    
    elif self._is_beginning( pg.ML_COMMENT, parse_string ):
      str_text = self._parse_search( pg.ML_COMMENT, parse_string, strip=True )
      text = str_text[ 0 ].split( '\n' )
      if text[ -1 ] == '':
        text.pop( -1 )
    return uc_objects.Comment( text )


  def _parser_helper( self, parent, parse_string = None, block_end = None ):
    """
    The meat of the parsing.
    """

    while len( parse_string ) > 0: 
      parse_string = parse_string.strip( )
      while_string = parse_string
           
      if self._comment_split( parse_string ):
        comment_split = self._comment_split( parse_string )
        new_comment = self._comment_parse( comment_split[ 0 ] )
        parent.add_child( new_comment )
        parse_string = comment_split[ 1 ]
      
      # Class declaration
      
      
      elif self._class_dec_split( parse_string ):
        class_dec_split = self._class_dec_split( parse_string )
        self._class_dec_parse( class_dec_split[ 0 ] )
        parse_string = class_dec_split[ 1 ]

      # Var declarations  
      
      
      elif self._var_dec_split( parse_string ):
        var_dec_split = self._var_dec_split( parse_string )
        new_var = self._var_dec_parse( var_dec_split[ 0 ] )
        parent.add_child( new_var )
        parse_string = var_dec_split[ 1 ]

      # Body Declarations
      elif self._function_split( parse_string ):
        function_split = self._function_split(parse_string)
        new_func = self._function_parse( function_split[ 0 ] )
        parent.add_child( new_func )
        parse_string = function_split[ 1 ]
        
      elif self._state_split(parse_string):
        state_split = self._state_split( parse_string )
        new_state = self._state_parse( state_split[ 0 ] )
        parent.add_child( new_state )
        parse_string = state_split[ 1 ]
        
      
      # Default Properties
      elif self._default_properties_split( parse_string ):
        dp_prop_split = self._default_properties_split(parse_string)
        self._default_properties_parse( dp_prop_split[ 0 ],
                                        default_properties = self._class.get_default_properties( ) )
        parse_string = dp_prop_split[ 1 ]


      if while_string == parse_string:
        parse_string = parse_string[ 1: ]
    
    return parent
        
  
   
  
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
 
  
  
    
    
  def _parse_function_body( self, parse_string ):
    """
    parse the body of an individual function.  This will eventually become more
    complex and actually look at the contents, I believe, but not at this point.
    """
    
    open_brac_count = 0
    i = 0
    while open_brac_count > 0 or not parse_string[ i ] == '}':
      if parse_string[ i ] == '{':
        open_brac_count = open_brac_count + 1
      if parse_string[ i ] == '}':
        open_brac_count = open_brac_count - 1
      i = i + 1

    return( parse_string[ :i ] )

  #============================================================================
  # Grammar Element parsers
  #
  # 
  # There are three different types of methods here.  
  #
  # The first type ( parser methods ) are the most numerous, as these will
  # parse an individual type of element (such as a function, a state, a 
  # default properties property, etc.). 
  #
  # The second type ( search methods ) will be called by parser methods
  # inside of blocks such as the body and the default properties to 
  # determine the exact type of element being parsed.  These will take a large
  # chunk of text and while through it until empty, adding new nodes created
  # by the parser methods to the parent. These don't return anything. 
  #
  # The third type( split methods ) determine the beginning and end of an
  # element type, provided that it is the first thing in the string that it is
  # given.  This way, it serves as both a check for whether this element is
  # the next element, and if it is, it returns the input string split at the
  # end of the next instance of that element.
  #
  #============================================================================
  
  
  # The class
  def _class_dec_split( self, parse_string ):
    if self._is_beginning( pg.CLASS_DEC, parse_string, True ):
      return self._parse_search( pg.CLASS_DEC, parse_string )
    else:
      return False
    
  
  def _class_dec_parse( self, parse_string ):
    """
    Parses the class declaration.  Returns the self._class object, since the 
    object that is having values assigned to it is already created
    """
    
    EXTENDS = 'extends'
    
    # Splits the class dec and the rest of the text
    class_dec = self._parse_search( pg.CLASS_DEC, parse_string, strip = True )
    split_dec = class_dec[ 0 ].split( None )
    self._class.set_class_name( split_dec.pop( 0 ) )
    if len( split_dec ) > 0 :

      if split_dec[ 0 ].lower( ) == EXTENDS:
        self._class.set_class_extends( split_dec[ 1 ] )
        opt_dec = split_dec[ 2: ]
    
    
    self._class.add_params( opt_dec )
    return self._class
  
  
  # Body elements ( Functions, States, Operators )
  
  def _parse_body_dec( self, parse_string ):
    """
    Figures out what type of body declaration is being made and passes the 
    data to the appropriate constructor
    """
    
    # Everything before the first '{', split at whitespaces
    test_split = parse_string.split( '{', 1 )[ 0 ].split( )
    
    for item in test_split:
      if item in pg.FUNC_TYPES:
        return self._parse_function( parse_string )
        
      if item in pg.OPERATOR_TYPES:
        return self._parse_operator( parse_string )
        
      if item in pg.STATE_TYPES:
        return self._parse_state( parse_string )
  
  def _var_dec_split( self, parse_string ):
    if self._is_beginning( pg.VAR_DEC, parse_string, True ):
      return self._parse_search( pg.VAR_DEC, parse_string )
    
    else:
      return False
    
  def _var_dec_parse( self, parse_string ):
    new_var = uc_objects.Variable( )
    
    stripped = self._parse_search( pg.VAR_DEC, parse_string, True )
    split_dec = stripped[ 0 ].split( )
    new_var.set_name( split_dec.pop( -1 ) )
    new_var.set_type( split_dec.pop( -1 ) )
    
    return new_var
      
  
  def _function_split( self, parse_string ):
    
    if self._is_param_beginning( pg.FUNC_PARAMS + pg.FUNC_TYPES, parse_string ):
      bracket_split = parse_string.split( '{', 1 )
      for item in bracket_split[ 0 ].split( ):
        if item in pg.FUNC_TYPES:
          body_split = self._split_closing_bracket( bracket_split[ 1 ], False )
          
          i = len( bracket_split[ 0 ] ) + 1 + len( body_split[ 0 ] )
          
          return [ parse_string[ :i ], parse_string[ i: ] ]  
          
      
    return False

  def _function_parse( self, parse_string ):
    """
    Currently aiming to get a string of all function params.  I'm currently
    treating 'Native (INT)' as an edge case, until I need to implement it.
    """
    
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
    
    
    #new_func.set_body( body_parse )

    return new_func
  
  def _state_split( self, parse_string ):
  
    if self._is_param_beginning( pg.STATE_PARAMS + pg.STATE_TYPES, parse_string, True ):
      bracket_split = parse_string.split( '{', 1 )
      for item in bracket_split[ 0 ].split( ):
        if item in pg.STATE_TYPES:
          body_split = self._split_closing_bracket( bracket_split[ 1 ], False )
          
          i = len( bracket_split[ 0 ] ) + 1 + len( body_split[ 0 ] )
          
          return [ parse_string[ :i ], parse_string[ i: ] ] 
  
  def _state_parse( self, parse_string ):

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
    new_state.set_body( body_parse[ 0 ] )
    remainder = body_parse[ 1 ]
    
    return new_state

  def _default_properties_split( self, parse_string ):
    if self._is_beginning( pg.DEFAULT_PROPERTIES_DEC, parse_string ):
      return self._parse_search( pg.DEFAULT_PROPERTIES_DEC, parse_string )
    
    else:
      return False
  
  def _default_properties_parse( self,
                                 parse_string,
                                 default_properties = uc_objects.DefaultProperites( ) ):

    assert isinstance( default_properties, uc_objects.DefaultProperites )

    prop_block_pre_split = self._parse_search( ('{', '}' ),
                                               parse_string,
                                               strip = True )

    props = prop_block_pre_split[ 0 ].strip( )
    
    self._default_properties_search( props,
                                     default_properties )

    return default_properties
  
  def _default_properties_search( self, parse_string, parent ):
    """
    parse the default properties block of the class
    """
    
    while len( parse_string ) > 0:
      
      parse_string = parse_string.strip( )
      
      if self._comment_split(parse_string):
        comment_split = self._comment_split(parse_string)
        new_comment = self._comment_parse( comment_split[ 0 ] )
        parent.add_child( new_comment )
        parse_string = comment_split[ 1 ]
         
      
      elif self._dp_object_split(parse_string):
        dp_obj_split = self._dp_object_split( parse_string )
        new_dp_obj = self._dp_object_parse( dp_obj_split[ 0 ] )
        parent.add_child( new_dp_obj )
        parse_string = dp_obj_split[ 1 ]
         
      
      elif self._dp_prop_split(parse_string):
        dp_prop_split = self._dp_prop_split(parse_string)
        new_dp_prop = self._dp_prop_parse( dp_prop_split[ 0 ] )
        parent.add_child( new_dp_prop )
        parse_string = dp_prop_split[ 1 ] 
  
  def _dp_prop_split( self, parse_string ):
    split_string = parse_string.split( '\n', 1 )
    if pg.DP_OBJECT_DEC[ 0 ] not in split_string[ 0 ] and '=' in split_string[ 0 ]:
      if len( split_string ) == 1:
        split_string.append( '' )
      return split_string

  
  def _dp_prop_parse( self, parse_string ):
    split_prop = parse_string.split( '=' )
    
    new_prop = uc_objects.DPProperty( split_prop[ 0 ], split_prop[ 1 ] )
    return new_prop
  
  def _dp_object_split( self, parse_string ):
    if self._is_beginning( pg.DP_OBJECT_DEC, parse_string ):
      return self._parse_search( pg.DP_OBJECT_DEC, parse_string, False )
    return False
    
    
  def _dp_object_parse( self, parse_string ):
    """
    Parse an object declared in the default properties.  
    """

    new_obj = uc_objects.DPObject( )
    
    search_object = self._parse_search( pg.DP_OBJECT_DEC, parse_string, True )
    split_object = search_object[ 0 ].strip( ).split( '\n', 1 )
    
      
    
    if len( split_object ) > 1:
      self._default_properties_search( split_object[ 1 ], new_obj )
    
    return new_obj
    

  #============================================================================
  # Convenience Functions
  #============================================================================

  def _split_closing_bracket( self, parse_string, strip = True ):
    open = 1
    i = 0
    while open > 0:
      if parse_string[ i ] == '{':
        open = open + 1
      elif parse_string[ i ] == '}':
        open = open - 1
        
      i = i + 1
    if strip == False:  
      return [ parse_string[ :i ], parse_string[ i: ] ]
    else:
      return [ parse_string[ :i - 1 ], parse_string[ i: ] ]
    

  def _is_param_beginning( self,
                           params,
                           parse_string,
                           needs_whitespace = True ):
    """
    Returns True if the beginning of the parse string is one element in a list
    of possible elements
    """

    
    for item in params:
      # Why reinvent the wheel? Use is beginning function from before
      if self._is_beginning( ( item, ),
                             parse_string = parse_string,
                             needs_whitespace = needs_whitespace ):
        return True
    return False

  def _is_beginning( self,
                     grammar_tuple,
                     parse_string,
                     needs_whitespace = False ):
    """
    Return True if the beginning of the parse string is the first element in
    the grammar tuple, otherwise return False.  Convenience function
    """

    if needs_whitespace == True:
      prefix = '{0} '.format( grammar_tuple[ 0 ] )
    else:
      prefix = grammar_tuple[ 0 ]
    if parse_string[ :len( prefix ) ].lower( ) == prefix:
      return True
    return False
  
  def _parse_search( self, grammar_tuple, parse_string, strip = False ):
    """
    Search through the parse string for the beginning and end of the given
    grammar tuple.  Used for leaves only, not something that might be recursed.
    return a list, first element is the grammar part's contents, the second
    element is the remainder of the parse_string.  The beginning and end
    identifiers are not stripped, but included in the first item (the parse
    element).
    """
    
    first_split = parse_string.lower( ).split( grammar_tuple[ 0 ], 1  )

    second_split = first_split[ 1 ].split( grammar_tuple[ 1 ], 1 )
    
    if strip == False:
      i = [ len( first_split[ 0 ] ) ]
      i.append( i[ 0 ] + len( second_split[ 0 ] ) 
                       + len( grammar_tuple[ 0 ] )
                       + len( grammar_tuple[ 1 ] ) )
      i.append( i[ 1 ] )
    else:
      i = [ len( first_split[ 0 ] ) + len( grammar_tuple[ 0 ] ) ]
      i.append( i[ 0 ] + len( second_split[ 0 ] ) )
      i.append( i [ 1 ] + len( grammar_tuple[ 1 ] ) )
    
    return_strings = [ parse_string[ i[ 0 ]: i[ 1 ] ], parse_string[ i[ 2 ]: ] ]
    
    
    return return_strings
  

test_parser = UCParser( )
c = test_parser.parse( r'C:\Users\Tyler\Downloads\UT_Weaps\UTWeap_ShockRifle.uc')
#print test_parser._parse_function_body( test_func )
#print test_parser.parse_from_string( test_full_func )
#print type(test_parser._class._children )
print 'chidren:'
for obj in test_parser._class._children:
  print obj
  if isinstance( obj, uc_objects.Comment ):
    print obj.write_to_string( )
print 'dp'
#print test_parser._class._default_properties.write_to_string( )
        