from pathlib import Path

PROJECT_PATH = Path(__file__).resolve().parents[2]

SOURCEFILE_PATH =PROJECT_PATH/'src'

CURRENCY_CONFIG_PATH =SOURCEFILE_PATH/'config'/'currency.yaml'
SCENARIO_CONFIG_PATH =SOURCEFILE_PATH/'config'/'scenarios.yaml'

DATA_PATH = PROJECT_PATH/'data'
