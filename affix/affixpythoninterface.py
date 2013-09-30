try:
  from repyportability import *
except ImportError:
  raise AffixConfigError("Affix framework has not been installed properly.")

_context = locals()
add_dy_support(_context)
dy_import_module_symbols("affixstackinterface")


