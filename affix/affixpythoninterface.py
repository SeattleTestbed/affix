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

<Usage>
  from affixpythoninterface import *

  # Open up a TCP listening server socket on the local host
  # on port 12345 using the Ascii Shifting AFFIX.
  affix_object = AffixStackInterface('(CoordinationAffix)(AsciiShiftingAffix)')
  affix_object.listenforconnection(getmyip(), 12345)
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


