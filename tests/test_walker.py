import tempfile
import shutil
from pathlib import Path

from aurelia.ingestion.walker import RepoWalker
from aurelia.core.model import FileClassification

def setup_test_repo(base_dir: Path):
    """Creates a mock repository structure to test the walker."""
    # 1. Create a .gitignore
    with open(base_dir / ".gitignore", "w") as f:
        f.write("ignored_folder/\n")
        f.write("secret.key\n")
        f.write("*.log\n")

    # 2. Add files that should be PARSED
    (base_dir / "main.py").touch()
    (base_dir / "utils.py").touch()

    # 3. Add files that should be MARKDOWN
    (base_dir / "README.md").touch()
    
    # 4. Add files that should be CONFIG
    (base_dir / "pyproject.toml").touch()
    (base_dir / "config.yaml").touch()

    # 5. Add files that should be SKIPPED (By Extension)
    (base_dir / "image.png").touch()
    (base_dir / "data.csv").touch()
    
    # 6. Add files that should be SKIPPED (Lock files)
    (base_dir / "poetry.lock").touch()

    # 7. Add files that should be IGNORED (By .gitignore)
    ignored_dir = base_dir / "ignored_folder"
    ignored_dir.mkdir()
    (ignored_dir / "should_not_see_this.py").touch()
    
    (base_dir / "secret.key").touch()
    (base_dir / "debug.log").touch()
    
    # 8. Add files that should be IGNORED (Hardcoded ALWAYS_IGNORE)
    git_dir = base_dir / ".git"
    git_dir.mkdir()
    (git_dir / "config").touch()
    
    pycache_dir = base_dir / "__pycache__"
    pycache_dir.mkdir()
    (pycache_dir / "main.cpython-310.pyc").touch()


def test_repo_walker():
    print("Starting RepoWalker Verification...")
    
    # Create a temporary directory that cleans itself up
    test_dir = tempfile.mkdtemp(prefix="aurelia_test_repo_")
    test_path = Path(test_dir)
    
    try:
        setup_test_repo(test_path)
        print(f"Set up test repository at: {test_path}")
        
        walker = RepoWalker(str(test_path))
        files = walker.walk()
        
        print(f"\nWalker found {len(files)} valid files:")
        print("-" * 40)
        
        expected_counts = {
            FileClassification.PARSE: 2,      # main.py, utils.py
            FileClassification.MARKDOWN: 1,   # README.md
            FileClassification.CONFIG: 2,     # pyproject.toml, config.yaml
            FileClassification.SKIP: 3        # image.png, data.csv, poetry.lock
        }
        
        actual_counts = {
            FileClassification.PARSE: 0,
            FileClassification.MARKDOWN: 0,
            FileClassification.CONFIG: 0,
            FileClassification.SKIP: 0
        }
        
        for f in files:
            print(f"[{f.classification.value.upper()}] {f.relative_path}")
            actual_counts[f.classification] += 1
            
            # Double check nothing ignored slipped through
            if "ignored_folder" in f.relative_path or f.relative_path.endswith(".log") or f.relative_path == "secret.key":
                print(f"ERROR: Walker failed to respect .gitignore for {f.relative_path}")
            if ".git" in f.relative_path or "__pycache__" in f.relative_path:
                print(f"ERROR: Walker failed to respect hardcoded ignore rules for {f.relative_path}")
        
        print("\nVerification Summary:")
        print("-" * 40)
        all_passed = True
        for classification, expected in expected_counts.items():
            actual = actual_counts[classification]
            status = "PASS" if actual == expected else "FAIL"
            if actual != expected:
                all_passed = False
            print(f"{status} {classification.name}: Expected {expected}, Found {actual}")
            
        if all_passed:
            print("\nSUCCESS: RepoWalker is working correctly!")
        else:
            print("\nWARNING: Some classifications did not match expectations.")

    finally:
        # Clean up the exact temporary directory tree
        shutil.rmtree(test_dir, ignore_errors=True)
        print(f"\nCleaned up test repository at: {test_path}")

if __name__ == "__main__":
    test_repo_walker()