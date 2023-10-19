import io
import uuid
from typing import Literal

from fastapi import Depends, APIRouter, HTTPException, Response, Request, Query, Body, status
from fastapi.responses import PlainTextResponse, StreamingResponse

from agnostic.core import crud
from agnostic.core.schemas import v2 as s

router = APIRouter(tags=["Logs"], prefix="/logs")


@router.post(
    "",
    responses={
        status.HTTP_201_CREATED: {
            "headers": {"Location": {"description": "URL of the created log", "type": "string"}}
        },
        status.HTTP_404_NOT_FOUND: {},
        status.HTTP_409_CONFLICT: {},
    },
    status_code=status.HTTP_201_CREATED,
)
async def create_log(
    log: s.LogCreate,
    request: Request,
    response: Response,
    logs: crud.Logs = Depends(crud.get_logs),
):
    try:
        log_id = await logs.create(log)
        response.headers.append("Location", f"{request.url.path}/{log_id}")
    except crud.DuplicateError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    except crud.ForeignKeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.put(
    "/{log_id}",
    responses={
        status.HTTP_201_CREATED: {
            "headers": {"Location": {"description": "URL of the created log", "type": "string"}}
        },
        status.HTTP_204_NO_CONTENT: {},
        status.HTTP_409_CONFLICT: {},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_log(
    log: s.LogUpdate,
    log_id: uuid.UUID,
    request: Request,
    response: Response,
    logs: crud.Logs = Depends(crud.get_logs),
):
    try:
        await logs.update(log_id, log)
    except crud.NotFoundError:
        try:
            await logs.create(s.LogCreate(id=log_id, **log.model_dump(exclude_unset=True)))
            response.status_code = status.HTTP_201_CREATED
            response.headers.append("Location", f"{request.url.path}/{log_id}")
        except (crud.DuplicateError, crud.ForeignKeyError) as e:
            raise HTTPException(status.HTTP_409_CONFLICT, str(e))


@router.patch(
    "/{log_id}",
    responses={
        status.HTTP_204_NO_CONTENT: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def patch_log(
    log: s.LogPatch,
    log_id: uuid.UUID,
    logs: crud.Logs = Depends(crud.get_logs),
):
    try:
        await logs.update(log_id, log, exclude_unset=True)
    except crud.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.get(
    "/{log_id}",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_200_OK,
)
async def get_log(
    log_id: uuid.UUID,
    include: list[Literal["body"]] = Query([]),
    logs: crud.Logs = Depends(crud.get_logs),
) -> s.Log:
    try:
        return await logs.get(log_id, include)
    except crud.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.get(
    "/{log_id}/body",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_200_OK,
    response_class=PlainTextResponse,
)
async def get_log_body(
    log_id: uuid.UUID,
    logs: crud.Logs = Depends(crud.get_logs),
) -> str:
    try:
        return await logs.get_body(log_id)
    except crud.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.get(
    "/{log_id}/download",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_200_OK,
    response_class=StreamingResponse,
)
async def download_log(
    log_id: uuid.UUID,
    logs: crud.Logs = Depends(crud.get_logs),
):
    def stream_response(content):
        c = io.BytesIO(content.encode("utf-8"))
        yield from c

    try:
        # TODO: Verify whether calling get_body separately
        #  helps to reduce RAM consumption as the content
        #  won't be kept in the pydantic model
        log = await logs.get(log_id)
        body = await logs.get_body(log_id)
        return StreamingResponse(
            stream_response(body),  # noqa
            media_type="text/plain",
            headers={
                "Content-Disposition": f'attachment;filename={log.name}-{log.start.isoformat(timespec="seconds")}.log',
            },
        )
    except crud.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.post(
    "/{log_id}/append",
    responses={status.HTTP_201_CREATED: {}, status.HTTP_404_NOT_FOUND: {}},
    status_code=status.HTTP_201_CREATED,
)
async def append_log_body(
    log_id: uuid.UUID,
    body: str = Body(..., media_type="text/plain"),
    logs: crud.Logs = Depends(crud.get_logs),
):
    try:
        await logs.append_body(log_id, body)
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
async def get_logs(
    response: Response,
    test_run_id: uuid.UUID | None = Query(None),
    test_id: uuid.UUID | None = Query(None),
    page: int = Query(1),
    page_size: int = Query(100),
    include: list[Literal["body"]] = Query([]),
    logs: crud.Logs = Depends(crud.get_logs),
) -> s.Logs:
    result = await logs.get_all(test_run_id, test_id, page, page_size, include)
    response.headers.append("X-Total-Count", str(result.count))
    return result.items
