from typing import List, Dict, Any, Tuple
import tree_sitter
import tree_sitter_python
from aurelia.core.model import ChunkType

class AureliaParser:
    """
    Parses Python source code into its Abstract Syntax Tree (AST) using Tree-Sitter.
    Extracts top-level structures (Classes, Functions) and groups the rest into a Module chunk.
    """
    
    def __init__(self):
        # Initialize the tree-sitter language and parser
        # tree_sitter_python.language() returns the compiled grammar for Python
        self.language = tree_sitter.Language(tree_sitter_python.language())
        self.parser = tree_sitter.Parser(self.language)

    def parse(self, code: str) -> tree_sitter.Tree:
        """
        Parses raw python source code into an AST.
        """
        # Tree-sitter requires bytes, not strings
        ## Recursive function that creates a AST(Tree like structure)
        return self.parser.parse(bytes(code, "utf-8"))

    def _get_source_lines(self, code_lines: List[str], start_point: Tuple[int, int], end_point: Tuple[int, int]) -> str:
        """Helper to extract the exact source text for a node."""
        # Tree-sitter points are (row, column). rows are 0-indexed.
        start_row, start_col = start_point
        end_row, end_col = end_point
        
        if start_row == end_row:
            return code_lines[start_row][start_col:end_col]
            
        # Extract the lines spanning the node
        lines = []
        lines.append(code_lines[start_row][start_col:])
        for i in range(start_row + 1, end_row):
             lines.append(code_lines[i])
        lines.append(code_lines[end_row][:end_col])
        
        return "\n".join(lines)

    def extract_chunks(self, source_code: str) -> List[Dict[str, Any]]:
        """
        Walks the root of the AST and extracts:
        - function_definition -> ChunkType.FUNCTION
        - class_definition    -> ChunkType.CLASS
        - everything else     -> Grouped into ChunkType.MODULE (orphan code)
        """
        tree = self.parse(source_code)
        root_node = tree.root_node
        
        # We need the source broken into lines for easy extraction
        code_lines = source_code.splitlines()
        
        chunks = []
        module_lines = []
        
        # We only iterate over the direct children of the root note (Top-Level)
        for child in root_node.children:
            
            # Extract the raw text for this specific node
            node_text = self._get_source_lines(
                code_lines, 
                child.start_point, 
                child.end_point
            )
            
            # Lines are 0-indexed in tree-sitter, so we add 1 for humans
            start_line = child.start_point[0] + 1
            end_line = child.end_point[0] + 1
            
            # Resolve decorated definitions to their inner function/class definition
            actual_node = child
            if actual_node.type == "decorated_definition":
                for sub_node in actual_node.children:
                    if sub_node.type in ("function_definition", "class_definition"):
                        actual_node = sub_node
                        break
            
            if actual_node.type == "function_definition":
                # Get the name of the function.
                name_node = actual_node.child_by_field_name('name')
                func_name = self._get_source_lines(code_lines, name_node.start_point, name_node.end_point) if name_node else "unknown_function"
                
                chunks.append({
                    "type": ChunkType.FUNCTION,
                    "name": func_name,
                    "content": node_text,
                    "start_line": start_line,
                    "end_line": end_line
                })
                
            elif actual_node.type == "class_definition":
                name_node = actual_node.child_by_field_name('name')
                class_name = self._get_source_lines(code_lines, name_node.start_point, name_node.end_point) if name_node else "unknown_class"
                
                chunks.append({
                    "type": ChunkType.CLASS,
                    "name": class_name,
                    "content": node_text,
                    "start_line": start_line,
                    "end_line": end_line
                })
                
            else:
                # Imports, globals, standalone expressions.
                module_lines.append({
                    "type": ChunkType.MODULE,
                    "content": node_text,
                    "start_line": start_line,
                    "end_line": end_line
                })
                
        # If we collected any module-level orphaned code, create a chunk for it
        if module_lines:
            combined_content = "\n".join([line["content"] for line in module_lines])
            chunks.insert(0, {
                 "type": ChunkType.MODULE,
                 "name": "module_level",
                 "content": combined_content,
                 "start_line": module_lines[0]["start_line"],
                 "end_line": module_lines[-1]["end_line"]
            })
            
        return chunks
