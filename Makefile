.PHONY:

setup:
	python setup.py sdist

upload: setup
	twine upload dist/*