from uuid import UUID

from fastapi import Depends, APIRouter, HTTPException, Response, status

from agnostic.core import schemas_v1, dal_v1

router = APIRouter(tags=['Progress'])


@router.post('/projects/{project_id}/test-runs/{test_run_id}/progress', status_code=status.HTTP_201_CREATED)
async def create_progress_record(progress: schemas_v1.ProgressCreate, project_id: UUID, test_run_id: UUID,
                                 response: Response, progresses: dal_v1.Progress = Depends(dal_v1.get_progress)):
    progress.test_run_id = test_run_id
    try:
        record_id = await progresses.create(progress)
        response.headers.append('Location', f'/projects/{project_id}/test-runs/{test_run_id}/progress/{record_id}')
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


@router.put('/projects/{project_id}/test-runs/{test_run_id}/progress/{record_id}')
async def update_progress_record(progress: schemas_v1.Progress, project_id: UUID, test_run_id: UUID, record_id: UUID,
                                 response: Response, progresses: dal_v1.Progress = Depends(dal_v1.get_progress)):
    progress.id = record_id
    progress.test_run_id = test_run_id
    try:
        await progresses.update(progress)
    except dal_v1.NotFoundError:
        try:
            await progresses.create(schemas_v1.ProgressCreate.parse_obj(progress))
            response.status_code = status.HTTP_201_CREATED
            response.headers.append('Location', f'/projects/{project_id}/test-runs/{test_run_id}/progress/{record_id}')
        except (dal_v1.DuplicateError, dal_v1.ForeignKeyError) as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                str(e)
            )


@router.patch('/projects/{project_id}/test-runs/{test_run_id}/progress/{record_id}')
async def update_progress_record_fields(progress: schemas_v1.Progress, project_id: UUID, test_run_id: UUID, record_id: UUID,
                                        progresses: dal_v1.Progress = Depends(dal_v1.get_progress)):
    progress.id = record_id
    progress.test_run_id = test_run_id
    try:
        await progresses.update(progress, exclude_unset=True)
    except dal_v1.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.get('/projects/{project_id}/test-runs/{test_run_id}/progress/{record_id}', response_model=schemas_v1.Progress)
async def get_progress_record(project_id: UUID, test_run_id: UUID, test_id: UUID, record_id:UUID,
                              progresses: dal_v1.Progress = Depends(dal_v1.get_progress)):
    try:
        return await progresses.get(record_id)
    except dal_v1.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.get('/projects/{project_id}/test-runs/{test_run_id}/progress', response_model=list[schemas_v1.Progress])
async def get_progress_records(project_id: UUID, test_run_id: UUID, test_id: UUID,
                               progresses: dal_v1.Progress = Depends(dal_v1.get_progress)):
    return await progresses.get_all(test_run_id)
