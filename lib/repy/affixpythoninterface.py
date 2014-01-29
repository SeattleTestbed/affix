"""
<Program>
  affixpythoninterface.py

<Started>
  September 30th, 2013

<Description>
  This library is a very simple interface that allows
  python applications to import the AFFIX framework
  with ease. This program has no other purpose other
  then to import affixstackinterface.repy, such that
  it can be used in Python applications. For further
  documentation on the AFFIX framework core code, 
  please look in the files affixstackinterface.repy
  and affix_stack.repy.

<Description>
  TODO: Write up a proper description after all methods
  have been implemented.

<Usage>
  from affixpythoninterface import *

  # Open up a TCP listening server socket on the local host
  # on port 12345 using the Ascii Shifting AFFIX.
  set_affix_string('(CoordinationAffix)(AsciiShiftingAffix)')
  listenforconnection(getmyip(), 12345)
"""

# Import the core repy functions so the repy API is available
# for the python application. 
try:
  from repyportability import *
except ImportError:
  raise AffixConfigError("Affix framework has not been installed properly.")

# Setup Dylink, which is the dynamic linker in repy that
# is used to import files in repy.
_context = locals()
add_dy_support(_context)
dy_import_module_symbols("affixstackinterface")


# If in debug mode, we will print out extra information.
debug_mode = True


# By default our affix string will be just the
# Coordination AFFIX and default virtual host
# name will be the local ip address.
AFFIX_STRING="(CoordinationAffix)"
virtual_host_name = getmyip()


# Store the old Repy API calls that we overload
# in case we need them.
old_repy_api = {}
old_repy_api['getmyip'] = getmyip
old_repy_api['sendmessage'] = sendmessage
old_repy_api['gethostbyname'] = gethostbyname
old_repy_api['openconnection'] = openconnection
old_repy_api['listenformessage'] = listenformessage
old_repy_api['listenforconnection'] = listenforconnection




def overload_repy_network_api(affix_object=None):
  """
  <Purpose>
    The purpose of this function is to overload the original
    Repy network API with the AFFIX framework. After this 
    function has been invoked, the application that imports
    this file will not be able to call the original Repy API.
  
  <Arguments>
    affix_object 

  <Side Effects>
    Some of the original Repy API calls related to networks
    cannot be called anymore.

  <Exceptions>
    None

  <Return>
    None
  """

  if not affix_object:
    affix_object = AffixStackInterface(AFFIX_STRING, virtual_host_name)

  if debug_mode:
    print "Trying to set AFFIX string to: " + AFFIX_STRING

  assert isinstance(affix_object, AffixStackInterface), "Argument must be of type: AffixStackInterface"
  

  # Overload all the network API.
  global getmyip
  global sendmessage
  global openconnection
  global listenformessage
  global listenforconnection

  getmyip = affix_object.getmyip
  sendmessage = affix_object.sendmessage
  openconnection = affix_object.openconnection
  listenformessage = affix_object.listenformessage
  listenforconnection = affix_object.listenforconnection
 



def set_affix_string(new_affix_string):
  """
  <Purpose>
    The purpose of this function is to change the
    AFFIX string that will be used for each of the
    network calls. After the AFFIX string is changed,
    any new calls that create a socket will use the
    new string.

  <Arguments>
    new_affix_string - the affix string the user wants to use
      for all network operations.

  <Side Effects>
    A new AffixStackInterface object is created.

  <Exception>
    None.

  <Return>
    None.
  """

  global AFFIX_STRING
  AFFIX_STRING = new_affix_string

  # Once we have set the new AFFIX string, we want to recreate
  # the AffixStackInterface object and overload the network 
  # operations with the new object.
  overload_repy_network_api()




def set_virtual_host_name(new_virtual_name):
  """
  Implement a method that overwrites the virtual host
  name for the AffixStackInterface object.
  """
  pass



def set_affixstackinterface_object(new_affixstackinterface_object):
  """
  Implement a method that allows user to create their own instance
  of AffixStackInterface object and set it for their application.
  """
  pass



overload_repy_network_api()

