import datetime
from uuid import UUID

from fastapi import Depends, APIRouter, HTTPException, Response, status

from agnostic.core import schemas_v1, dal_v1

router = APIRouter(tags=['Tests'])


@router.post('/projects/{project_id}/test-runs/{test_run_id}/tests', status_code=status.HTTP_201_CREATED)
async def create_test(test: schemas_v1.Test, project_id: UUID, test_run_id: UUID,
                      response: Response, tests: dal_v1.Tests = Depends(dal_v1.get_tests)):
    test.test_run_id = test_run_id
    try:
        test_id = await tests.create(test)
        response.headers.append('Location', f'/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}')
    except dal_v1.DuplicateError as e:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            str(e)
        )
    except dal_v1.ForeignKeyError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.put('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}')
async def update_test(test: schemas_v1.Test, project_id: UUID, test_run_id: UUID, test_id: UUID,
                      response: Response, tests: dal_v1.Tests = Depends(dal_v1.get_tests)):
    test.id = test_id
    test.test_run_id = test_run_id

    try:
        await tests.update(test)
    except dal_v1.NotFoundError:
        try:
            await tests.create(test)
            response.status_code = status.HTTP_201_CREATED
            response.headers.append('Location', f'/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}')
        except (dal_v1.DuplicateError, dal_v1.ForeignKeyError) as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                str(e)
            )


@router.patch('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}')
async def update_test_fields(test: schemas_v1.Test, project_id: UUID, test_run_id: UUID, test_id: UUID,
                             tests: dal_v1.Tests = Depends(dal_v1.get_tests)):
    test.id = test_id
    test.test_run_id = test_run_id
    try:
        await tests.update(test, exclude_unset=True)
    except dal_v1.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.post('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/start')
async def start_test(project_id: UUID, test_run_id: UUID, test_id: UUID,
                     response: Response, test: schemas_v1.Test, tests: dal_v1.Tests = Depends(dal_v1.get_tests)):
    test.id = test_id
    test.test_run_id = test_run_id
    try:
        await tests.update(test, exclude_unset=True)
    except dal_v1.NotFoundError as e:
        try:
            await tests.create(test)
            response.status_code = status.HTTP_201_CREATED
            response.headers.append('Location', f'/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}')
        except (dal_v1.DuplicateError, dal_v1.ForeignKeyError) as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                str(e)
            )


@router.post('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/finish')
async def finish_test(project_id: UUID, test_run_id: UUID, test_id: UUID,
                      test: schemas_v1.TestFinish, tests: dal_v1.Tests = Depends(dal_v1.get_tests)):
    test.id = test_id
    test.test_run_id = test_run_id
    test.finish = test.finish or datetime.datetime.utcnow()
    try:
        await tests.update(test, exclude_unset=True)
    except dal_v1.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.get('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}', response_model=schemas_v1.Test)
async def get_test(project_id: UUID, test_run_id: UUID, test_id: UUID, tests: dal_v1.Tests = Depends(dal_v1.get_tests)):
    try:
        return await tests.get(test_id)
    except dal_v1.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.get('/projects/{project_id}/test-runs/{test_run_id}/tests', response_model=list[schemas_v1.Test])
async def get_tests(project_id: UUID, test_run_id: UUID, tests: dal_v1.Tests = Depends(dal_v1.get_tests)):
    return await tests.get_all(test_run_id)
