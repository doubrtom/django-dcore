clean:
	rm -rf dist/*
	rm -rf build/*

upload:
	twine upload dist/*

create:
	python setup.py sdist bdist_wheel
