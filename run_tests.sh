#!/usr/bin/env bash

docker-compose exec api pytest --cov=/code/app --cov-report=term-missing