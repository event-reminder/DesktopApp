all: test run

run:
	python ./app/app_main.py

clean:
	rm -rf event-reminder-tmp/

test:
	python -m unittest

lang:
	lrelease ./app/locale/tr/uk_UA.tr -qm ./app/locale/qm/uk_UA.qm
	lrelease ./app/locale/tr/en_US.tr -qm ./app/locale/qm/en_US.qm
