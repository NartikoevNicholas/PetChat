include .env


docker_run:
	docker-compose -f docker-compose.yml up -d --remove-orphans
	poetry run python3 -m alembic upgrade head
	docker ps -a

open_postgres:
	docker-compose exec -it postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

docker_clean:
	docker rm -f `sudo docker ps -qa`
	docker rmi -f `sudo docker images -qa`
	docker volume prune -a
	docker network prune
	docker system prune --volumes

test:
	poetry run python3 -m pytest --verbosity=2 --showlocals --log-level=DEBUG
