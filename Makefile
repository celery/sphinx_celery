PROJ=sphinx_celery
PYTHON=python

flakecheck:
	# the only way to enable all errors is to ignore something bogus
	flake8 --ignore=X999 "$(PROJ)"

flakediag:
	-$(MAKE) flakecheck

flakepluscheck:
	flakeplus --2.7 "$(PROJ)"

flakeplusdiag:
	-$(MAKE) flakepluscheck

flakes: flakediag flakeplusdiag

test:
	nosetests -x

cov:
	nosetests -x --with-coverage --cover-html --cover-branch

removepyc:
	-find . -type f -a \( -name "*.pyc" -o -name "*$$py.class" \) | xargs rm
	-find . -type d -name "__pycache__" | xargs rm -r

gitclean: removepyc
	git clean -xdn

gitcleanforce:
	git clean -xdf

distcheck: flakecheck test gitclean

dist: gitcleanforce removepyc
