.PHONY: build

build:
	@echo "Building..."
	docker build -t connectai/gitmaya -f deploy/Dockerfile .
	@echo "Done."

build-proxy:
	@echo "Building proxy..."
	git submodule update --init && docker build -t connectai/gitmaya-proxy -f deploy/Dockerfile.proxy .
	@echo "Done."

push:
	@echo "Push Image..."
	docker push connectai/gitmaya
	docker push connectai/gitmaya-proxy
	@echo "Done."

startup:
	@echo "Deploy..."
	[ -f deploy/.env ] || cp deploy/.env.example deploy/.env
	cd deploy && docker-compose up -d
	@echo "Waiting Mysql Server..."
	sleep 3
	@echo "Init Database..."
	cd deploy && docker-compose exec gitmaya flask --app model.schema:app create
	@echo "Done."
