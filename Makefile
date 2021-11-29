docker-build:
	@pipenv lock --keep-outdated --requirements > requirements.txt
	@docker build --tag quart-base .

docker-run:
	@docker run --publish 5000:5000 quart-base

rm-cache:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -name \*.pyc -delete

create-reqs:
	@pipenv lock --keep-outdated --requirements > requirements.txt
