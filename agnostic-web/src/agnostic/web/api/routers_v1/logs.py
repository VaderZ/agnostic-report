import io
from uuid import UUID

from fastapi import Depends, APIRouter, HTTPException, Response, status, Query
from fastapi.responses import StreamingResponse

from agnostic.core import schemas_v1, dal_v1

router = APIRouter(tags=['Logs'])


@router.post('/projects/{project_id}/test-runs/{test_run_id}/logs', status_code=status.HTTP_201_CREATED)
async def create_test_run_log(log: schemas_v1.LogCreate, project_id: UUID, test_run_id: UUID,
                              response: Response, logs: dal_v1.Logs = Depends(dal_v1.get_logs)):
    log.test_run_id = test_run_id
    try:
        log_id = await logs.create(log)
        response.headers.append('Location', f'/projects/{project_id}/test-runs/{test_run_id}/logs/{log_id}')
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


@router.put('/projects/{project_id}/test-runs/{test_run_id}/logs/{log_id}')
async def update_test_run_log(log: schemas_v1.Log, project_id: UUID, test_run_id: UUID, log_id: UUID,
                              response: Response, logs: dal_v1.Logs = Depends(dal_v1.get_logs)):
    log.id = log_id
    log.test_run_id = test_run_id
    try:
        await logs.update(log)
    except dal_v1.NotFoundError:
        try:
            await logs.create(schemas_v1.LogCreate.parse_obj(log))
            response.status_code = status.HTTP_201_CREATED
            response.headers.append('Location', f'/projects/{project_id}/test-runs/{test_run_id}/logs/{log_id}')
        except (dal_v1.DuplicateError, dal_v1.ForeignKeyError) as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                str(e)
            )


@router.patch('/projects/{project_id}/test-runs/{test_run_id}/logs/{log_id}')
async def update_test_run_log_fields(log: schemas_v1.Log, project_id: UUID, test_run_id: UUID, log_id: UUID,
                                     logs: dal_v1.Logs = Depends(dal_v1.get_logs)):
    log.id = log_id
    log.test_run_id = test_run_id
    try:
        await logs.update(log, exclude_unset=True)
    except dal_v1.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.patch('/projects/{project_id}/test-runs/{test_run_id}/logs/{log_id}/body')
async def append_test_run_log(body: schemas_v1.StringValue, project_id: UUID, test_run_id: UUID, log_id: UUID,
                              logs: dal_v1.Logs = Depends(dal_v1.get_logs)):
    try:
        await logs.append_body(log_id, body.value)
    except dal_v1.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.get('/projects/{project_id}/test-runs/{test_run_id}/logs', response_model=list[schemas_v1.Log])
async def get_test_run_logs(project_id: UUID, test_run_id: UUID, logs: dal_v1.Logs = Depends(dal_v1.get_logs)):
    return await logs.get_all(test_run_id)


@router.get('/projects/{project_id}/test-runs/{test_run_id}/logs/{log_id}', response_model=schemas_v1.Log)
async def get_test_run_log(project_id: UUID, test_run_id: UUID, log_id: UUID,
                           logs: dal_v1.Logs = Depends(dal_v1.get_logs)):
    try:
        return await logs.get(log_id)
    except dal_v1.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


def stream_response(content):
    c = io.BytesIO(content.encode('utf-8'))
    yield from c


@router.get('/projects/{project_id}/test-runs/{test_run_id}/logs/{log_id}/download')
async def download_test_run_log(project_id: UUID, test_run_id: UUID, log_id: UUID,
                                logs: dal_v1.Logs = Depends(dal_v1.get_logs)):
    try:
        log = await logs.get(log_id)
        # TODO: Fix and re-enable context size header
        return StreamingResponse(
            stream_response(log.body),
            media_type='text/plain',
            headers={
                'Content-Disposition': f'attachment;filename={log.name}-{log.start.isoformat(timespec="seconds")}.log',
                # 'Content-Length': f'{len(log.body)}'
            }
        )
    except dal_v1.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.get('/projects/{project_id}/test-runs/{test_run_id}/logs/{log_id}/body')
async def get_test_run_log_body(
        project_id: UUID,
        test_run_id: UUID,
        log_id: UUID,
        offset: int | None = Query(0),
        limit: int | None = Query(None),
        logs: dal_v1.Logs = Depends(dal_v1.get_logs)
):
    try:
        return await logs.get_body(log_id, offset, limit)
    except dal_v1.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.post('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/logs',
             status_code=status.HTTP_201_CREATED)
async def create_test_log(log: schemas_v1.LogCreate, project_id: UUID, test_run_id: UUID, test_id: UUID,
                          response: Response, logs: dal_v1.Logs = Depends(dal_v1.get_logs)):
    log.test_run_id = test_run_id
    log.test_id = test_id
    try:
        log_id = await logs.create(log)
        response.headers.append('Location',
                                f'/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/logs/{log_id}')
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


@router.put('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/logs/{log_id}')
async def update_test_log(log: schemas_v1.Log, project_id: UUID, test_run_id: UUID, test_id: UUID, log_id: UUID,
                          response: Response, logs: dal_v1.Logs = Depends(dal_v1.get_logs)):
    log.id = log_id
    log.test_run_id = test_run_id
    log.test_id = test_id
    try:
        await logs.update(log)
    except dal_v1.NotFoundError:
        try:
            await logs.create(schemas_v1.LogCreate.parse_obj(log))
            response.status_code = status.HTTP_201_CREATED
            response.headers.append('Location', f'/projects/{project_id}/test-runs/{test_run_id}/logs/{log_id}')
        except (dal_v1.DuplicateError, dal_v1.ForeignKeyError) as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                str(e)
            )


@router.patch('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/logs/{log_id}')
async def update_test_log_fields(log: schemas_v1.Log, project_id: UUID, test_run_id: UUID, test_id: UUID, log_id: UUID,
                                 logs: dal_v1.Logs = Depends(dal_v1.get_logs)):
    log.id = log_id
    log.test_run_id = test_run_id
    log.test_id = test_id
    try:
        await logs.update(log, exclude_unset=True)
    except dal_v1.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.patch('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/logs/{log_id}/body')
async def append_test_log(body: schemas_v1.StringValue, project_id: UUID, test_run_id: UUID, log_id: UUID,
                          logs: dal_v1.Logs = Depends(dal_v1.get_logs)):
    try:
        await logs.append_body(log_id, body.value)
    except dal_v1.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.get('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/logs/{log_id}', response_model=schemas_v1.Log)
async def get_test_log(project_id: UUID, test_run_id: UUID, test_id: UUID, log_id: UUID,
                       logs: dal_v1.Logs = Depends(dal_v1.get_logs)):
    try:
        return await logs.get(log_id)
    except dal_v1.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.get('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/logs', response_model=list[schemas_v1.Log])
async def get_test_logs(project_id: UUID, test_run_id: UUID, test_id: UUID,
                        logs: dal_v1.Logs = Depends(dal_v1.get_logs)):
    return await logs.get_all(test_id)
