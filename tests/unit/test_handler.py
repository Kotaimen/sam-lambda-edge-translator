import json
import logging
import os

import pytest

logging.getLogger().setLevel(logging.DEBUG)
os.environ["AWS_SAM_LOCAL"] = "yes"

from translator.handler import handler


@pytest.fixture()
def origin_response():
    event_file = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            os.pardir,
            "events",
            "origin-response.json",
        )
    )

    with open(event_file) as fp:
        return json.load(fp)


def test_handler(origin_response, monkeypatch):
    response = handler(origin_response, {})
    assert response == {"status": "200", "statusDescription": "Ok", "body": "你好，世界！"}
