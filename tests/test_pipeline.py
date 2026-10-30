"""Tests for the shared orchestration code (team lead)."""

import pytest
import requests

import pipeline
from etl import common


def test_required_size_constants():
    assert common.MIN_ROWS >= 10000
    assert common.MIN_COLS >= 18


def test_validate_raw_data_rejects_missing_columns(raw_sample):
    with pytest.raises(ValueError, match="missing expected columns"):
        pipeline.validate_raw_data(raw_sample.drop(columns=["adr"]))


def test_validate_raw_data_rejects_too_few_rows(raw_sample):
    with pytest.raises(ValueError, match="at least"):
        pipeline.validate_raw_data(raw_sample)      # only ~24 rows


def test_extract_uses_local_copy_when_download_fails(raw_sample, tmp_path, monkeypatch):
    raw_file = tmp_path / "hotel_bookings_raw.csv"
    raw_sample.to_csv(raw_file, index=False)

    def broken_get(*args, **kwargs):
        raise requests.ConnectionError("no internet")

    monkeypatch.setattr(pipeline.requests, "get", broken_get)
    monkeypatch.setattr(pipeline, "RAW_FILE", str(raw_file))
    monkeypatch.setattr(pipeline, "RAW_DIR", str(tmp_path))
    monkeypatch.setattr(pipeline, "MIN_ROWS", 1)
    monkeypatch.setattr(pipeline, "MIN_COLS", 1)
    df = pipeline.extract()
    assert len(df) == len(raw_sample)


def test_extract_fails_clearly_without_any_data(tmp_path, monkeypatch):
    def broken_get(*args, **kwargs):
        raise requests.ConnectionError("no internet")

    monkeypatch.setattr(pipeline.requests, "get", broken_get)
    monkeypatch.setattr(pipeline, "RAW_FILE", str(tmp_path / "missing.csv"))
    monkeypatch.setattr(pipeline, "RAW_DIR", str(tmp_path))
    with pytest.raises(RuntimeError, match="Could not download"):
        pipeline.extract()
