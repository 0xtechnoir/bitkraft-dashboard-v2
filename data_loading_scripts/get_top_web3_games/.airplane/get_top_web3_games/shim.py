# This file includes a shim that will execute your task code.

try:
    import airplane
except ModuleNotFoundError:
    pass
import importlib.util as util
import inspect
import json
import os
import sys
import traceback


def run(args):
    sys.path.append("/Users/bennaylor/Development/bitkraft/airplane-scripts/get_top_web3_games")

    if len(args) != 2:
        err_msg = "usage: python ./shim.py <args>"
        print(err_msg, file=sys.stderr)
        airplane.set_output(err_msg, "error")
        sys.exit(1)

    os.chdir("/Users/bennaylor/Development/bitkraft/airplane-scripts/get_top_web3_games")

    
    module_name = "mod.get_top_web3_games"
    
    spec = util.spec_from_file_location(module_name, "get_top_web3_games_airplane.py")
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    arg_dict = json.loads(args[1])
    
    ret = mod.get_top_web3_games.__airplane.run(arg_dict)
    
    if ret is not None:
        try:
            airplane.set_output(ret)
        except NameError:
            # airplanesdk is not installed - gracefully print to stdout instead.
            # This makes it easier to use the shim in a dev environment. We ensure airplanesdk
            # is installed in production images.
            sys.stdout.flush()
            print("The airplanesdk package must be installed to set return values as task output.", file=sys.stderr)
            print("Printing return values to stdout instead.", file=sys.stderr)
            sys.stderr.flush()
            print(json.dumps(ret, indent=2))

if __name__ == "__main__":
    try:
        run(sys.argv)
    except Exception as e:
        print(traceback.format_exc(), file=sys.stderr)
        try:
            airplane.set_output(str(e), "error")
        except NameError:
            # airplanesdk is not installed so we can't set the output.
            pass
        sys.exit(1)
