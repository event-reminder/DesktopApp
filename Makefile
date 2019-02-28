all: test run

run:
	python ./app/app_main.py

clean:
	rm -rf event-reminder-tmp/

test:
	python -m unittest
