# Digital Product Passport - Data Repository backend

This application is meant to serve as a proof-of-concept for a dynamic, federated, extensible Digital Product Passport data repository, intended to support a wide variety of use-cases.

Documentation is to follow:

## Running the application

Install the requirements from the requirements.txt file first.

To run the application, use the following command.

```shell
uvicorn app.main:app --port 8001 --reload --log-config logging.json
```

## Current roadmap

This application is intended to be open-sourced, and thus basic functionality is to be setup as first priority.

- Data models for the backend data - in-progress.
- Support for at least 1 stable persistent backend alternative for the dev mode (i.e Minio and MongoDB/Postgres)
- Support for connecting with other DPP data repositories
- Access-control mechanisms and signing mechanisms for verifying data integrity and authenticity.
