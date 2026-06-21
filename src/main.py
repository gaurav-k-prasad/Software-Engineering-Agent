import os
from pprint import pprint
from pathlib import Path
from typing import IO

import tree_sitter_python as tspython
from tree_sitter import Language, Node, Parser
from collections import deque
from structs.chunk_meta_data import ChunkMetaData, Import
from uuid import uuid4
from utils.constants import SEMANTIC_CHUNKS

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)


def extract_function(
    node: Node,
    decorator_names: list[str],
    parent_metadata: ChunkMetaData,
) -> ChunkMetaData:
    assert (
        node.type == SEMANTIC_CHUNKS["FUNCTION"]
    ), f"Node type should be of {SEMANTIC_CHUNKS['FUNCTION']}"

    res = ChunkMetaData()

    res.chunk_id = str(uuid4())
    chunk_type = "function"

    if "class" in parent_metadata.chunk_type:
        chunk_type = "method"
    elif "function" in parent_metadata.chunk_type:
        chunk_type = "nested_function"
    res.chunk_type = chunk_type

    name_node = node.child_by_field_name("name")
    if not name_node or not name_node.text:
        raise ValueError(f"{chunk_type} name not found")
    name = name_node.text.decode()
    res.name = name
    res.qualified_name = parent_metadata.qualified_name + "." + res.name
    res.parent_name = parent_metadata.name
    res.parent_type = parent_metadata.chunk_type
    res.file_path = parent_metadata.file_path
    res.file_name = parent_metadata.file_name
    res.module_path = parent_metadata.module_path
    res.language = parent_metadata.language
    res.start_line = node.start_point.row  # 0 based indexing
    res.end_line = node.end_point.row  # 0 based indexing

    if not node.text:
        raise ValueError("No source code found")
    res.source_code = node.text.decode()

    res.parameters = []
    parameter_node = node.child_by_field_name("parameters")
    if not parameter_node:
        raise ValueError("No parameters found")

    for parameter in parameter_node.named_children:
        if not parameter or not parameter.text:
            raise ValueError("No parameter name")

        res.parameters.append(parameter.text.decode())

    res.return_type = None
    return_type_node = node.child_by_field_name("return_type")
    if return_type_node and return_type_node.text:
        res.return_type = return_type_node.text.decode()

    res.decorators = decorator_names
    res.is_async = any(child.type == "async" for child in node.children)
    res.base_classes = []  # no inheritance in SEMANTIC_CHUNKS['FUNCTION']
    res.imports = []  # no Import in function_definition
    parent_metadata.contains.append(res.qualified_name)

    if chunk_type == "method":
        parent_metadata.methods.append(name)
    res.contained_in = res.parent_name

    return res


def extract_class(
    node: Node,
    decorator_names: list[str],
    parent_metadata: ChunkMetaData,
) -> ChunkMetaData:
    assert (
        node.type == SEMANTIC_CHUNKS["CLASS"]
    ), f"Node type should be of {SEMANTIC_CHUNKS['CLASS']}"

    res = ChunkMetaData()

    res.chunk_id = str(uuid4())
    chunk_type = "class"
    if parent_metadata.chunk_type != "module":
        chunk_type = "nested_class"
    res.chunk_type = chunk_type

    name_node = node.child_by_field_name("name")
    if not name_node or not name_node.text:
        raise ValueError(f"{chunk_type} name not found")
    name = name_node.text.decode()
    res.name = name
    res.qualified_name = parent_metadata.qualified_name + "." + res.name
    res.parent_name = parent_metadata.name
    res.parent_type = parent_metadata.chunk_type
    res.file_path = parent_metadata.file_path
    res.file_name = parent_metadata.file_name
    res.module_path = parent_metadata.module_path
    res.language = parent_metadata.language
    res.start_line = node.start_point.row  # 0 based indexing
    res.end_line = node.end_point.row  # 0 based indexing
    res.source_code = node.text.decode() if node.text else ""

    res.parameters = []  # no parameters in SEMANTIC_CHUNKS['CLASS'] declaration
    res.return_type = None  # no return type in SEMANTIC_CHUNKS['CLASS'] declaration
    res.decorators = decorator_names
    res.is_async = False  # SEMANTIC_CHUNKS['CLASS'] is not async

    res.base_classes = []
    superclasses_node = node.child_by_field_name("superclasses")
    if superclasses_node:
        for superclass in superclasses_node.named_children:
            if superclass.text:
                res.base_classes.append(superclass.text.decode())

    res.imports = []  # no Import in class_definition
    parent_metadata.contains.append(res.qualified_name)

    res.contained_in = res.parent_name

    return res


def extract_decorator(
    node: Node,
    parent_metadata: ChunkMetaData,
) -> ChunkMetaData | None:
    assert (
        node.type == SEMANTIC_CHUNKS["DECORATOR"]
    ), f"Node type should be of {SEMANTIC_CHUNKS['DECORATOR']}"

    decorator_names = []

    for dec in node.named_children:
        if dec.type == "decorator":
            if not dec or not dec.text:
                raise ValueError(f"No identifier name found for decorator")

            decorator_name = dec.text.decode()
            decorator_names.append(decorator_name)
        elif dec.type == SEMANTIC_CHUNKS["FUNCTION"]:
            return extract_function(dec, decorator_names, parent_metadata)

        elif dec.type == SEMANTIC_CHUNKS["CLASS"]:
            return extract_class(dec, decorator_names, parent_metadata)

    return None


def get_imports(node: Node) -> list[Import]:
    assert (
        node.type == "import_statement" or node.type == "import_from_statement"
    ), f"Node type should be import statement"

    res: list[Import] = []

    if node.type == "import_statement":
        modules = node.children_by_field_name("name")
        for name_node in modules:
            if name_node.type == "aliased_import":
                name = name_node.child_by_field_name("name")
                alias = name_node.child_by_field_name("alias")
            else:
                name = name_node
                alias = name_node.child(0)

            name = name_node.child(0)
            if not name or not alias or not alias.text or not name.text:
                raise ValueError("Invalid alias import")

            res.append(Import(name.text.decode(), alias.text.decode()))

    elif node.type == "import_from_statement":
        importer_module = node.child_by_field_name("module_name")
        if not importer_module or not importer_module.text:
            raise ValueError("Invalid importer module")

        if (
            node.named_child_count > 0
            and node.named_children[-1].type == "wildcard_import"
        ):
            res.append(
                Import(module_name=importer_module.text.decode() + ".*", alias="")
            )

        modules = node.children_by_field_name("name")
        for name_node in modules:
            if name_node.type == "aliased_import":
                name = name_node.child_by_field_name("name")
                alias = name_node.child_by_field_name("alias")
            else:
                name = name_node
                alias = name_node.child(0)

            name = name_node.child(0)
            if not name or not alias or not alias.text or not name.text:
                raise ValueError("Invalid alias import")

            res.append(
                Import(
                    importer_module.text.decode() + "." + name.text.decode(),
                    alias.text.decode(),
                )
            )
    else:
        raise NotImplementedError(node)

    return res


def init_metadata(
    root: Node | None, file_path="", module_path="", language=""
) -> ChunkMetaData:
    res = ChunkMetaData()
    res.chunk_id = str(uuid4())
    res.chunk_type = "module"
    res.name = "module"
    res.qualified_name = "module"
    res.parent_name = None
    res.parent_type = None
    res.file_path = file_path
    res.file_name = os.path.basename(file_path)
    res.module_path = module_path
    res.language = language
    res.start_line = root.start_point.row if root else 0
    res.end_line = root.end_point.row if root else 0
    res.source_code = root.text.decode() if root and root.text else ""

    res.parameters = []
    res.return_type = None
    res.decorators = []
    res.is_async = False
    res.base_classes = []
    res.imports = []
    res.contained_in = None

    return res


def chunk_python_file(
    file_path: str,
    module_path: str,
    language: str = "Python",
    file_stream: IO[str] | None = None,
):
    def read_callable_point(byte_offset, point):
        row, column = point
        if row >= len(src_lines) or column >= len(src_lines[row]):
            return None
        return src_lines[row][column:].encode("utf8")

    with open(file_path) as f:
        src_lines = f.readlines()
        tree = parser.parse(read_callable_point, encoding="utf8")
        root = tree.root_node

    q: deque[tuple[Node, ChunkMetaData]] = deque([])
    parent_metadata = init_metadata(root, file_path, module_path, language)
    q.append((root, parent_metadata))
    chunks: list[ChunkMetaData] = []

    while q:
        curr, parent_metadata = q.popleft()
        i = 0

        while i < len(curr.named_children):
            child = curr.named_children[i]
            chunk = None
            if child.type == SEMANTIC_CHUNKS["FUNCTION"]:
                chunk = extract_function(child, [], parent_metadata)
                q.append((child, chunk))
            elif child.type == SEMANTIC_CHUNKS["CLASS"]:
                chunk = extract_class(child, [], parent_metadata)
                q.append((child, chunk))
            elif child.type == SEMANTIC_CHUNKS["DECORATOR"]:
                chunk = extract_decorator(child, parent_metadata)
                if chunk:
                    function_children = [
                        (item, chunk)
                        for item in child.named_children[-1].named_children
                    ]
                    q.extend((function_children))
            elif (
                parent_metadata.chunk_type == "module"
                and child.type not in SEMANTIC_CHUNKS.values()
            ):  # if it's file level code
                chunk = init_metadata(None, file_path, module_path, language)
                chunk.start_line = child.start_point.row

                while (
                    i < len(curr.named_children)
                    and curr.named_children[i].type not in SEMANTIC_CHUNKS.values()
                ):
                    child = curr.named_children[i]
                    chunk.end_line = child.end_point.row
                    if child.text:
                        chunk.source_code += child.text.decode() + "\n"

                    if child.type in ["import_from_statement", "import_statement"]:
                        chunk.imports.extend(get_imports(child))
                    i += 1

                i -= 1  # for adjusting +1 later in the code
            elif child.type in [
                "import_from_statement",
                "import_statement",
            ]:  # Import statements that are not module level
                parent_metadata.imports.extend(get_imports(child))
            else:
                q.append((child, parent_metadata))

            if chunk:
                chunks.append(chunk)
            i += 1

    if not chunks:
        chunks.append(parent_metadata)

    for chunk in chunks:
        pprint(chunk, file_stream)

    return chunks


def preprocess_python_file(file: Path, dir_path: Path, file_stream: IO[str] | None):
    module_parts = list(Path(os.path.relpath(file, dir_path)).parts)
    module_parts[-1] = module_parts[-1].split(".")[0]

    if module_parts[-1] == "__init__":
        module_parts.pop()

    module_path = ".".join(module_parts)
    return chunk_python_file(str(file), module_path, "Python", file_stream)


def chunk_files(dir_path: Path, file_stream: IO[str] | None):
    files = walk_directory(dir_path)

    for file in files:
        if file.suffix.lower() == ".py":
            preprocess_python_file(file, dir_path, file_stream)


def walk_directory(dir_path: Path):
    for root, dirs, files in os.walk(dir_path):
        # If a subfolder contains 'pyvenv.cfg', remove it so os.walk skips it
        for d in list(dirs):
            if os.path.exists(os.path.join(root, d, "pyvenv.cfg")):
                dirs.remove(d)

        for file in files:
            yield Path(os.path.join(root, file))


curr_dir = Path.cwd()
with open("output.txt", "w") as f:
    chunk_files(curr_dir, f)
