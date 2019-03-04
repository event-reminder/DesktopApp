.PHONY: test test-verbose clean pre_build build install deploy

all: test clean test install

run:
	python ./app/app_main.py

clean:
	rm -rf event-reminder-tmp/

test:
	python -m unittest

test-verbose:
	python -m unittest -v

lang-uk:
	lrelease ./locale/uk_UA.tr -qm ./erdesktop/locale/uk_UA.qm

lang-en:
	lrelease ./locale/en_US.tr -qm ./erdesktop/locale/en_US.qm

lang: lang-uk lang-en

clean:
	rm -rf build/ djexp.egg-info/ dist/

pre_build:
	pip3 install --user --upgrade setuptools wheel twine

build: pre_build
	python setup.py sdist bdist_wheel

install: pre_build
	python setup.py install

deploy: build
	twine upload dist/*

test-deploy: build
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*
