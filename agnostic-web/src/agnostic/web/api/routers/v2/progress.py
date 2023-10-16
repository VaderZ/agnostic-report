import uuid

from fastapi import Depends, APIRouter, HTTPException, Response, Request, Query, status

from agnostic.core import crud
from agnostic.core.schemas import v2 as s

router = APIRouter(tags=["Progress"], prefix="/progress")


@router.post(
    "",
    responses={
        status.HTTP_201_CREATED: {
            "headers": {
                "Location": {"description": "URL of the created progress record", "type": "string"}
            }
        },
        status.HTTP_404_NOT_FOUND: {},
        status.HTTP_409_CONFLICT: {},
    },
    status_code=status.HTTP_201_CREATED,
)
async def create_progress(
    progress: s.ProgressCreate,
    request: Request,
    response: Response,
    progresses: crud.Progress = Depends(crud.get_progress),
):
    try:
        progress_id = await progresses.create(progress)
        response.headers.append("Location", f"{request.url.path}/{progress_id}")
    except crud.DuplicateError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    except crud.ForeignKeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.put(
    "/{progress_id}",
    responses={
        status.HTTP_201_CREATED: {
            "headers": {
                "Location": {"description": "URL of the created progress record", "type": "string"}
            }
        },
        status.HTTP_204_NO_CONTENT: {},
        status.HTTP_409_CONFLICT: {},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_progress(
    progress: s.ProgressUpdate,
    progress_id: uuid.UUID,
    request: Request,
    response: Response,
    progresses: crud.Progress = Depends(crud.get_progress),
):
    try:
        await progresses.update(progress_id, progress)
    except crud.NotFoundError:
        try:
            await progresses.create(
                s.Progress(id=progress_id, **progress.model_dump(exclude_unset=True))
            )
            response.status_code = status.HTTP_201_CREATED
            response.headers.append("Location", f"{request.url.path}/{progress_id}")
        except (crud.DuplicateError, crud.ForeignKeyError) as e:
            raise HTTPException(status.HTTP_409_CONFLICT, str(e))


@router.patch(
    "/{progress_id}",
    responses={
        status.HTTP_204_NO_CONTENT: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def patch_progress(
    progress: s.ProgressPatch,
    progress_id: uuid.UUID,
    progresses: crud.Progress = Depends(crud.get_progress),
):
    try:
        await progresses.update(progress_id, progress, exclude_unset=True)
    except crud.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.get(
    "/{progress_id}",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_200_OK,
)
async def get_progress(
    progress_id: uuid.UUID, progresses: crud.Progress = Depends(crud.get_progress)
) -> s.Progress:
    try:
        return await progresses.get(progress_id)
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
async def get_progresses(
    response: Response,
    test_run_id: uuid.UUID | None = Query(None),
    test_id: uuid.UUID | None = Query(None),
    page: int = Query(1),
    page_size: int = Query(100),
    progresses: crud.Progress = Depends(crud.get_progress),
) -> s.Progresses:
    result = await progresses.get_all(test_run_id, test_id, page, page_size)
    response.headers.append("X-Total-Count", str(result.count))
    return result.items
