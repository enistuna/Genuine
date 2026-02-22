import pytest
from unittest.mock import MagicMock, patch
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'actions')))

from actions.custom_ner import TurkishFinancialNER

@patch('custom_ner.AutoTokenizer')
@patch('custom_ner.AutoModelForTokenClassification')
def test_extract_entities_logic(mock_model_cls, mock_tokenizer_cls):

    mock_tokenizer = MagicMock()
    mock_model = MagicMock()
    
    mock_tokenizer_cls.from_pretrained.return_value = mock_tokenizer
    mock_model_cls.from_pretrained.return_value = mock_model
    
    mock_tokenizer.return_value = {"input_ids": [0]}
    mock_tokenizer.convert_ids_to_tokens.return_value = ["500", "TL"]
    
    ner = TurkishFinancialNER()
    assert ner.label_map == {0: "O", 1: "B-PARA", 2: "I-PARA"}
    assert hasattr(ner, 'extract_entities')

@pytest.mark.skip(reason="Requires downloading heavy models")
def test_real_extraction():
    ner = TurkishFinancialNER()
    result = ner.extract_entities("Hesabıma 100 TL yatır.")
    
    assert isinstance(result, list)
