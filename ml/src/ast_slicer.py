import tree_sitter
import tree_sitter_c
import tree_sitter_cpp

# Modern tree-sitter API (v0.22+)
C_LANG = tree_sitter.Language(tree_sitter_c.language())
CPP_LANG = tree_sitter.Language(tree_sitter_cpp.language())

def extract_function_name(node, code_bytes):
    """Recursively search for the function identifier."""
    if node.type == "identifier":
        return code_bytes[node.start_byte:node.end_byte].decode('utf8', 'ignore')
    for child in node.children:
        name = extract_function_name(child, code_bytes)
        if name:
            return name
    return None

def get_functions(code: str, language: str = "c"):
    """Parse source code and return a list of function dictionaries."""
    parser = tree_sitter.Parser(CPP_LANG if language == "cpp" else C_LANG)
    code_bytes = bytes(code, "utf8")
    tree = parser.parse(code_bytes)
    
    functions = []
    
    def traverse(node):
        if node.type == "function_definition":
            # Find the declarator to extract the name
            decl = next((c for c in node.children if "declarator" in c.type), None)
            name = extract_function_name(decl, code_bytes) if decl else "unknown_func"
            
            functions.append({
                "name": name,
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
                "code": code_bytes[node.start_byte:node.end_byte].decode('utf8', 'ignore')
            })
        else:
            for child in node.children:
                traverse(child)
                
    traverse(tree.root_node)
    
    # Fallback if no functions parse successfully
    if not functions:
        functions = [{
            "name": "snippet",
            "start_line": 1,
            "end_line": len(code.splitlines()) or 1,
            "code": code
        }]
        
    return functions