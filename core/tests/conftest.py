import pytest
from datetime import date
from core.models import Competition, Vote

@pytest.fixture
def sample_competition(db):
    return Competition.objects.create(
        name="Best Colleague 2024",
        start_date=date(2024,1,1),
        end_date=date(2024,12,31)
    )

@pytest.fixture
def sample_vote(db, sample_competition):
    return Vote.objects.create(
        competition=sample_competition,
        title="Most Helpful",
        description="Vote for the most helpful colleague",
        is_public=True
    )
