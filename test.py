import tree_sitter_python as tspython
from tree_sitter import Language, Node, Parser

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)


def read_callable_point(byte_offset, point):
    row, column = point
    if row >= len(src_lines) or column >= len(src_lines[row]):
        return None
    return src_lines[row][column:].encode("utf8")


with open("data/test-files/test.py") as f:
    src_lines = f.readlines()
    tree = parser.parse(read_callable_point, encoding="utf8")
    root = tree.root_node.child(0).child(0)
    print(root)
    # print("".join([it.text.decode() for it in root.child(0).child(0).named_children]))