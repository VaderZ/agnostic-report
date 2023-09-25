from uuid import UUID

from fastapi import Depends, APIRouter, HTTPException, Response, status

from agnostic.core import schemas_v1, dal_v1

router = APIRouter(tags=['Requests'])


@router.post('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/requests',
             status_code=status.HTTP_201_CREATED)
async def create_request(request: schemas_v1.RequestCreate, project_id: UUID, test_run_id: UUID, test_id: UUID,
                         response: Response, requests: dal_v1.Requests = Depends(dal_v1.get_requests)):
    request.test_run_id = test_run_id
    request.test_id = test_id
    try:
        request_id = await requests.create(request)
        response.headers.append('Location',
                                f'/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/requests/{request_id}')
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


@router.put('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/requests/{request_id}')
async def update_request(request: schemas_v1.Request, project_id: UUID, test_run_id: UUID, test_id: UUID, request_id: UUID,
                         response: Response, requests: dal_v1.Requests = Depends(dal_v1.get_requests)):
    request.id = request_id
    request.test_run_id = test_run_id
    request.test_id = test_id
    try:
        await requests.update(request)
    except dal_v1.NotFoundError:
        try:
            await requests.create(schemas_v1.RequestCreate.parse_obj(request))
            response.status_code = status.HTTP_201_CREATED
            response.headers.append('Location', f'/projects/{project_id}/test-runs/{test_run_id}/requests/{request_id}')
        except (dal_v1.DuplicateError, dal_v1.ForeignKeyError) as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                str(e)
            )


@router.patch('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/requests/{request_id}')
async def update_request_fields(request: schemas_v1.Request, project_id: UUID, test_run_id: UUID, test_id: UUID, request_id: UUID,
                                requests: dal_v1.Requests = Depends(dal_v1.get_requests)):
    request.id = request_id
    request.test_run_id = test_run_id
    request.test_id = test_id
    try:
        await requests.update(request, exclude_unset=True)
    except dal_v1.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.get('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/requests/{request_id}', response_model=schemas_v1.Request)
async def get_request(project_id: UUID, test_run_id: UUID, test_id: UUID, request_id: UUID,
                      requests: dal_v1.Requests = Depends(dal_v1.get_requests)):
    try:
        return await requests.get(request_id)
    except dal_v1.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.get('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/requests', response_model=list[schemas_v1.Request])
async def get_requests(project_id: UUID, test_run_id: UUID, test_id: UUID,
                       requests: dal_v1.Requests = Depends(dal_v1.get_requests)):
    return await requests.get_all(test_id)
