import datetime
from uuid import UUID

from fastapi import Depends, APIRouter, HTTPException, Response, Request, status

from agnostic.core import schemas, dal

router = APIRouter(tags=["Test Runs"], prefix="/projects/{project_id}/test-runs")


@router.post(
    "",
    responses={
        status.HTTP_201_CREATED: {
            "headers": {
                "Location": {"description": "URL of the created test run", "type": "string"}
            }
        },
        status.HTTP_404_NOT_FOUND: {},
        status.HTTP_409_CONFLICT: {},
    },
    status_code=status.HTTP_201_CREATED,
)
async def create_test_run(
    test_run: schemas.TestRunCreate,
    project_id: UUID,
    request: Request,
    response: Response,
    test_runs: dal.TestRuns = Depends(dal.get_test_runs),
) -> None:
    try:
        test_run_id = await test_runs.create(
            schemas.TestRun(**test_run.model_dump(exclude={"project_id"}), project_id=project_id)
        )
        response.headers.append("Location", f"{request.url.path}/{test_run_id}")
    except dal.DuplicateError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    except dal.ForeignKeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.put(
    "/{test_run_id}",
    responses={
        status.HTTP_201_CREATED: {
            "headers": {
                "Location": {"description": "URL of the created test run", "type": "string"}
            }
        },
        status.HTTP_204_NO_CONTENT: {},
        status.HTTP_409_CONFLICT: {},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_test_run(
    test_run: schemas.TestRunUpdate,
    project_id: UUID,
    test_run_id: UUID,
    request: Request,
    response: Response,
    test_runs: dal.TestRuns = Depends(dal.get_test_runs),
):
    tr = schemas.TestRun(**test_run.model_dump(), project_id=project_id, id=test_run_id)
    try:
        await test_runs.update(tr)
    except dal.NotFoundError:
        try:
            await test_runs.create(tr)
            response.status_code = status.HTTP_201_CREATED
            response.headers.append("Location", str(request.url.path))
        except (dal.DuplicateError, dal.ForeignKeyError) as e:
            raise HTTPException(status.HTTP_409_CONFLICT, str(e))


@router.patch(
    "/{test_run_id}",
    responses={
        status.HTTP_204_NO_CONTENT: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def patch_test_run(
    test_run: schemas.TestRunUpdate,
    project_id: UUID,
    test_run_id: UUID,
    test_runs: dal.TestRuns = Depends(dal.get_test_runs),
):
    try:
        await test_runs.update(
            schemas.TestRun(
                **test_run.model_dump(exclude_unset=True), project_id=project_id, id=test_run_id
            ),
            exclude_unset=True,
        )
    except dal.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.post(
    "/{test_run_id}/start",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_201_CREATED: {},
        status.HTTP_409_CONFLICT: {},
    },
    status_code=status.HTTP_200_OK,
)
async def start_test_run(
    project_id: UUID,
    test_run_id: UUID,
    timestamp: schemas.Timestamp,
    request: Request,
    response: Response,
    test_runs: dal.TestRuns = Depends(dal.get_test_runs),
):
    tr = schemas.TestRun(
        id=test_run_id,
        project_id=project_id,
        start=timestamp.timestamp or datetime.datetime.utcnow(),
    )
    try:
        await test_runs.update(
            tr,
            exclude_unset=True,
        )
    except dal.NotFoundError as e:
        await test_runs.create(tr)
        response.status_code = status.HTTP_201_CREATED
        response.headers.append("Location", str(request.url.path).rstrip("/start"))
    except (dal.DuplicateError, dal.ForeignKeyError) as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))


@router.post(
    "/{test_run_id}/finish",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_200_OK,
)
async def finish_test_run(
    project_id: UUID,
    test_run_id: UUID,
    timestamp: schemas.Timestamp,
    test_runs: dal.TestRuns = Depends(dal.get_test_runs),
):
    try:
        await test_runs.update(
            schemas.TestRun(
                id=test_run_id,
                project_id=project_id,
                finish=timestamp.timestamp or datetime.datetime.utcnow(),
            ),
            exclude_unset=True,
        )
    except dal.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.post(
    "/{test_run_id}/heartbeat",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_200_OK,
)
async def update_test_run_heartbeat(
    project_id: UUID,
    test_run_id: UUID,
    timestamp: schemas.Timestamp,
    test_runs: dal.TestRuns = Depends(dal.get_test_runs),
):
    try:
        await test_runs.update(
            schemas.TestRun(
                id=test_run_id,
                project_id=project_id,
                heartbeat=timestamp.timestamp or datetime.datetime.utcnow(),
            ),
            exclude_unset=True,
        )
    except dal.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.post(
    "/{test_run_id}/property",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_200_OK,
)
async def set_test_run_property(
    project_id: UUID,
    test_run_id: UUID,
    prop: schemas.KeyValue,
    test_runs: dal.TestRuns = Depends(dal.get_test_runs),
):
    try:
        test_run = await test_runs.get(test_run_id)
        if not test_run.properties:
            test_run.properties = {}
        test_run.properties.update({prop.key: prop.value})
        await test_runs.update(test_run)
    except dal.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.get(
    "/{test_run_id}",
    responses={
        status.HTTP_200_OK: {"model": schemas.TestRun},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_200_OK,
)
async def get_test_run(
    project_id: UUID, test_run_id: UUID, test_runs: dal.TestRuns = Depends(dal.get_test_runs)
) -> schemas.TestRun:
    try:
        return await test_runs.get(test_run_id)
    except dal.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.get(
    "",
    status_code=status.HTTP_200_OK,
)
async def get_test_runs(
    project_id: UUID, test_runs: dal.TestRuns = Depends(dal.get_test_runs)
) -> schemas.TestRuns:
    return schemas.TestRuns(await test_runs.get_all(project_id))
