import boto3
import pytest
from translator.translator import translate_text

client = boto3.client("translate")


@pytest.fixture
def text():
    return "Hello, world!"


def test_translate(text):
    assert translate_text(text, "zh") == "你好，世界！"


def test_translate_error(text):
    with pytest.raises(client.exceptions.UnsupportedLanguagePairException):
        translate_text(text, "??")
