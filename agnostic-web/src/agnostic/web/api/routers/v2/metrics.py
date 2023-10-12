import uuid

from fastapi import Depends, APIRouter, HTTPException, Response, Request, Query, status

from agnostic.core import crud
from agnostic.core.schemas import v2 as s

router = APIRouter(tags=["Metrics"], prefix="/metrics")


@router.post(
    "",
    responses={
        status.HTTP_201_CREATED: {
            "headers": {"Location": {"description": "URL of the created metric", "type": "string"}}
        },
        status.HTTP_404_NOT_FOUND: {},
        status.HTTP_409_CONFLICT: {},
    },
    status_code=status.HTTP_201_CREATED,
)
async def create_metric(
    metric: s.MetricCreate,
    request: Request,
    response: Response,
    metrics: crud.Metrics = Depends(crud.get_metrics),
):
    try:
        metric_id = await metrics.create(metric)
        response.headers.append("Location", f"{request.url.path}/{metric_id}")
    except crud.DuplicateError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    except crud.ForeignKeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.put(
    "/{metric_id}",
    responses={
        status.HTTP_201_CREATED: {
            "headers": {"Location": {"description": "URL of the created metric", "type": "string"}}
        },
        status.HTTP_204_NO_CONTENT: {},
        status.HTTP_409_CONFLICT: {},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_metric(
    metric: s.MetricUpdate,
    metric_id: uuid.UUID,
    request: Request,
    response: Response,
    metrics: crud.Metrics = Depends(crud.get_metrics),
):
    try:
        await metrics.update(metric_id, metric)
    except crud.NotFoundError:
        try:
            await metrics.create(
                s.MetricCreate(id=metric_id, **metric.model_dump(exclude_unset=True))
            )
            response.status_code = status.HTTP_201_CREATED
            response.headers.append("Location", f"{request.url.path}/{metric_id}")
        except (crud.DuplicateError, crud.ForeignKeyError) as e:
            raise HTTPException(status.HTTP_409_CONFLICT, str(e))


@router.patch(
    "/{metric_id}",
    responses={
        status.HTTP_204_NO_CONTENT: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def patch_metric(
    metric: s.MetricPatch,
    metric_id: uuid.UUID,
    metrics: crud.Metrics = Depends(crud.get_metrics),
):
    try:
        await metrics.update(metric_id, metric, exclude_unset=True)
    except crud.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.get(
    "/{metric_id}",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_200_OK,
)
async def get_metric(
    metric_id: uuid.UUID, metrics: crud.Metrics = Depends(crud.get_metrics)
) -> s.Metric:
    try:
        return await metrics.get(metric_id)
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
async def get_metrics(
    response: Response,
    test_run_id: uuid.UUID | None = Query(None),
    test_id: uuid.UUID | None = Query(None),
    page: int = Query(1),
    page_size: int = Query(100),
    metrics: crud.Metrics = Depends(crud.get_metrics),
) -> s.Metrics:
    result = await metrics.get_all(test_run_id, test_id, page, page_size)
    response.headers.append("X-Total-Count", str(result.count))
    return result.items
