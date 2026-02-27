from aurelia.core.model import AureliaConfig
from aurelia.core.config import save_config, load_config, CONFIG_PATH

def test_config_roundtrip():
    print("Starting Configuration Roundtrip Verification...")
    
    # 1. Initialize with default values
    original_config = AureliaConfig(project_name="Verification-Test")
    print(f"Initialized config with project_name: {original_config.project_name}")
    
    # 2. Save to home directory (~/.aurelia/config.yaml)
    try:
        save_config(original_config)
        print(f"Saved config to {CONFIG_PATH}")
    except Exception as e:
        print(f"Save failed: {e}")
        return

    # 3. Load back from disk
    try:
        loaded_config = load_config()
        print("Loaded config back from disk")
    except Exception as e:
        print(f"Load failed: {e}")
        return

    # 4. Compare results
    if loaded_config.project_name == original_config.project_name:
        print("SUCCESS: Roundtrip verification passed! Data is consistent.")
        print("-" * 30)
        print(f"Final Project Name: {loaded_config.project_name}")
        print(f"LLM Provider: {loaded_config.llm.provider}")
    else:
        print("FAILURE: Loaded data does not match original data!")
        print(f"Original: {original_config.project_name}")
        print(f"Loaded: {loaded_config.project_name}")

if __name__ == "__main__":
    test_config_roundtrip()

# What essentially the test_config_roundtrip does:
'''
1) It initializes the AureliaConfig class with a project name.
2) Saves that config to the yaml file.
3) Loads that config back from the yaml file to an instance.
4) Compares the loaded config with the original config.
5) If they are the same then its a success else its a failure. Ta da! Done!
'''