from validators import validate_tckn

def test_validate_tckn_valid():
    assert validate_tckn("10000000146") is True

def test_validate_tckn_invalid_length():
    assert validate_tckn("123") is False
    assert validate_tckn("123456789012") is False

def test_validate_tckn_starts_with_zero():
    assert validate_tckn("01234567890") is False

def test_validate_tckn_invalid_checksum():
    assert validate_tckn("10000000145") is False
