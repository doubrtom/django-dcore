clean:
	rm -rf dist/*
	rm -rf build/*

upload:
	pipenv run twine upload dist/*

create:
	pipenv run python setup.py sdist bdist_wheel

