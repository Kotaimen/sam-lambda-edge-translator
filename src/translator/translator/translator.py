import logging

import boto3
from smart_open import open

translate = boto3.client("translate")
s3 = boto3.client("s3")


def translate_text(text: str, target_lang: str, source_lang: str = "auto") -> str:
    """Translate given text to target language and return translated text."""
    response = translate.translate_text(
        Text=text, SourceLanguageCode=source_lang, TargetLanguageCode=target_lang
    )
    return response["TranslatedText"]


def tranlate_s3(bucket: str, key: str, target_lang: str, target_key: str) -> str:
    logging.info(f"Opening s3://{bucket}/{key} for read.")
    with open(f"s3://{bucket}/{key}", "r") as ifp:
        logging.info(f"Translating s3://{bucket}/{key} to {target_lang}")
        translated_text = translate_text(ifp.read(), target_lang=target_lang)
        logging.info(f"Writing s3://{bucket}/{target_key}")
        with open(f"s3://{bucket}/{target_key}", "w") as ofp:
            ofp.write(translated_text)
    return translated_text
