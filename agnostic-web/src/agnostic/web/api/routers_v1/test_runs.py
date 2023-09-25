import datetime
from uuid import UUID

from fastapi import Depends, APIRouter, HTTPException, Response, status

from agnostic.core import schemas_v1, dal_v1

router = APIRouter(tags=['Test Runs'])


@router.post('/projects/{project_id}/test-runs', status_code=status.HTTP_201_CREATED)
async def create_test_run(test_run: schemas_v1.TestRun, project_id: UUID,
                          response: Response, test_runs: dal_v1.TestRuns = Depends(dal_v1.get_test_runs)):
    test_run.project_id = project_id
    try:
        test_run_id = await test_runs.create(test_run)
        response.headers.append('Location', f'/projects/{project_id}/test-runs/{test_run_id}')
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


@router.put('/projects/{project_id}/test-runs/{test_run_id}')
async def update_test_run(test_run: schemas_v1.TestRun, project_id: UUID, test_run_id: UUID,
                          response: Response, test_runs: dal_v1.TestRuns = Depends(dal_v1.get_test_runs)):
    test_run.id = test_run_id
    test_run.project_id = project_id

    try:
        await test_runs.update(test_run)
    except dal_v1.NotFoundError:
        try:
            await test_runs.create(test_run)
            response.status_code = status.HTTP_201_CREATED
            response.headers.append('Location', f'/projects/{project_id}/test-runs/{test_run.id}')
        except (dal_v1.DuplicateError, dal_v1.ForeignKeyError) as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                str(e)
            )


@router.patch('/projects/{project_id}/test-runs/{test_run_id}')
async def update_test_run_fields(test_run: schemas_v1.TestRun, project_id: UUID, test_run_id: UUID,
                                 test_runs: dal_v1.TestRuns = Depends(dal_v1.get_test_runs)):
    test_run.id = test_run_id
    test_run.project_id = project_id
    try:
        await test_runs.update(test_run, exclude_unset=True)
    except dal_v1.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.post('/projects/{project_id}/test-runs/{test_run_id}/start')
async def start_test_run(project_id: UUID, test_run_id: UUID,
                         test_run: schemas_v1.TestRun, test_runs: dal_v1.TestRuns = Depends(dal_v1.get_test_runs)):
    try:
        await test_runs.update(
            schemas_v1.TestRun(id=test_run_id, start=test_run.start or datetime.datetime.utcnow()),
            exclude_unset=True
        )
    except dal_v1.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.post('/projects/{project_id}/test-runs/{test_run_id}/finish')
async def finish_test_run(project_id: UUID, test_run_id: UUID,
                          test_run: schemas_v1.TestRun, test_runs:dal_v1. TestRuns = Depends(dal_v1.get_test_runs)):
    try:
        await test_runs.update(
            schemas_v1.TestRun(id=test_run_id, finish=test_run.finish or datetime.datetime.utcnow()),
            exclude_unset=True
        )
    except dal_v1.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.post('/projects/{project_id}/test-runs/{test_run_id}/heartbeat')
async def update_test_run_heartbeat(project_id: UUID, test_run_id: UUID,
                                    test_run: schemas_v1.TestRun, test_runs: dal_v1.TestRuns = Depends(dal_v1.get_test_runs)):
    try:
        await test_runs.update(
            schemas_v1.TestRun(id=test_run_id, heartbeat=test_run.heartbeat or datetime.datetime.utcnow()),
            exclude_unset=True
        )
    except dal_v1.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.post('/projects/{project_id}/test-runs/{test_run_id}/property')
async def add_test_run_property(project_id: UUID, test_run_id: UUID,
                                prop: schemas_v1.KeyValue, test_runs: dal_v1.TestRuns = Depends(dal_v1.get_test_runs)):
    try:
        test_run = await test_runs.get(test_run_id)
        if not test_run.properties:
            test_run.properties = {}
        test_run.properties.update({prop.key: prop.value})
        await test_runs.update(test_run)
    except dal_v1.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.get('/projects/{project_id}/test-runs/{test_run_id}', response_model=schemas_v1.TestRun)
async def get_test_run(project_id: UUID, test_run_id: UUID,
                       test_runs: dal_v1.TestRuns = Depends(dal_v1.get_test_runs)):
    try:
        return await test_runs.get(test_run_id)
    except dal_v1.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.get('/projects/{project_id}/test-runs', response_model=list[schemas_v1.TestRun])
async def get_test_runs(project_id: UUID, test_runs: dal_v1.TestRuns = Depends(dal_v1.get_test_runs)):
    return await test_runs.get_all(project_id)
