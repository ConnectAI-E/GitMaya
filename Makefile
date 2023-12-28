.PHONY: build

build:
	@echo "Building..."
	docker build -t gitmaya -f deploy/Dockerfile .
	@echo "Done."


FORCE:

