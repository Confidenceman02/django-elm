import types


def loader(module: str, module_path: str) -> types.ModuleType:
    import importlib.machinery

    loader = importlib.machinery.SourceFileLoader(
        module,
        module_path,
    )

    mod = types.ModuleType(loader.name)

    loader.exec_module(mod)

    return mod
