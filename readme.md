# Agnostic Report

Agnostic is a test reporting server primarily focused on enriching integration test reports with details beyond 
simple asserts and error messages that makes them way more useful for debugging and root cause analysis.
We started developing Agnostic to support on-target integration testing of the [Holoplot X1](https://holoplot.com/systems/)
audio system and even the very first version of it brought more clarity to test results, helped to improve development speed 
and simplified collaboration within and between teams.

While Agnostic is deeply work-in-progress and has a bunch of incomplete and missing features one might still want to try it 
if they are looking for the following combined in a single tool:

- Centralized test results storage for multiple projects
- Configurable test report layout per project
- Near real-time updates of the test progress
- Support of distributed testing. Agnostic provides a way to combine tests executed in different processes and/or on different machines
as well as metrics, logs and properties captured from a distributed environment in a single test run
- Tracing SUT and test code branches of test runs 
- Capturing test run level metrics (e.g. device update time) and properties (e.g. firmware version a device was upgraded from)
- Capturing test level metrics (e.g. time required for a certain operation)
- Capturing test run and test level logs
- Capturing request details within test runs (currently HTTP, GRPC, NATS and SQL supported)
- Capturing over time metrics within test runs, analyzing them as charts and/or aggregates
- Project level history and aggregates of test run metrics
- Integration with pytest
- REST-like API for integration with other tools

Before getting your hands dirty have a look at several screenshots to know what to expect:

### Project Summary

![Project Summary](docs/images/project-summary.png)

### Test Run Summary

![Test Run Summary](docs/images/test-run-summary.png)

### Test Details

![Test Details](docs/images/test-details.png)

### Test Run Charts

![Test Run Charts](docs/images/test-run-charts.png)

## Build and Deploy

### Docker

Running Agnostic with external PostgreSQL server

#### Prerequisites

- Docker 19.03+

#### Build container

1. Checkout the repository
2. Change working directory to the root of the cloned repo
```shell
cd agnostic
```
3. Build the container
```shell
docker build -t agnostic -f ./docker/deployment/Dockerfile .
```

#### Run container

1. Create a database for Agnostic at PostgreSQL database server
2. Run the container
```shell
docker run -t agnostic -p 8000:8000 -e AGNOSTIC_DB_NAME=<database name> -e AGNOSTIC_DB_USERNAME=<username> -e AGNOSTIC_DB_PASSWORD=<password> -e AGNOSTIC_DB_HOST=<PostreSQL address> -e AGNOSTIC_DB_PORT=<PostgreSQL port> 
```
3. Check that Agnostic is available at http://localhost:8000

### Docker Compose

Running self-contained Agnostic setup with dockerized PostgreSQL server 

#### Prerequisites

- Docker 19.03+
- Docker Compose 1.27+

#### Run docker compose environment

1. Checkout the repository
2. Change working directory to the root of the cloned repo
```shell
cd agnostic
```
3. Run docker compose environment 
```shell
docker-compose up -d --build
```


## Build pytest Plugin

1. Checkout the repository 
. Change working directory
```shell
cd src/plugins/pytest
```
2. Build the plugin
```shell
python3 -m build .
```

## Development


#### Prerequisites

For local development:

- Python 3.10+
- NodeJS 14.0

For development in the container:

- Docker 19.03+


#### Use development servers locally
1. Checkout the repository
2. Install Python dependencies
```shell
pip install -r requirements.txt
```
3. Run API server in hot reload mode on port `8000`
```shell
python3 ./src/run.py
```
4. Install NodeJS dependencies
```shell
cd src/agnostic_report/ui
npm install
```
5. Run UI server in hot reload mode on port `3000`
```shell
export VITE_API_URL=http://localhost:8000/api/v1
npm run dev
```


#### Run development docker compose environment
1. Checkout the repository
2. Change working directory to the root of the cloned repo
```shell
cd agnostic
```
3. Run docker compose environment 
```shell
docker-compose -f docker-compose.dev.yaml up
```

#### Deploy Demo Data
1. Checkout the repository
2. Navigate to
```shell
cd src/dev/demo-data
```
3. Install dependencies
```shell
pip install -r requirements.txt
```
4. Generate demo data
```shell
python3 datagen.py <postgresql_url>
```
if `postgresql_url` is omitted the tool attempts to deploy data to `postgresql+asyncpg://postgres:postgres@localhost:5432/agnostic`

## Configuring Agnostic Report

### Create a project
1. Navigate to `http://<agnostic_url>/projects#admin=true`
2. Use `New Project` button to create a project

### Configuring a project
1. Navigate to `http://<agnostic_url>/projects/<project_uuid>#admin=true`
2. Use `Edit` button next to the project name to edit JSON configuration

For some insights on what could be configured check out configurations from demo data under 
`src/dev/demo-data/resources/configs`

### Using pytest plugin
After installing a plugin run your test project with the following options:
```shell
pytest . --agnostic_url http://<agnostic_url>/api/v1 --agnostic_project_id <project_uuid>
```

The full list of available options:

- `agnostic_url`
- `agnostic_project_id`
- `agnostic_test_run_id` - useful for merging parallelized tests into a single test run, if omitted test run ID will be generated automatically
- `agnostic_sut_branch`
- `agnostic_sut_version`
- `agnostic_test_branch`
- `agnostic_test_version`
- `agnostic_variant` - can be specified multiple times in a format `<variant_name>=<variant_value>` 
- `agnostic_property` - can be specified multiple times in a format `<property_name>=<property_value>`
- `agnostic_redis_host` - required to support Agnostic usage in distributed manner 
- `agnostic_redis_port`- required to support Agnostic usage in distributed manner
- `agnostic_redis_db` - required to support Agnostic usage in distributed manner
- `agnostic_http_client` - HTTP client implementation, currently is not supported from CLI and can be only set from pytest hooks
- `agnostic_offline` - prevents Agnostic from sending data to report server, useful during development of your test project
