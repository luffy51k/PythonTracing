import os
from dotenv import load_dotenv

load_dotenv()

OTLP_ENDPOINT = os.getenv('OTLP_ENDPOINT')
OTLP_ENDPOINT_USER = os.getenv('OTLP_ENDPOINT_USER')
OTLP_ENDPOINT_PASSWORD = os.getenv('OTLP_ENDPOINT_PASSWORD')
