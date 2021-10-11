# catalog-demo
A practice project that implements an API to interact with simple product catalog.

## Getting started

### Prerequisities

To run this project you need Docker installed:

* [Windows](https://docs.docker.com/windows/started)
* [OS X](https://docs.docker.com/mac/started/)
* [Linux](https://docs.docker.com/engine/install/)

Additionally `docker-compose` is also required, this comes pre-installed with some 
versions of Docker, in case your system is missing it, please refer to the:

[Docker Compose install page](https://docs.docker.com/compose/install/)


### Quick Start

If you want to get right into things without worrying about AWS configuration, just do the following:


```bash
touch .env
docker-compose up -d
```

Most of the functionality will be present but no notification emails will be sent, if you want to enable them, use the instructions
in the following section instead.


### Full functionality with AWS credentials and SES configuration

This project uses AWS SES to send email notifications, but you'll need to provide your own 
AWS credentials for this to work. In order to do so create a `.env` file at the root of
the project it. Should contain the following:

```
AWS_DEFAULT_REGION=<Default AWS region>
AWS_ACCESS_KEY_ID=<Your Key ID>
AWS_SECRET_ACCESS_KEY=<Your Acesss Key>
```

And start the server with:

```bash
docker-compose up -d
```

Additionally, you need to upload this project's email template to your SES account, this can be done in this way:

```bash
docker-compose exec api python /code/app/notification.py --upload-template
```

### Checking out the API

Whether you opted for the quick start or the full featured alternative, the API should now be running at http://localhost:8080/, but the really interesting part is the interactive documentation available at:

http://localhost:8080/docs

The following endpoints accept anonymous/unauthenticated requests:

* `GET /`
* `GET /token`
* `GET /products/`
* `GET /products/{product_id}`

But for the full experience you should click on the Authorize button on the top left and enter the following credentials:

User: `escribele.a.alfonso@gmail.com`

Password: `not_a_real_password`

### Running the tests

There's a convenience script to trigger the test suite from outside the container:

```bash
./run_tests.sh
```

This will run the tests and print a coverage report, it doesn't matter whether you started the quick start or did the full SES configuration,
the test script uses [moto](http://docs.getmoto.org/en/latest/) to mock the notification service,
so it will test it regardless of environmet.

## Navigating the code

I decided to develop this project as a [FastAPI](https://fastapi.tiangolo.com/) REST API that uses
[SQLAlchemy](https://docs.sqlalchemy.org) as an ORM to connect to the database.

The general structure of the application is as follows.

[main.py](app/main.py) contains the app initialization, defines some dependencies and finally declares every endpoint exposed by the API,
a typical endpoint declaration looks like this:

```python
@app.put("/users/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    user_in: schemas.UserIn,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user)
):
```

The decorator `@app.put("/users/{user_id}", response_model=schemas.UserOut)` defines de HTTP method this _path operation function_ will listen to, 
then it declares the route (with optional path parameters) and finally the structure (schema) of the JSON response.

The function itself takes several types of arguments:

* Path parameters (`user_id`)
* Body parameters defined as schemas (`user_in: schemas.UserIn`)
* Autoinjected dependencies (`db: Session = Depends(get_db)`)

Finally, there's a particular construct that's used several times in the code that may seem confusing:

```
_: models.User = Depends(get_current_user)
```

This ensures that only authenticated users access the endpoint by trying to get a user model
from a JWT token in the request's header, the user model returned is not always used in the function
itself and it's usual to see it assigned to `_` and ignored.

[models.py](app/models.py) contains the Data Model definition used by SQLAlchemy to initialize the Database.

[schemas.py](app/schemas.py) contains the [Pydantic](https://pydantic-docs.helpmanual.io/) schemas used to specify 
the structure of the JSON payloads that the API accepts ands returns. Those are relevant for validation purposes,
but also help making the interactive documentation more accesible. Every kind of JSON parameter or response gets
its own schema, there are several Schemas for each database model as they get interacted with using slightly different kinds
of requests/responses.

[test_main.py](app/test_main.py) contains a [pytest](https://docs.pytest.org/en/6.2.x/) test suite that tries to get as close as possible
to 100% coverage by invoking every API endpoint.

[crud.py](app/crud.py) are utilities used to interact with the DB, independent from the endpoint that calls it, the idea of 
separating those utilities is to make them more reusable and testeable.

[security.py](app/security.py) contains the auxiliary functions needed to implement JWT authentication.

[notification.py](app/notification.py) has the code related to AWS SES and sending notifications via email.

[database.py](app/database.py) contains code to define the DB connection, it is also concerned with declaring some default records for demo purposes.

[config.py](app/config.py) contains some configuration variables.


## Design choices

FastAPI was chosen between the frameworks I'm familiar with because it is efficient and well documented, but also because it provided me 
with an easy path to an autogenerated interactive documentation and a functional test suite. Structure-wise I tried
to follow the simple structure proposed in the FastAPI docs (creating aditional modules as needed). This worked OK for this small project, but 
in the end some modules where starting to grow to unmanageable sizes.

As backend I chose an instance of in-memory `sqlite`, which is something I would never pick for a "real" project, but I knew I would be
constantly tearing down and recreating databases: this made this process easier and faster.
Plus, I didn't want to spend a lot of time configuring a proper DBMS.

On the flip side, I had to use an ORM to abstract database access and to be able to later replace `sqlite` as painlessly as possible.
SQLAlchemy was chosen because it integrates nicely with FastAPI, being able to utilize its `async` features.

`pytest` was a no-brainer as it's the _de facto_ standard, I just added a couple of coverage plugins so I was alerted 
to parts of the code which I wasn't testing.

Finally, I made the decision to use AWS SES to send notifications mostly for the challenge, I had never used it 
but it draw my curiosity because it was mentioned as a "plus" in the specification. And it was indeed a challange to
learn it and get it running and tested it in the limited time I had. In the end "it works" but still can use a lot of improvement.


## Next steps

Code-wise there's a lot to do:

* The whole app should be reestructured. There are several modules with sections separated by comments that should be broken down into different files.
* There are scattered `# TODO:`s clamoring for attention.
* There is a non-trivial amount of redundant code asking to be refactored.
* The SES notification code and AWS integration must be improved.

All in all, if we wanted to keep growing the application the restructure should take priority, to be able to add new models and endpoints in an
orderly fashion.

When thinking about scaling it, the first step would be to connect it to a proper database while ensuring that FastAPI's `async` capabilites
are properly taken into account. The next step would be to change the Docker configuration so our main app is no longer a `uvicorn` standalone server,
but a node behind a load balancer. Another common optimization for this kind of stack is adding celery + flower to take charge of longer-running
processes.
