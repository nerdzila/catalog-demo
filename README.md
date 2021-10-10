# catalog-demo
A practice project that implements an API to interact with simple product catalog.

## Quick Start

### Prerequisities

To run this project you need Docker installed:

* [Windows](https://docs.docker.com/windows/started)
* [OS X](https://docs.docker.com/mac/started/)
* [Linux](https://docs.docker.com/linux/started/)

Additionally `docker-compose` is also required, this comes pre-installed with some 
versions of Docker, in case your system is missing it, please refer to the:

[Docker Compose install page](https://docs.docker.com/compose/install/)

### Start the server

Just run:

```bash
docker-compose up
```

API will be available at http://localhost:8080/. But the best way to get acquainted with is is to 
take a look at the interactive documentation:  http://localhost:8080/docs.

### Running the tests

```bash
./run_tests.sh
```

Will run the tests and print a coverage report
