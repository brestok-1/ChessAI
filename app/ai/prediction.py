import numpy as np
import torch

from app.ai.utils import board_to_matrix
from app.core.config import settings

def prepare_input(chess):
    matrix = board_to_matrix(chess)
    X_tensor = torch.tensor(matrix, dtype=torch.float32).unsqueeze(0)
    return X_tensor


def predict_move(chess):
    X_tensor = prepare_input(chess).to(settings.DEVICE)
    with torch.no_grad():
        logits = settings.MODEL(X_tensor)
    logits = logits.squeeze(0)  # Remove batch dimension
    probabilities = torch.softmax(logits, dim=0).cpu().numpy()  # Convert to probabilities

    legal_moves = chess.get_legal_moves()
    legal_moves_uci = chess.utils.convert_moves_to_uci(legal_moves)

    sorted_indices = np.argsort(probabilities)[::-1]
    for move_index in sorted_indices:
        move = settings.MOVE_TO_INT[move_index]
        if move in legal_moves_uci:
            return move
    return None
