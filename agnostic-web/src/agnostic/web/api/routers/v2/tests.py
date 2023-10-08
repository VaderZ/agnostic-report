import datetime
import uuid

from fastapi import Depends, APIRouter, HTTPException, Response, Request, Query, status

from agnostic.core import crud
from agnostic.core.schemas import v2 as s

router = APIRouter(tags=["Tests"], prefix="/tests")


@router.post(
    "",
    responses={
        status.HTTP_201_CREATED: {
            "headers": {"Location": {"description": "URL of the created test", "type": "string"}}
        },
        status.HTTP_404_NOT_FOUND: {},
        status.HTTP_409_CONFLICT: {},
    },
    status_code=status.HTTP_201_CREATED,
)
async def create_test(
    test: s.TestCreate,
    request: Request,
    response: Response,
    tests: crud.Tests = Depends(crud.get_tests),
):
    try:
        test_id = await tests.create(test)
        response.headers.append("Location", f"{request.url.path}/{test_id}")
    except crud.DuplicateError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    except crud.ForeignKeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.put(
    "/{test_id}",
    responses={
        status.HTTP_201_CREATED: {
            "headers": {"Location": {"description": "URL of the created test", "type": "string"}}
        },
        status.HTTP_204_NO_CONTENT: {},
        status.HTTP_409_CONFLICT: {},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_test(
    test: s.TestUpdate,
    test_id: uuid.UUID,
    request: Request,
    response: Response,
    tests: crud.Tests = Depends(crud.get_tests),
):
    try:
        await tests.update(test_id, test)
    except crud.NotFoundError:
        try:
            await tests.create(s.TestCreate(id=test_id, **test.model_dump(exclude_unset=True)))
            response.status_code = status.HTTP_201_CREATED
            response.headers.append("Location", f"{request.url.path}/{test_id}")
        except (crud.DuplicateError, crud.ForeignKeyError) as e:
            raise HTTPException(status.HTTP_409_CONFLICT, str(e))


@router.patch(
    "/{test_id}",
    responses={
        status.HTTP_204_NO_CONTENT: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def patch_test(
    test: s.TestPatch,
    test_id: uuid.UUID,
    tests: crud.Tests = Depends(crud.get_tests),
):
    try:
        await tests.update(test_id, test, exclude_unset=True)
    except crud.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.post(
    "/{test_id}/start",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_201_CREATED: {},
        status.HTTP_409_CONFLICT: {},
    },
    status_code=status.HTTP_200_OK,
)
async def start_test(
    test_id: uuid.UUID,
    timestamp: s.Timestamp,
    tests: crud.Tests = Depends(crud.get_tests),
):
    try:
        await tests.update(
            id_=test_id,
            test=s.TestPatch(
                start=timestamp.timestamp or datetime.datetime.now(datetime.UTC),
                finish=None,
            ),
            exclude_unset=True,
        )
    except crud.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.post(
    "/{test_id}/finish",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_200_OK,
)
async def finish_test(
    test_id: uuid.UUID,
    outcome: s.TestOutcome,
    tests: crud.Tests = Depends(crud.get_tests),
):
    try:
        await tests.update(
            id_=test_id,
            test=s.TestPatch(
                finish=outcome.timestamp or datetime.datetime.now(datetime.UTC),
                result=outcome.result,
                reason=outcome.reason,
                error_message=outcome.reason,
            ),
            exclude_unset=True,
        )
    except crud.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.get(
    "/{test_id}",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_200_OK,
)
async def get_test(test_id: uuid.UUID, tests: crud.Tests = Depends(crud.get_tests)) -> s.Test:
    try:
        return await tests.get(test_id)
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
async def get_tests(
    response: Response,
    test_run_id: uuid.UUID | None = Query(None),
    page: int = Query(1),
    page_size: int = Query(100),
    tests: crud.Tests = Depends(crud.get_tests),
) -> s.Tests:
    ts = await tests.get_all(test_run_id, page, page_size)
    response.headers.append("X-Total-Count", str(ts.count))
    return ts.items
