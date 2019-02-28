all: test run

run:
	python ./app/app_main.py

clean:
	rm -rf event-reminder-tmp/

test:
	python -m unittest

lang-uk:
	lrelease ./locale/uk_UA.tr -qm ./app/locale/uk_UA.qm

lang-en:
	lrelease ./locale/en_US.tr -qm ./app/locale/en_US.qm

lang: lang-uk lang-en
