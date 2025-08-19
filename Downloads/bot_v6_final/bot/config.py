from pathlib import Path
class Settings:
    TARGET_HORIZON = 3
    PROBA_THRESHOLD = 0.62
    PROBA_SMOOTH_ALPHA = 0.3
    ADX_FILTER = 18.0
    VOL_Q_LOW = 0.15
    VOL_Q_HIGH = 0.98
    MODEL_PATH = Path(__file__).resolve().parent / "models"
    LOG_PATH = Path(__file__).resolve().parent / "logs"
settings = Settings()
