BASE := $(shell /bin/pwd)

all: build

.PHONY: clean env build test invoke deploy

clean:
	rm -rf .aws-sam/build

Pipfile.lock: Pipfile
	pipenv update --dev

requirements.txt: Pipfile.lock
	pipenv install --dev
	pipenv lock --requirements > $@

lambdas/origin_response/requirements.txt: requirements.txt
	cat $< | sed 's/^-e //g' > $@

env: Pipfile.lock requirements.txt lambdas/origin_response/requirements.txt

build: env
	cp -r ./src ./lambdas/origin_response/
	pipenv run sam build --use-container
	rm -rf ./lambdas/origin_response/src

test:
	pipenv run pytest tests/unit

invoke:
	pipenv run sam local invoke OriginResponseFunction --event events/origin-response.json

SOURCES := $(shell find ./lambdas -name '*.py') $(shell find ./src -name '*.py')

deploy: build $(SOURCES)
	pipenv run sam deploy
