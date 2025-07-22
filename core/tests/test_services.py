from core.models import Competition
from core.services import get_winner

def test_get_winner(sample_competition):
    winner = get_winner(sample_competition.id)
    assert winner == "No winners yet"