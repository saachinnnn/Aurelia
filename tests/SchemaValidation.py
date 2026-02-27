from src.core.model import AureliaConfig

try:
    config = AureliaConfig()
    print("Successfully initialized AureliaConfig!")
    print(config.model_dump_json(indent=2))
except Exception as e:
    print(f"Error: {e}")
