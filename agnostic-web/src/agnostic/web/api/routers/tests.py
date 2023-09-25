from uuid import UUID

from fastapi import Depends, APIRouter, HTTPException, Response, Request, status

from agnostic.core import schemas, dal

router = APIRouter(tags=["Tests"], prefix="/projects/{project_id}/test-runs/{test_run_id}/tests")


@router.post(
    "",
    responses={
        status.HTTP_201_CREATED: {
            "headers": {
                "Location": {"description": "URL of created created test", "type": "string"}
            }
        },
        status.HTTP_404_NOT_FOUND: {},
        status.HTTP_409_CONFLICT: {},
    },
    status_code=status.HTTP_201_CREATED,
)
async def create_test(
    test: schemas.TestCreate,
    project_id: UUID,
    test_run_id: UUID,
    request: Request,
    response: Response,
    tests: dal.Tests = Depends(dal.get_tests),
):
    test.test_run_id = test_run_id
    try:
        test_id = await tests.create(
            schemas.Test(**test.model_dump(exclude={"test_run_id"}), test_run_id=test_run_id)
        )
        response.headers.append("Location", f"{request.url.path}/{test_id}")
    except dal.DuplicateError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    except dal.ForeignKeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.put(
    "/{test_id}",
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
async def update_test(
    test: schemas.TestUpdate,
    project_id: UUID,
    test_run_id: UUID,
    test_id: UUID,
    request: Request,
    response: Response,
    tests: dal.Tests = Depends(dal.get_tests),
):
    t = schemas.Test(**test.model_dump(), test_run_id=test_run_id, id=test_id)
    try:
        await tests.update(t)
    except dal.NotFoundError:
        try:
            await tests.create(t)
            response.status_code = status.HTTP_201_CREATED
            response.headers.append("Location", f"{request.url.path}/{test_id}")
        except (dal.DuplicateError, dal.ForeignKeyError) as e:
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
    test: schemas.TestPatch,
    project_id: UUID,
    test_run_id: UUID,
    test_id: UUID,
    tests: dal.Tests = Depends(dal.get_tests),
):
    try:
        await tests.update(
            schemas.Test.model_construct(
                _fields_set=test.model_fields_set, **test.model_dump(), test_run_id=test_run_id, id=test_id
            ),
            exclude_unset=True,
        )
    except dal.NotFoundError as e:
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
    project_id: UUID,
    test_run_id: UUID,
    test_id: UUID,
    request: Request,
    response: Response,
    test_start: schemas.TestStart,
    tests: dal.Tests = Depends(dal.get_tests),
):
    test_start.id = test_id
    test_start.test_run_id = test_run_id
    try:
        await tests.update(test_start, exclude_unset=True)
    except dal.NotFoundError as e:
        try:
            await tests.create(test_start)
            response.status_code = status.HTTP_201_CREATED
            response.headers.append("Location", str(request.url.path).rstrip("/start"))
        except (dal.DuplicateError, dal.ForeignKeyError) as e:
            raise HTTPException(status.HTTP_409_CONFLICT, str(e))


@router.post(
    "/{test_id}/finish",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_200_OK,
)
async def finish_test(
    project_id: UUID,
    test_run_id: UUID,
    test_id: UUID,
    test_finish: schemas.TestFinish,
    tests: dal.Tests = Depends(dal.get_tests),
):
    test_finish.id = test_id
    test_finish.test_run_id = test_run_id
    try:
        await tests.update(
            test_finish,
            exclude_unset=True,
        )
    except dal.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.get(
    "/{test_id}",
    responses={
        status.HTTP_200_OK: {"model": schemas.Test},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_200_OK,
)
async def get_test(
    project_id: UUID, test_run_id: UUID, test_id: UUID, tests: dal.Tests = Depends(dal.get_tests)
) -> schemas.Test:
    try:
        return await tests.get(test_id)
    except dal.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.get(
    "",
    status_code=status.HTTP_200_OK,
)
async def get_tests(
    project_id: UUID, test_run_id: UUID, tests: dal.Tests = Depends(dal.get_tests)
) -> schemas.Tests:
    return schemas.Tests(await tests.get_all(test_run_id))
