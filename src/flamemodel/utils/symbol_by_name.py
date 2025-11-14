import importlib


def symbol_by_name(name, aliases=None, imp=None, package=None,
                   sep='.', default=None, **kwargs):
    aliases = {} if not aliases else aliases
    if imp is None:
        imp = importlib.import_module

    if not isinstance(name, str):
        return name  # already a class

    name = aliases.get(name) or name
    sep = ':' if ':' in name else sep
    module_name, _, cls_name = name.rpartition(sep)
    if not module_name:
        cls_name, module_name = None, package if package else cls_name
    try:
        try:
            module = imp(module_name, package=package, **kwargs)
        except ValueError as exc:
            raise exc
        return getattr(module, cls_name) if cls_name else module
    except (ImportError, AttributeError):
        if default is None:
            raise
    return default
