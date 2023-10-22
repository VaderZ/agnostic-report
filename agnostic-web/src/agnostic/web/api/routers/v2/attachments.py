import datetime
import io
import uuid
from typing import Literal

from fastapi import (
    Depends,
    APIRouter,
    HTTPException,
    Response,
    Request,
    Query,
    UploadFile,
    File,
    Form,
    status,
)
from fastapi.responses import StreamingResponse

from agnostic.core import crud
from agnostic.core.schemas import v2 as s

router = APIRouter(tags=["Attachments"], prefix="/attachments")


@router.post(
    "",
    responses={
        status.HTTP_201_CREATED: {
            "headers": {
                "Location": {"description": "URL of the created attachment", "type": "string"}
            }
        },
        status.HTTP_404_NOT_FOUND: {},
        status.HTTP_409_CONFLICT: {},
    },
    status_code=status.HTTP_201_CREATED,
)
async def create_attachment(
    request: Request,
    response: Response,
    id: uuid.UUID | None = Form(None),
    test_run_id: uuid.UUID = Form(...),
    test_id: uuid.UUID | None = Form(None),
    attachment: UploadFile = File(...),
    attachments: crud.Attachments = Depends(crud.get_attachments),
):
    content = await attachment.read()
    record = s.AttachmentCreate(
        id=id,
        test_run_id=test_run_id,
        test_id=test_id,
        timestamp=datetime.datetime.now(datetime.UTC),
        name=attachment.filename,
        mime_type=attachment.content_type,
        size=len(content),
        content=content,
    )
    try:
        attachment_id = await attachments.create(record)
        response.headers.append("Location", f"{request.url.path}/{attachment_id}")
    except crud.DuplicateError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    except crud.ForeignKeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.get(
    "/{attachment_id}",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_200_OK,
)
async def get_attachment(
    attachment_id: uuid.UUID,
    include: list[Literal["content"]] = Query([]),
    attachments: crud.Attachments = Depends(crud.get_attachments),
) -> s.Attachment:
    try:
        return await attachments.get(attachment_id, include)
    except crud.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.get(
    "/{attachment_id}/download",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_200_OK,
    response_class=StreamingResponse,
)
async def download_attachment(
    attachment_id: uuid.UUID,
    attachments: crud.Attachments = Depends(crud.get_attachments),
) -> StreamingResponse:
    def stream_response(content):
        c = io.BytesIO(content)
        yield from c

    try:
        # TODO: Verify whether calling get_content separately
        #  helps to reduce RAM consumption as the content
        #  won't be kept in the pydantic model
        attachment = await attachments.get(attachment_id)
        content = await attachments.get_content(attachment_id)
        return StreamingResponse(
            stream_response(content),  # noqa
            media_type=attachment.mime_type,
            headers={
                "Content-Disposition": f"attachment;filename={attachment.name}",
                "Content-Length": f"{attachment.size}",
            },
        )
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
async def get_attachments(
    response: Response,
    test_run_id: uuid.UUID | None = Query(None),
    test_id: uuid.UUID | None = Query(None),
    page: int = Query(1),
    page_size: int = Query(100),
    include: list[Literal["content"]] = Query([]),
    attachments: crud.Attachments = Depends(crud.get_attachments),
) -> s.Attachments:
    result = await attachments.get_all(test_run_id, test_id, page, page_size, include)
    response.headers.append("X-Total-Count", str(result.count))
    return result.items
