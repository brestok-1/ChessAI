import os
import pathlib
import pickle
from functools import lru_cache

import torch
from dotenv import load_dotenv

from app.core.model import ChessModel

load_dotenv()


class BaseConfig:
    BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent.parent
    MODELS_DIR: pathlib.Path = BASE_DIR / 'app' / 'ai' / 'models'

    def __init__(self):
        with open(self.MODELS_DIR / 'move_to_int', "rb") as file:
            move_to_int = pickle.load(file)

        device = torch.device("cpu")
        model = ChessModel(num_classes=len(move_to_int))
        model.load_state_dict(torch.load(self.MODELS_DIR / "TORCH_100EPOCHS.pth", map_location="cpu"))
        model.to(device)
        model.eval()
        move_to_int = {v: k for k, v in move_to_int.items()}
        self.MODEL = model
        self.MOVE_TO_INT = move_to_int
        self.DEVICE = device

class DevelopmentConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    pass


@lru_cache()
def get_settings() -> DevelopmentConfig | ProductionConfig:
    config_cls_dict = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
    }
    config_name = os.getenv('FASTAPI_CONFIG', default='development')
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings = get_settings()
