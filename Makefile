include .env


docker_run:
	docker-compose -f docker-compose.yml up -d --remove-orphans
	docker ps -a

open_postgres:
	docker-compose exec -it postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

docker_clean:
	docker rm -f `sudo docker ps -qa`
	docker rmi -f `sudo docker images -qa`
	docker volume prune -a
	docker network prune
	docker system prune --volumes
