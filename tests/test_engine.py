
import pytest
from src.pyautoforge.engine.core import AutomationEngine

def test_engine_creation():
    engine = AutomationEngine()
    assert engine is not None
