import pytest
from scanner.models import Candle
from scanner.indicators import calculate_sma, calculate_ema, calculate_avwap

def test_calculate_sma(flat_candles):
    # flat_candles has 60 candles around 100.0
    sma = calculate_sma(flat_candles, 10)
    assert sma is not None
    assert 98.0 <= sma <= 102.0

def test_calculate_sma_insufficient_data(flat_candles):
    assert calculate_sma(flat_candles[:5], 10) is None

def test_calculate_ema(flat_candles):
    ema = calculate_ema(flat_candles, 10)
    assert ema is not None
    assert 98.0 <= ema <= 102.0

def test_calculate_ema_insufficient_data(flat_candles):
    assert calculate_ema(flat_candles[:5], 10) is None

def test_calculate_avwap(flat_candles):
    avwap = calculate_avwap(flat_candles, 10)
    assert avwap is not None
    assert 98.0 <= avwap <= 102.0

def test_calculate_avwap_invalid_index(flat_candles):
    assert calculate_avwap(flat_candles, -1) is None
    assert calculate_avwap(flat_candles, 100) is None
