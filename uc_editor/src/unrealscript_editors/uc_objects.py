'''
Created on Aug 28, 2011

@author: Tyler
'''

import parser_grammar as pg


class UCObjectBase( object ):
  """
  Base Abstract UC Unrealscript Object
  """
  def __repr__( self ):
    return '< UC {0} object >'.format( self.__class__.__name__ )

  

class UCParentBase( UCObjectBase ):
  VALID_CHILDREN = ( UCObjectBase )
  
  def __init__( self ):
    self._children = [ ]
  
  def add_child( self, object ):
    assert isinstance( object, self.VALID_CHILDREN )
    if not object in self._children:
      self._children.append( object )
      
  def remove_child( self, object ):
    if object in self._children:
      self._children.remove( object )
      
  

class Comment( UCObjectBase ):
  """
  an Unrealscript comment
  """
  def __init__( self, comment_text = [ ] ):
    if isinstance( comment_text, ( list, tuple ) ):
      self._text = comment_text
    else:
      self._text = [ comment_text ]  
    
    UCObjectBase.__init__( self )
    
  def get_text( self ):
    return self._text
  
  def set_text( self, text ):
    if isinstance( text, basestring ):
      text = [ text ] 
    self._text = text
    
  def append( self, object ):
    if isinstance( object, Comment ):
      self._text = self._text + object.get_text( )
    
    elif isinstance( object, ( list, tuple ) ):
      self._text = self._text + object 
      
    else:
        self._text = self._text.append( object )
        
  def write_to_string( self, tabs = 0  ):
    repr(  self._text )
    ws = WriteString( )
    
    if len( self._text ) > 1:

      ws.append( pg.ML_COMMENT[ 0 ], tabs )
      for l in self._text:
        ws.append( l, tabs )
        
      ws.append( pg.ML_COMMENT[ 1 ], tabs )
      
    else:
      ws.append( pg.SL_COMMENT[ 0 ] + self._text[ 0 ], tabs )
      
    return ws.write( )
  
  def __repr__( self ):
    return '< UC Comment object( {0!r} )>'.format( self._text )
      
class ClassDelcarations( UCParentBase ):
  """
  The Declarations at the beginning of an unrealscript class
  """

class ClassBody( UCParentBase ):
  """
  The body of an unrealscript class (its functions, operators, and states)
  """
  
class DefaultProperites( UCParentBase ):
  """
  The Default Properties block of an unrealscript class
  """

  
class Class( UCParentBase ):
  """
  Unrealscript class
  """
  def __init__( self, class_name = None, class_extends = None, params = [ ] ):
    self._class_name = class_name
    self._class_extends = class_extends
    self._params = list( set( params ) )

    self._default_properties = DefaultProperites( )

    UCParentBase.__init__( self )
    
  def set_class_name( self, name ):
    self._class_name = name
    
  def get_class_name( self ):
    return self._class_name
  
  def set_class_extends( self, name ):
    self._class_extends = name
    
  def get_class_extends( self ):
    return self._class_extends
  
  def add_param( self, param ):
    self._params = list( set( self._params.append( param ) ) )
      
  def add_params( self, params ):
    self._params = list( set( self._params + params ) )
    
  def get_params( self ):
    return self._params
  
  def remove_params( self, params ):
    for param in params:
      self.remove_param( param )
      
  def remove_param( self, param ):
    self._params.remove( param )
    
  def write_to_string( self ):
    pass
  
  def get_default_properties( self ):
    return self._default_properties
  
  def set_default_properties( self, default_properties ):
    self._default_properties = default_properties

class BaseVar( UCObjectBase ):
  def __init__( self, name = None, value = None ):
    self._value = value
    self._name = name

    
  def set_value( self, value ):
    self._value = value
    
  def get_value( self ):
    return self._value
  
  def set_name( self, name ):
    self._name = name
    
  def get_name( self ):
    return self._name 
  
  def __repr__( self ):
    return '< UC {0} object( Name = {1!r}, Value = {2!r} )>'.format( self.__class__.__name__,
                                                                     self._name,
                                                                     self._value )
    
class Variable( BaseVar ):
  def __init__( self, name = None, value = None, type = None ):
    
    BaseVar.__init__( self, name, value )
    self._type = type

  def set_type( self, type ):
    self._type = type
  
  def get_type( self ):
    return self._type
  
  def __repr__( self ):
    return '< UC {0} object( Name = {1!r}, Type = {2!r} )>'.format( self.__class__.__name__,
                                                                    self._name,
                                                                    self._type )
  
class Const( BaseVar ):
  """
  Extension of basevar, doesn't make any changes atm.
  """
  pass

class UCBodyDecBase( UCParentBase ):
  """
  Abstract base for all body declarations( Function, State, Operator )
  """
  def __init__( self,
                name = None,
                params = [ ],
                *args, **kwargs ):
    
    self._name = name
    self._params = params
    self._body = ''
    
    UCParentBase.__init__( self )
    
  def set_name( self, name ):
    self._name = name
    
  def get_name( self ):
    return self._name
  
  def set_params( self, params ):
    self._params = params
    
  def append_to_params( self, params ):
    if isinstance( params, ( list, tuple ) ):
      self._params = self._params + params
      
    elif isinstance( params, basestring ):
      self._params.append( params )

  def set_body( self, body ):
    self._body = body
    
  def append_to_body( self, body ):
    self._body = body + body
    
  def get_body( self ):
    return self._body
  
  def write_to_string( self, tabs = 0 ):
    pass
  
  
class State( UCBodyDecBase ):
  def __init__( self,
                name = None,
                params = [ ],
                config_group = None,
                extends = None,
                *args, **kwargs ):
    
    self._config_group = config_group
    self._extends = extends
    UCBodyDecBase.__init__( self, *args, **kwargs )
    
    def set_config_group( self, config_group ):
      self._config_group = config_group
      
    def get_config_group( self ):
      return self._config_group
    
    def set_extends( self, name ):
      self._extends = name
      
    def get_extends( self ):
      return self._extends
  

class DPProperty( UCObjectBase ):
  def __init__( self, name = None, value = None ):
    
    self._value = value
    self._name = name
    
  def set_name( self, name ):
    self._name = name
    
  def get_name( self ):
    return self._name 
    
  def set_value( self, value ):
    self._value = value
    
  def get_value( self ):
    return self._value
  
  def __repr__( self ):
    return '< UC {0} object( Name = {1!r}, Value = {2!r} )>'.format( self.__class__.__name__,
                                                                     self._name,
                                                                     self._value )
    

class DPObject( UCParentBase ):
  VALID_CHIDLREN = ( DPProperty )
  
  def __init__( self, name = None, obj_class = None ):
    self._class = obj_class
    self._name = name
    UCParentBase.__init__( self )
  
  def add_child( self, object ):
    assert isinstance( object, DPProperty )
    UCParentBase.add_child(self, object)
    
  def set_name( self, name ):
    self._name = name
    
  def get_name( self ):
    return self._name
  
  def set_class( self, obj_class ):
    self._class = obj_class
  def get_class( self ):
    return self._class
  
  def __repr__( self ):
    return '< UC {0} object( Name = {1!r}, class = {2!r} )>'.format( self.__class__.__name__,
                                                                     self._name,
                                                                     self._class )
    
  def write_to_string( self, tab_size = 0 ):
    
    ws = WriteString( tab_size = tab_size )
    
    
class Function( UCBodyDecBase ):
  def __init__( self,
                name = None,
                params = [ ],
                type = None,
                *args, **kwargs ):

    self._type = type
    
    UCBodyDecBase.__init__( self, *args, **kwargs )
      
  def set_type( self, type ):
    self._type = type
    
  def get_type( self ):
    return self._type
  
  def __repr__( self ):
    return '< UC {0} object( Name = {1!r} ) >'.format( self.__class__.__name__,
                                                       self._name )
  
  def write_to_string( self, tabs = 0 ):
    pass

class NormalFunction( Function ):
  
  def __init__( self, local_type = None, *args, **kwargs ):
    self._local_type = local_type
    Function.__init__( self, *args, **kwargs )
    
  def set_local_type( self, type ):
    self._local_type = type
    
  def get_local_type( self ):
    return self._local_type
  
  
#==============================================================================
# Convenience Objects
#==============================================================================
  
class WriteString( object ):
  """
  This object is used by the UC objects to assist in writing output strings
  """
  def __init__( self, tab_size = 2 ):
    self._string = ''
    self._tab_size = tab_size
    
  def set_string( self, string ):
    self._string = string
    
  def get_string( self ):
    return self._string

  def set_tab_size( self, tab_size ):
    self._tab_size = tab_size
  
  def get_tab_size( self ):
    return self._tab_size
  
  def append( self, append_string, tabs ):
    new_line = '\n'
    if self._string == '':
      new_line = ''
    tab_string = ' '*self._tab_size * tabs
    self._string = '{0}{1}{2}{3}'.format( self._string,
                                          new_line,
                                          tab_string,
                                          append_string )
    
  def write( self ):
    return self._string
  