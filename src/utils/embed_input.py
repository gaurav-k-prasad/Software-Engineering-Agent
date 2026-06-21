import json
from structs.chunk_meta_data import ChunkMetaData, Import


def jsonl2datadict(s: str):
    json_dict = json.loads(s)
    print(len(json_dict["source_code"]))
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

Qualified Name: {datadict.qualified_name}

File: {datadict.file_name}

"""
    else:
        raise NotImplementedError(f"{datadict.chunk_type} is not implemented")

    if datadict.imports:
        res += "Imports:\n"

        for _import in datadict.imports:
            res += f"{str(_import)} "

        res += "\n"

    if datadict.decorators:
        res += "Decorators:\n"

        for decorator in datadict.decorators:
            res += f"{decorator}\n"

        res += "\n"

    res += "Source Code:\n"
    res += datadict.source_code

    return res
