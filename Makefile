install:
	pip install --requirement=requirements.app.txt --target=./graphql/lib
	pip install --requirement=requirements.dev.txt

run:
	dev_appserver.py graphql/ --allow_skipped_files True

cov:
	# relies on configuration in `setup.cfg`
	py.test --cov-report html --cov=graphql/app --cov=graphql/config
	open coverage/graphql/index.html

check:
	# relies on configuration in `setup.cfg`
	py.test --flakes graphql/app graphql/config

watch:
	# relies on configuration in `setup.cfg`
	py.test --looponfail
