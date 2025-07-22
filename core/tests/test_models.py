#from django.test import TestCase
from core.models import Competition
from datetime import date

def test_competition_str_representation(sample_competition):
    assert str(sample_competition) == "Best Colleague 2024"

def test_competition_dates(sample_competition):
    assert sample_competition.start_date == date(2024, 1, 1)
    assert sample_competition.end_date == date(2024, 12, 31)
