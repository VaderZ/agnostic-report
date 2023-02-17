from uuid import UUID

from fastapi import Depends, APIRouter, HTTPException, Response, status

from .. import schemas
from ...db.dal import get_requests, Requests, DuplicateError, ForeignKeyError, NotFoundError

router = APIRouter(tags=['Requests'])


@router.post('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/requests',
             status_code=status.HTTP_201_CREATED)
async def create_request(request: schemas.RequestCreate, project_id: UUID, test_run_id: UUID, test_id: UUID,
                         response: Response, requests: Requests = Depends(get_requests)):
    request.test_run_id = test_run_id
    request.test_id = test_id
    try:
        request_id = await requests.create(request)
        response.headers.append('Location',
                                f'/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/requests/{request_id}')
    except DuplicateError as e:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            str(e)
        )
    except ForeignKeyError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.put('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/requests/{request_id}')
async def update_request(request: schemas.Request, project_id: UUID, test_run_id: UUID, test_id: UUID, request_id: UUID,
                         response: Response, requests: Requests = Depends(get_requests)):
    request.id = request_id
    request.test_run_id = test_run_id
    request.test_id = test_id
    try:
        await requests.update(request)
    except NotFoundError:
        try:
            await requests.create(schemas.RequestCreate.parse_obj(request))
            response.status_code = status.HTTP_201_CREATED
            response.headers.append('Location', f'/projects/{project_id}/test-runs/{test_run_id}/requests/{request_id}')
        except (DuplicateError, ForeignKeyError) as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                str(e)
            )


@router.patch('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/requests/{request_id}')
async def update_request_fields(request: schemas.Request, project_id: UUID, test_run_id: UUID, test_id: UUID, request_id: UUID,
                                requests: Requests = Depends(get_requests)):
    request.id = request_id
    request.test_run_id = test_run_id
    request.test_id = test_id
    try:
        await requests.update(request, exclude_unset=True)
    except NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.get('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/requests/{request_id}', response_model=schemas.Request)
async def get_request(project_id: UUID, test_run_id: UUID, test_id: UUID, request_id: UUID,
                      requests: Requests = Depends(get_requests)):
    try:
        return await requests.get(request_id)
    except NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.get('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/requests', response_model=list[schemas.Request])
async def get_requests(project_id: UUID, test_run_id: UUID, test_id: UUID,
                       requests: Requests = Depends(get_requests)):
    return await requests.get_all(test_id)
