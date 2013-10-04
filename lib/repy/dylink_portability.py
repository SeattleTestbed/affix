import safe
import nanny
import emulmisc
import namespace
import repyportability
import virtual_namespace


def _do_nothing(*args):
  pass


def _initialize_safe_module():
    """
    A helper private function that helps initialize
    the safe module.
    """

    # Allow Import Errors.
    safe._NODE_CLASS_OK.append("Import")

    # needed to allow primitive marshalling to be built
    safe._BUILTIN_OK.append("__import__")
    safe._BUILTIN_OK.append("open")
    safe._BUILTIN_OK.append("eval")


    # Allow all built-ins
    for builtin_type in dir(__builtins__):
      if builtin_type not in safe._BUILTIN_OK:
        safe._BUILTIN_OK.append(builtin_type)
    
    for str_type in dir(__name__):
      if str_type not in safe._STR_OK:
        safe._STR_OK.append(str_type)

    safe.serial_safe_check = _do_nothing
    safe._check_node = _do_nothing



def run_unrestricted_repy_code(filename, args_list=[]):
    """
    <Purpose>
        This function allows an user to run a repy file without
        using any restrictions like a normal repy program.

    <Arguments>
        filename - The filename of the repy file you want to run.

        args_list - a list of arguments that need to be passed in
            to the repy file.

    <Exceptions>
        Exception raised if args_list provided is not in the list form.

        Any exception raised by the repy file will be raised.

        Error may be raised if the code in the repy file is not safe.

    <Return>
        None
    """

    if not isinstance(args_list, list):
        raise Exception("args_list must be of list type!")

    # Initialize the safe module before building the context.
    _initialize_safe_module()

    # Prepare the callargs list
    callargs_list = [filename]
    callargs_list.extend(args_list)

    # Prepare the context.
    context = {}
    namespace.wrap_and_insert_api_functions(context)
    context = safe.SafeDict(context)
    context["_context"] = context
    context["createvirtualnamespace"] = virtual_namespace.createvirtualnamespace
    context["getlasterror"] = emulmisc.getlasterror
    context['callfunc'] = 'initialize'
    context['callargs'] = callargs_list


    code = open("dylink.repy").read()

    virt = virtual_namespace.VirtualNamespace(code, name="dylink_code")
    result = virt.evaluate(context) 
