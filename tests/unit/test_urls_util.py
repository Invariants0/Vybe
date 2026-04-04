import pytest
from datetime import datetime, timezone, timedelta
from backend.app.utils.urls import normalize_url, parse_expiration
from backend.app.config import ValidationError


class TestNormalizeUrl:
    
    def test_valid_http_url(self):
        result = normalize_url("http://example.com")
        assert result == "http://example.com"
    
    def test_valid_https_url(self):
        result = normalize_url("https://example.com/path")
        assert result == "https://example.com/path"
    
    def test_url_with_query_params(self):
        result = normalize_url("https://example.com/search?q=test")
        assert result == "https://example.com/search?q=test"
    
    def test_empty_url(self):
        with pytest.raises(ValidationError, match="url is required"):
            normalize_url("")
    
    def test_whitespace_only_url(self):
        with pytest.raises(ValidationError, match="url is required"):
            normalize_url("   ")
    
    def test_non_string_url(self):
        with pytest.raises(ValidationError, match="url is required"):
            normalize_url(None)
    
    def test_url_too_long(self):
        long_url = "https://example.com/" + "a" * 3000
        with pytest.raises(ValidationError, match="url must be at most"):
            normalize_url(long_url)
    
    def test_url_without_scheme(self):
        with pytest.raises(ValidationError, match="url must start with http"):
            normalize_url("ftp://example.com")
    
    def test_url_without_hostname(self):
        with pytest.raises(ValidationError, match="url must include a valid hostname"):
            normalize_url("https://")
    
    def test_url_with_whitespace_trimmed(self):
        result = normalize_url("  https://example.com  ")
        assert result == "https://example.com"


class TestParseExpiration:
    
    def test_none_expiration(self):
        result = parse_expiration(None)
        assert result is None
    
    def test_empty_string_expiration(self):
        result = parse_expiration("")
        assert result is None
    
    def test_valid_iso_datetime(self):
        future_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        result = parse_expiration(future_time)
        assert result is not None
        assert result.tzinfo is not None
    
    def test_datetime_with_z_suffix(self):
        future_time = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        result = parse_expiration(future_time)
        assert result is not None
    
    def test_invalid_datetime_format(self):
        with pytest.raises(ValidationError, match="expires_at must be a valid ISO 8601 datetime"):
            parse_expiration("not-a-date")
    
    def test_past_datetime(self):
        past_time = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        with pytest.raises(ValidationError, match="expires_at must be in the future"):
            parse_expiration(past_time)
    
    def test_naive_datetime_gets_utc(self):
        future_time = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
        result = parse_expiration(future_time)
        assert result is not None
        assert result.tzinfo is not None
