import os
import pathspec
from pathlib import Path
from typing import List, Optional

from aurelia.core.model import FileInfo, FileClassification

class RepoWalker:
    """
    Walks a repository directory tree, respects .gitignore patterns via pathspec, 
    and classifies files for downstream processing.
    """
    
    # The below three are sets of hardcoded ignore patterns.These will never be traversed by the walker even though if they are not present in the .gitignore
    ALWAYS_IGNORE_DIRS = {
        ".git", "__pycache__", "node_modules", ".venv", "venv", "env", "build", "dist", ".idea", ".vscode"
    }
    
    BINARY_EXTENSIONS = {
        ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".exe", ".dll", ".so", 
        ".dylib", ".zip", ".tar", ".gz", ".pyc", ".pyo", ".pyd", ".mp3", ".mp4", ".wmv"
    }
    
    LOCK_FILES = {
        "package-lock.json", "yarn.lock", "poetry.lock", "Pipfile.lock", "Cargo.lock"
    }

    def __init__(self, repo_path: str):
        self.repo_root = Path(repo_path).resolve() # Make sure the path is absolute.
        if not self.repo_root.is_dir(): # If the path is not a directory, raise an error.
            raise ValueError(f"Provided path is not a valid directory: {self.repo_root}")
        
        self.ignore_spec = self._load_gitignore() # Load the .gitignore file in the given folder and its contents that match are stored here.

    def _load_gitignore(self) -> Optional[pathspec.PathSpec]:
        """Loads the root .gitignore file into a pathspec matcher."""
        gitignore_path = self.repo_root / ".gitignore" #.gitignore of the folder given by the user
        if gitignore_path.exists() and gitignore_path.is_file():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    return pathspec.PathSpec.from_lines('gitwildmatch', f) # I didnt understand this
            except Exception as e:
                print(f"Warning: Failed to read .gitignore at {gitignore_path}: {e}") # But why are we terminating the entire process just because we cant read the .gitignore file?
        return None

    def _get_classification(self, file_path: Path) -> FileClassification:
        """Determines how a file should be processed based on its extension or name."""
        ext = file_path.suffix.lower()
        name = file_path.name.lower()
        
        # Hard limits on skipping
        if ext in self.BINARY_EXTENSIONS or name in self.LOCK_FILES:
            return FileClassification.SKIP
            
        # Classify based on type
        if ext == ".py": # For now this is restricted to python
            return FileClassification.PARSE
        elif ext == ".md":
            return FileClassification.MARKDOWN
        elif ext in {".yaml", ".yml", ".toml", ".json", ".cfg", ".ini"}:
            return FileClassification.CONFIG
            
        # Default fallback
        return FileClassification.SKIP # If it meets none of the conditions above mentioned then.

    def _is_explicitly_ignored(self, path: Path) -> bool:
        """Check hardcoded ignore patterns."""
        # Check directories in the path
        for part in path.parts:
            if part in self.ALWAYS_IGNORE_DIRS:
                return True
        
        # Also ignore the .gitignore and .git files themselves
        ## This may not be the final fix but it works for now.
        if path.name == ".gitignore" or path.name == ".git":
            return True
            
        return False
    # Main function
    def walk(self) -> List[FileInfo]:
        """
        Recursively walks the repository, avoiding ignored paths and yielding classified FileInfo.
        """
        results = []
        # Recursively calls itself
        for root, dirs, files in os.walk(self.repo_root, followlinks=False):
            root_path = Path(root)
            
            # Prune directories starting with '.' (except current dir '.') or in ALWAYS_IGNORE
            # Modifying `dirs` in-place tells os.walk to skip those directories entirely!
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in self.ALWAYS_IGNORE_DIRS]
            
            for file_name in files:
                file_path = root_path / file_name
                
                # Double check hardcoded ignores just in case
                if self._is_explicitly_ignored(file_path):
                    continue

                # Calculate relative path string for pathspec and output
                try:
                    rel_path_str = str(file_path.relative_to(self.repo_root)).replace('\\', '/')
                except ValueError:
                    continue # Somehow escaped repo root, skip
                    
                # Check pathspec (.gitignore)
                if self.ignore_spec and self.ignore_spec.match_file(rel_path_str):
                    continue
                    
                # Classify and append
                try:
                    classification = self._get_classification(file_path)
                    results.append(FileInfo(
                        absolute_path=str(file_path.absolute()),
                        relative_path=rel_path_str,
                        classification=classification
                    ))
                except Exception as e:
                    # Catch permission errors or other FS issues gracefully
                    print(f"Warning: Could not process file {file_path}: {e}")

        return results
