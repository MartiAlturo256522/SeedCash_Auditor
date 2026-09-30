.PHONY: lint test draft

lint:
	python3 tools/lint_brain.py

test: lint
	python3 -m unittest discover -s tools/tests -v

draft:
	python3 tools/file_issue.py --finding $(FINDING)
