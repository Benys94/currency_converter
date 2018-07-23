lint: pylint

pylint:
	FILES=`find . \
                -path './libs' -prune -o \
                -type d -exec test -e '{}/__init__.py' \; -print -prune -o \
                -name '*.py' -print`; \
        python3 -m pylint $${FILES}

test: unittests

unittests:
	coverage3 run -m pytest -rxXs tests/unit
	coverage3 report
	coverage3 html
