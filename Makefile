.PHONY: test test-verbose clean pre_build build install deploy test_deploy lang lang_resources img_resources resources

all: test clean test install

clean:
	rm -rf build/ erdesktop.egg-info/ dist/

test:
	coverage run -m unittest
	coverage html

test-verbose:
	coverage run -m unittest -v
	coverage html

pre_build:
	pip3 install --user --upgrade setuptools wheel twine

build:
	python setup.py sdist bdist_wheel

install: pre_build
	python setup.py install

deploy: build
	twine upload dist/*

test_deploy: build
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

lang:
	mkdir -p ./locale/out
	lrelease ./locale/uk_UA.tr -qm ./locale/out/uk_UA.qm
	lrelease ./locale/en_US.tr -qm ./locale/out/en_US.qm

lang_resources: lang
	pyrcc5 -o ./erdesktop/resources/languages.py ./resources/languages.qrc
	rm -rf ./locale/out/

resources: lang_resources
