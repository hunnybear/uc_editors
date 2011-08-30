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
      self.parse_from_string( parse_file.read( ) )
      
  def parse_from_string( self, parse_string ):
    self._parser_helper( self._class, parse_string)
  
  def _parser_helper( self, parent, in_parse_string, block_end = None ):
    """
    The meat of the parsing.
    """
    parse_string = in_parse_string
    print 'parser helper'
    
    while len( parse_string ) > 0: 
      while_string = parse_string
      #==========================================================================
      # Non-Recursive elements
      #==========================================================================
      
      # Remove leading whitespace
      parse_string = parse_string.lstrip( )
      
      # Single Line Comments  
      if self._is_beginning( parse_string, pg.SL_COMMENT ):
        print 'found sl comment'
        parse = self._parse_search( parse_string, pg.SL_COMMENT )
        new_comment = uc_objects.Comment( parse[ 0 ] )
        parse_string = parse[ 1 ]
        parent.add_child( new_comment )

      # Multi-line comments    
      # Same as single line comments except for the "M" instead of "S" 
      elif self._is_beginning( parse_string, pg.ML_COMMENT ):
        print 'found ml comment'
        parse = self._parse_search( parse_string, pg.ML_COMMENT )
        
        print 'ml parse: {0}'.format( parse )
        new_comment = uc_objects.Comment( parse[ 0 ] )
        parse_string = parse[ 1 ]
        parent.add_child( new_comment )
        
      elif self._is_beginning( parse_string, pg.CLASS_DEC ):
        parse_string = self._parse_class_dec( parse_string )

      # Var declarations  
      elif self._is_beginning( parse_string, pg.VAR_DEC ):
        parse = self._parse_search( parse_string, pg.VAR_DEC )
        print 'var parse: {0}'.format( parse )
        parse_string = parse[ 1 ]

      # Normal Fucntion Declarations
      elif self._is_param_beginning( parse_string, pg.FUNC_PARAMS ):
        print 'func parse'
        parse_string = self._parse_function( parse_string, parent )
        
      
      # State Declarations
      elif self._is_param_beginning( parse_string, pg.STATE_PARAMS ):
        parse_string = self._parse_state( parse_string, parent )
     
      if while_string == parse_string:
        parse_string = parse_string[ 1: ]
  
  def _parse_declarations( self ):
    pass
  
  def _parse_body_dec( self, parse_string ):
    """
    Handles parsing operations on body declartions that are common to all types
    ( Normal Functions, Operator Functions, and States )
    returns anything left of the top block, split by whitespace, and the
    remainder (all code after the object that is not part of it)
    """
    
    
    
    split = parse_string.split( '{', 1 )
    
    # Everything outside of the body of the object
    top_block = split[ 0 ].strip( )
    params = [ ]
    
    print top_block
    
    # Look for what type of object this is
    
    if '(' in top_block:
      args = top_block.split( '(' )[ 1 ].split( ')' )[ 0 ]
      top_block = top_block.split( '(' )[ 0 ].strip( )
    
    
    
    # Name/Identifier
    split_top = top_block.split( )
    name = split_top.pop( -1 )
    
    # Params
    while split_top[ 0 ].lower( ) in pg.FUNC_PARAMS:
      params.append( split_top[ 0 ].lower( ) )
      split_top.pop( 0 )
      
    new_object.set_params( params )
    
    # This method will eventually be more complex, for now it just gets the
    # chunk of text that is the body of the function.
    if isinstance( new_object, uc_objects.Function ):
      body_parse = self._parse_function_body( split[ 1 ] )
      new_object.set_body( body_parse [ 0 ] )
      remainder = body_parse [ 1 ]
      
    elif isinstance( new_object, uc_objects.State ):
      body_parse = self._parse_state_body( split[ 1 ] )
      new_object.set_body( body_parse[ 0 ] )
      remainder = body_parse[ 1 ]
      
    return ( split_top, remainder )
      
    
    
  def _parse_state( self, parse_string, parent ):
    new_state = uc_objects.State( )
    
    self._parse_common_body_dec( new_state, parse_string)
    
    
  
  def _parse_function( self, parse_string, parent ):
    """
    Currently aiming to get a string of all function params.  I'm currently
    treating 'Native (INT)' as an edge case, until I need to implement it.
    """
    new_func = uc_objects.NormalFunction( )
    parent.add_child( new_func )
    
    common_parse = self._parse_common_body_dec( new_func, parse_string )
    
    split_top = common_parse[ 0 ]
    
    # Function Type (either function, event, or delegate)
    assert split_top[ 0 ].lower( ) in pg.FUNCTION_TYPES, '{0} not valid'.format( split_top[ 0 ])
    new_func.set_type( split_top.pop( 0 ) )
    
    # The rest should be localtype, if it exists
    if not len( split_top ) == 0:
      new_func.set_local_type( ' '.join( split_top ) )
 
    print 'test printout: '
    #print new_func.get_body( )
    #print 'localtype: {0}'.format( new_func.get_local_type( ) )
    print 'name: {0}'.format( new_func.get_name( ) )
    print 'type: {0}'.format( new_func.get_type( ) )
    
    return common_parse[ 1 ]
    
    
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
      
    return( parse_string[ :i ], parse_string[ i + 1: ] )

  
  def _parse_class_dec( self, parse_text ):
    """
    Parses the class declaration
    """
    EXTENDS = 'extends'
    
    # Splits the class dec and the rest of the text
    split_parse_text = self._parse_search( parse_text, pg.CLASS_DEC )
    class_dec = split_parse_text[ 0 ]
    
    split_dec = class_dec.split( None, 1 )
    self._class.set_class_name( split_dec[ 0 ] )
    if len( split_dec ) > 1 :
      
      opt_dec = class_dec.split( None )[ 1: ]
      
      if opt_dec[ 0 ].lower( ) == EXTENDS:
        self._class.set_class_extends( opt_dec[ 1 ] )
        opt_dec = opt_dec[ 2: ]
    
    self._class.add_params( opt_dec )
    
    # return non-parsed text
    return split_parse_text[ 1 ]

  def _is_param_beginning( self, parse_string, params ):
    """
    Returns True if the beginning of the parse string is one element in a list
    of possible elements
    """
    for item in params:
      # Why reinvent the wheel? Use is beginning function from before
      if self._is_beginning( parse_string, ( item ) ):
        return True
    return False

  def _is_beginning( self, parse_string, grammar_tuple ):
    """
    Return True if the beginning of the parse string is the first element in
    the grammar tuple, otherwise return False.  Convenience function
    """
    if parse_string[ :len( grammar_tuple[ 0 ] ) ].lower( ) == grammar_tuple[ 0 ]:
      return True
    return False
  
  def _parse_search( self, parse_string, grammar_tuple ):
    """
    Search through the parse string for the beginning and end of the given
    grammar tuple.  Used for leaves only, not something that might be recursed.
    return a list, first element is the grammar part's contents, the second
    element is the remainder of the parse_string.  The beginning and end
    identifiers are stripped
    """
    
    new_parse_string = parse_string[ len( grammar_tuple[ 0 ] ): ]
    element_string = ''
    
    while not new_parse_string[ :len( grammar_tuple[ 1 ] ) ].lower( ) == grammar_tuple[ 1 ]:
      element_string = element_string + new_parse_string[ 0 ]
      new_parse_string = new_parse_string[ 1: ]
      
    # Strip the end identifier
    new_parse_string = new_parse_string[ len( grammar_tuple[ 1 ] ): ]
    
    return [ element_string, new_parse_string ]
  
  
  
#print test_text
test_parser = UCParser( )
print test_parser.parse( r'C:\Users\Tyler\Downloads\UT_Weaps\UTWeap_ShockRifle.uc')
#print test_parser._parse_function_body( test_func )
#print test_parser.parse_from_string( test_full_func )
#print type(test_parser._class._children )
print 'children: {0}'.format( test_parser._class._children )
        