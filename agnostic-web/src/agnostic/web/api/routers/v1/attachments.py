import datetime
import io
from uuid import UUID

from fastapi import Depends, APIRouter, HTTPException, Response, status, UploadFile, File
from fastapi.responses import StreamingResponse

from agnostic.core import schemas, dal

router = APIRouter(tags=['Attachments'])


@router.post('/projects/{project_id}/test-runs/{test_run_id}/attachments', status_code=status.HTTP_201_CREATED)
async def create_test_run_attachment(project_id: UUID, test_run_id: UUID, response: Response,
                                     attachment: UploadFile = File(...),
                                     attachments: dal.Attachments = Depends(dal.get_attachments)):
    content = await attachment.read()
    record = schemas.v1.AttachmentCreate(
        test_run_id=test_run_id,
        timestamp=datetime.datetime.utcnow(),
        name=attachment.filename,
        mime_type=attachment.content_type,
        size=len(content),
        content=content
    )
    try:
        attachment_id = await attachments.create(record)
        response.headers.append(
            'Location',
            f'/projects/{project_id}/test-runs/{test_run_id}/attachments/{attachment_id}'
        )
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


@router.post('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/attachments',
             status_code=status.HTTP_201_CREATED)
async def create_test_attachment(project_id: UUID, test_run_id: UUID, test_id: UUID,
                                 response: Response, attachment: UploadFile = File(...),
                                 attachments: dal.Attachments = Depends(dal.get_attachments)):
    content = await attachment.read()
    record = schemas.v1.AttachmentCreate(
        test_run_id=test_run_id,
        test_id=test_id,
        timestamp=datetime.datetime.utcnow(),
        name=attachment.filename,
        mime_type=attachment.content_type,
        size=len(content),
        content=content
    )
    try:
        attachment_id = await attachments.create(record)
        response.headers.append(
            'Location',
            f'/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/attachments/{attachment_id}'
        )
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


def stream_response(content):
    c = io.BytesIO(content)
    yield from c


@router.get('/projects/{project_id}/test-runs/{test_run_id}/attachments/{attachment_id}')
async def get_test_run_attachment(project_id: UUID, test_run_id: UUID, attachment_id: UUID,
                                  attachments: dal.Attachments = Depends(dal.get_attachments)):
    try:
        attachment = await attachments.get(attachment_id)
        return StreamingResponse(
            stream_response(attachment.content),
            media_type=attachment.mime_type,
            headers={
                'Content-Disposition': f'attachment;filename={attachment.name}',
                'Content-Length': f'{attachment.size}'
            }
        )
    except dal.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.get('/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}/attachments/{attachment_id}')
async def get_test_attachment(project_id: UUID, test_run_id: UUID, test_id: UUID, attachment_id: UUID,
                              attachments: dal.Attachments = Depends(dal.get_attachments)):
    try:
        attachment = await attachments.get(attachment_id)
        return StreamingResponse(
            stream_response(attachment.content),
            media_type=attachment.mime_type,
            headers={
                'Content-Disposition': f'attachment;filename={attachment.name}',
                'Content-Length': f'{attachment.size}'
            }
        )
    except dal.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )
