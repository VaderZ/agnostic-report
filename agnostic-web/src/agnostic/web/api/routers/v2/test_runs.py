import datetime
import uuid

from fastapi import Depends, APIRouter, HTTPException, Response, Request, Query, status

from agnostic.core import crud
from agnostic.core.schemas import v2 as s

router = APIRouter(tags=["Test Runs"], prefix="/test-runs")


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
    test_run: s.TestRunCreate,
    request: Request,
    response: Response,
    test_runs: crud.TestRuns = Depends(crud.get_test_runs),
):
    try:
        test_run_id = await test_runs.create(test_run)
        response.headers.append("Location", f"{request.url.path}/{test_run_id}")
    except crud.DuplicateError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    except crud.ForeignKeyError as e:
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
    test_run: s.TestRunUpdate,
    test_run_id: uuid.UUID,
    request: Request,
    response: Response,
    test_runs: crud.TestRuns = Depends(crud.get_test_runs),
):
    try:
        await test_runs.update(test_run_id, test_run)
    except crud.NotFoundError:
        try:
            await test_runs.create(
                s.TestRunCreate(id=test_run_id, **test_run.model_dump(exclude_unset=True))
            )
            response.status_code = status.HTTP_201_CREATED
            response.headers.append("Location", f"{request.url.path}/{test_run.id}")
        except (crud.DuplicateError, crud.ForeignKeyError) as e:
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
    test_run: s.TestRunPatch,
    test_run_id: uuid.UUID,
    test_runs: crud.TestRuns = Depends(crud.get_test_runs),
):
    try:
        await test_runs.update(test_run_id, test_run, exclude_unset=True)
    except crud.NotFoundError as e:
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
    test_run_id: uuid.UUID,
    timestamp: s.Timestamp,
    test_runs: crud.TestRuns = Depends(crud.get_test_runs),
):
    try:
        await test_runs.update(
            id_=test_run_id,
            test_run=s.TestRunPatch(
                start=timestamp.timestamp or datetime.datetime.now(datetime.UTC),
                heartbeat=timestamp.timestamp or datetime.datetime.now(datetime.UTC),
                finish=None,
            ),
            exclude_unset=True,
        )
    except crud.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.post(
    "/{test_run_id}/finish",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_200_OK,
)
async def finish_test_run(
    test_run_id: uuid.UUID,
    timestamp: s.Timestamp,
    test_runs: crud.TestRuns = Depends(crud.get_test_runs),
):
    try:
        await test_runs.update(
            id_=test_run_id,
            test_run=s.TestRunPatch(
                finish=timestamp.timestamp or datetime.datetime.now(datetime.UTC)
            ),
            exclude_unset=True,
        )
    except crud.NotFoundError as e:
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
    test_run_id: uuid.UUID,
    timestamp: s.Timestamp,
    test_runs: crud.TestRuns = Depends(crud.get_test_runs),
):
    try:
        await test_runs.update(
            id_=test_run_id,
            test_run=s.TestRunPatch(
                heartbeat=timestamp.timestamp or datetime.datetime.now(datetime.UTC)
            ),
            exclude_unset=True,
        )
    except crud.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.post(
    "/{test_run_id}/property",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_200_OK,
)
async def add_test_run_property(
    test_run_id: uuid.UUID,
    prop: s.KeyValue,
    test_runs: crud.TestRuns = Depends(crud.get_test_runs),
):
    try:
        test_run = await test_runs.get(test_run_id)
        if not test_run.properties:
            test_run.properties = {}
        test_run.properties.update({prop.key: prop.value})
        await test_runs.update(test_run_id, test_run)
    except crud.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.get(
    "/{test_run_id}",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_200_OK,
)
async def get_test_run(
    test_run_id: uuid.UUID, test_runs: crud.TestRuns = Depends(crud.get_test_runs)
) -> s.TestRun:
    try:
        return await test_runs.get(test_run_id)
    except crud.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.get(
    "",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_200_OK,
)
async def get_test_runs(
    response: Response,
    project_id: uuid.UUID | None = Query(None),
    page: int = Query(1),
    page_size: int = Query(100),
    test_runs: crud.TestRuns = Depends(crud.get_test_runs),
) -> s.TestRuns:
    trs = await test_runs.get_all(project_id, page, page_size)
    response.headers.append("X-Total-Count", str(trs.count))
    return trs.items
