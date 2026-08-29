import tree_sitter, tree_sitter_python as tspython
language = tree_sitter.Language(tspython.language())
parser = tree_sitter.Parser(language)
tree = parser.parse(b'def foo(): pass')
q = tree_sitter.Query(language, '(function_definition name: (identifier) @n) @f')
cursor = tree_sitter.QueryCursor(q)
matches = cursor.matches(tree.root_node)
print(matches)
