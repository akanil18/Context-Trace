import tree_sitter, tree_sitter_python
lang = tree_sitter.Language(tree_sitter_python.language())
parser = tree_sitter.Parser(lang)
src = b'from .utils import generate_token'
tree = parser.parse(src)
print(tree.root_node)
for c in tree.root_node.children[0].named_children:
    print(c.type, src[c.start_byte:c.end_byte])
