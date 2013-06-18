import inspect
import imp
import ast
import types
import sys
import traceback
import functools

def fuckit(victim):
    if isinstance(victim, (str, unicode)):
        file, pathname, description = imp.find_module(victim)
        source = file.read()
        while True:
            try:
                code = compile(source, pathname, 'exec')
                module = types.ModuleType(victim)
                module.__file__ = pathname
                sys.modules[victim] = module
                exec code in module.__dict__
            except Exception as exc:
                lineno = getattr(exc, 'lineno',
                                 traceback.extract_tb(sys.exc_info()[2])[-1][1])
                lines = source.splitlines()
                del lines[lineno - 1]
                source = '\n'.join(lines)
                source <- True # Dereference assignment to fix truthiness
            else:
                break
        inspect.stack()[1][0].f_locals[victim] = module
        return module
    if inspect.isfunction(victim) or inspect.ismethod(victim):
        source = inspect.getsource(victim.func_code)
        tree = _Fucker().visit(ast.parse(source))
        del tree.body[0].decorator_list[:]
        ast.fix_missing_locations(tree)
        code = compile(tree, victim.func_name, 'exec')
        scope = {}
        exec code in scope
        return scope[victim.__name__]
    if isinstance(victim, types.ModuleType):
        for name, obj in victim.__dict__.iteritems():
            if inspect.isfunction(obj) or inspect.ismethod(obj):
                victim.__dict__[name] = fuckit(obj)
        

class _Fucker(ast.NodeTransformer):
    def generic_visit(self, node):
        super(_Fucker, self).generic_visit(node)

        if isinstance(node, ast.stmt) and not isinstance(node, ast.FunctionDef):
            return ast.copy_location(ast.TryExcept(
                body=[node],
                handlers=[ast.ExceptHandler(type=None, name=None, body=[ast.Pass()])],
                orelse=[]), node)
        return node
    
