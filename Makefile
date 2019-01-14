all: test run

run:
	python ./main.py

clean:
	rm -rf event-reminder-tmp/

test:
	python -m unittest
