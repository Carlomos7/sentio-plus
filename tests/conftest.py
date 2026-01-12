import pandas as pd
import pytest


@pytest.fixture
def sample_apps_info_df():
    return pd.DataFrame({
        "app_id": ["a1"],
        "app_name": ["Test App"],
        "score": [4.5],              
        "ratings_count": [100],
        "downloads": [1000],
        "content_rating": ["Everyone"],
        "section": ["Tools"],
        "categories": ["Utility"]
    })


@pytest.fixture
def sample_apps_reviews_df():
    return pd.DataFrame({
        "app_id": ["a1"] * 5,
        "review_text": ["ok"] * 5,
        "review_score": [5] * 5,
        "review_date": ["2024-01-01"] * 5,
        "helpful_count": [0] * 5
    })
