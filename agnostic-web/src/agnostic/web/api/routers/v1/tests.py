import datetime
from uuid import UUID

from fastapi import Depends, APIRouter, HTTPException, Response, status

from agnostic.core import schemas, dal

router = APIRouter(tags=['Tests'])


@router.post('/projects/{project_id}/test-runs/{test_run_id}/tests', status_code=status.HTTP_201_CREATED)
async def create_test(test: schemas.v1.Test, project_id: UUID, test_run_id: UUID,
                      response: Response, tests: dal.Tests = Depends(dal.get_tests)):
    test.test_run_id = test_run_id
    try:
        test_id = await tests.create(test)
        response.headers.append('Location', f'/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}')
    except dal.DuplicateError as e:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            str(e)
        )
    except dal.ForeignKeyError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.put('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}')
async def update_test(test: schemas.v1.Test, project_id: UUID, test_run_id: UUID, test_id: UUID,
                      response: Response, tests: dal.Tests = Depends(dal.get_tests)):
    test.id = test_id
    test.test_run_id = test_run_id

    try:
        await tests.update(test)
    except dal.NotFoundError:
        try:
            await tests.create(test)
            response.status_code = status.HTTP_201_CREATED
            response.headers.append('Location', f'/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}')
        except (dal.DuplicateError, dal.ForeignKeyError) as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                str(e)
            )


@router.patch('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}')
async def update_test_fields(test: schemas.v1.Test, project_id: UUID, test_run_id: UUID, test_id: UUID,
                             tests: dal.Tests = Depends(dal.get_tests)):
    test.id = test_id
    test.test_run_id = test_run_id
    try:
        await tests.update(test, exclude_unset=True)
    except dal.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.post('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/start')
async def start_test(project_id: UUID, test_run_id: UUID, test_id: UUID,
                     response: Response, test: schemas.v1.Test, tests: dal.Tests = Depends(dal.get_tests)):
    test.id = test_id
    test.test_run_id = test_run_id
    try:
        await tests.update(test, exclude_unset=True)
    except dal.NotFoundError as e:
        try:
            await tests.create(test)
            response.status_code = status.HTTP_201_CREATED
            response.headers.append('Location', f'/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}')
        except (dal.DuplicateError, dal.ForeignKeyError) as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                str(e)
            )


@router.post('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/finish')
async def finish_test(project_id: UUID, test_run_id: UUID, test_id: UUID,
                      test: schemas.v1.TestFinish, tests: dal.Tests = Depends(dal.get_tests)):
    test.id = test_id
    test.test_run_id = test_run_id
    test.finish = test.finish or datetime.datetime.utcnow()
    try:
        await tests.update(test, exclude_unset=True)
    except dal.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.get('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}', response_model=schemas.v1.Test)
async def get_test(project_id: UUID, test_run_id: UUID, test_id: UUID, tests: dal.Tests = Depends(dal.get_tests)):
    try:
        return await tests.get(test_id)
    except dal.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.get('/projects/{project_id}/test-runs/{test_run_id}/tests', response_model=list[schemas.v1.Test])
async def get_tests(project_id: UUID, test_run_id: UUID, tests: dal.Tests = Depends(dal.get_tests)):
    return await tests.get_all(test_run_id)
