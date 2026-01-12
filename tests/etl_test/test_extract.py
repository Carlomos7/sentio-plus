def test_create_apps_and_reviews_respects_limit(
    monkeypatch,
    sample_apps_info_df,
    sample_apps_reviews_df
):
    import pandas as pd
    from etl.extract import create_apps_and_reviews

    def fake_read_csv(path, *args, **kwargs):
        if "apps_info" in str(path):
            return sample_apps_info_df
        return sample_apps_reviews_df

    # Mock the CSV reads
    monkeypatch.setattr(pd, "read_csv", fake_read_csv)

    # Mock the CSV write pulls to here (prevent filesystem error)
    monkeypatch.setattr(pd.DataFrame, "to_csv", lambda *args, **kwargs: None)

    df = create_apps_and_reviews(limit=3)

    assert len(df) == 3
