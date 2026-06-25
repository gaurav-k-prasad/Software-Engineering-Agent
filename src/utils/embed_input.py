import json
from structs.chunk_meta_data import ChunkMetaData, Import


def jsonl2datadict(s: str):
    json_dict = json.loads(s)
    json_dict["imports"] = [Import(**_import) for _import in json_dict["imports"]] # converting

    return ChunkMetaData(**json_dict)


def datadict2embed_input(datadict: ChunkMetaData):
    res = ""
    if "class" in datadict.chunk_type:
        res += f"""Type: Class

Qualified Name: {datadict.qualified_name}

"""

        if datadict.methods:
            res += f"Methods:\n"
            for method in datadict.methods:
                res += f"{method}\n"

            res += "\n"

        if datadict.base_classes:
            res += "Inherits From:\n"
            for base_class in datadict.base_classes:
                res += base_class + "\n"

            res += "\n"

    elif "function" in datadict.chunk_type or "method" in datadict.chunk_type:
        is_method = "method" in datadict.chunk_type

        res += f"""Type: {"Method" if is_method else "Function"}

Qualified Name: {datadict.qualified_name}

"""
        if is_method:
            res += f"Parent Class: {datadict.parent_name}\n\n"

        if not datadict.parameters:
            res += "Parameters: None\n\n"
        else:
            res += "Parameters:\n"
            for parameter in datadict.parameters:
                res += parameter + "\n"
            res += "\n"

        if datadict.return_type:
            res += f"Return Type: {datadict.return_type}\n\n"

    elif "module" in datadict.chunk_type:
        res += f"""Type: Module

Qualified Name: {datadict.module_path}

File: {datadict.file_name}

"""
    else:
        raise NotImplementedError(f"{datadict.chunk_type} is not implemented")

    if datadict.imports and "module" not in datadict.chunk_type: # useless imports information in module level information
        res += "Imports:\n"

        for i, _import in enumerate(datadict.imports):
            res += f"{str(_import)}"
            res += ", " if i < len(datadict.imports) - 1 else ""

        res += "\n\n"

    if datadict.decorators:
        res += "Decorators:\n"

        for decorator in datadict.decorators:
            res += f"{decorator}\n"

        res += "\n"

    if "class" not in datadict.chunk_type: # class need not have full source code
        res += "Source Code:\n"
        res += datadict.source_code

    return res
