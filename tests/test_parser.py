import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.ingestion.parser import AureliaParser
from src.core.model import ChunkType

def test_python_parsing():
    print("Starting Tree-Sitter Parser Verification...")
    
    # 1. Provide a mock python file as a raw string
    sample_code = """import os
from typing import List

GLOBAL_VAR = True

def standalone_function(x: int) -> int:
    return x * 2

class MockClass:
    \"\"\"This is a test class.\"\"\"
    
    def __init__(self):
        self.value = 42
        
    def do_something(self):
        print("Doing something!")
"""

    parser = AureliaParser()
    
    try:
        chunks = parser.extract_chunks(sample_code)
        
        print(f"\nParser extracted {len(chunks)} top-level chunks:")
        print("-" * 40)
        
        expected_counts = {
            ChunkType.MODULE: 1,
            ChunkType.FUNCTION: 1,
            ChunkType.CLASS: 1
        }
        
        actual_counts = {
            ChunkType.MODULE: 0,
            ChunkType.FUNCTION: 0,
            ChunkType.CLASS: 0
        }
        
        for i, chunk in enumerate(chunks):
            c_type = chunk["type"]
            c_name = chunk["name"]
            lines = f"lines {chunk['start_line']}-{chunk['end_line']}"
            
            print(f"├── [{c_type.value}] {c_name} {lines}")
            
            # Simple format check to see if content was actually grabbed
            if len(chunk["content"]) < 5:
                print(f"  ERROR: Chunk content seems missing or too short!")
            
            if c_type in actual_counts:
                actual_counts[c_type] += 1
                
        print("\nVerification Summary:")
        print("-" * 40)
        all_passed = True
        for chunk_type, expected_count in expected_counts.items():
            actual_count = actual_counts[chunk_type]
            status = "PASS" if actual_count == expected_count else "FAIL"
            if actual_count != expected_count:
                 all_passed = False
            print(f"{status} {chunk_type.name}: Expected {expected_count}, Found {actual_count}")
            
        if all_passed:
            print("\nSUCCESS: Tree-Sitter Parser is working correctly!")
        else:
             print("\nWARNING: Some chunks were not extracted as expected.")
             
    except Exception as e:
         print(f"FATAL ERROR during extraction: {e}")

if __name__ == "__main__":
    test_python_parsing()
