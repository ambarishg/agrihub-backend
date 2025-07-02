from dotenv import load_dotenv
from config.extractor_configs import ExtractorConfigs

status: bool = load_dotenv(".env", override=True)
print(status)
CONFIGS = ExtractorConfigs()