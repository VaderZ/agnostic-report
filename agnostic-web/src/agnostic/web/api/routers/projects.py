from uuid import UUID

from fastapi import Depends, APIRouter, HTTPException, Response, status, Request

from agnostic.core import schemas, dal

router = APIRouter(tags=["Projects"], prefix="/projects")


@router.post(
    "",
    responses={
        status.HTTP_201_CREATED: {
            "headers": {"Location": {"description": "URL of the created project", "type": "string"}}
        },
        status.HTTP_409_CONFLICT: {},
    },
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    project: schemas.ProjectCreate,
    response: Response,
    request: Request,
    projects: dal.Projects = Depends(dal.get_projects),
) -> None:
    try:
        project_id = await projects.create(project)
        response.headers.append("Location", f"{request.url.path}/{project_id}")
    except dal.DuplicateError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))


@router.put(
    "/{project_id}",
    responses={
        status.HTTP_201_CREATED: {
            "headers": {"Location": {"description": "URL of the created project", "type": "string"}}
        },
        status.HTTP_204_NO_CONTENT: {},
        status.HTTP_409_CONFLICT: {},
    },
    status_code=status.HTTP_204_NO_CONTENT
)
async def update_project(
    project: schemas.ProjectUpdate,
    project_id: UUID,
    response: Response,
    request: Request,
    projects: dal.Projects = Depends(dal.get_projects),
):
    try:
        await projects.update(
            schemas.Project.model_construct(
                _fields_set=project.model_fields_set, **project.model_dump(), id=project_id
            )
        )
        response.status_code = status.HTTP_204_NO_CONTENT
    except dal.DuplicateError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    except dal.NotFoundError:
        try:
            await projects.create(schemas.Project(**project.model_dump(), id=project_id))
            response.status_code = status.HTTP_201_CREATED
            response.headers.append("Location", str(request.url.path))
        except dal.DuplicateError as e:
            raise HTTPException(status.HTTP_409_CONFLICT, str(e))


@router.patch(
    "/{project_id}",
    responses={
        status.HTTP_204_NO_CONTENT: {},
        status.HTTP_404_NOT_FOUND: {},
        status.HTTP_409_CONFLICT: {},
    },
    status_code=status.HTTP_204_NO_CONTENT
)
async def patch_project(
    project: schemas.ProjectUpdate,
    project_id: UUID,
    projects: dal.Projects = Depends(dal.get_projects),
):
    try:
        await projects.update(
            schemas.Project.model_construct(
                _fields_set=project.model_fields_set, **project.model_dump(), id=project_id
            ),
            exclude_unset=True,
        )
    except dal.DuplicateError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    except dal.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.get(
    "/{project_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {},
    },
)
async def get_project(
    project_id: UUID, projects: dal.Projects = Depends(dal.get_projects)
) -> schemas.Project:
    try:
        project = await projects.get(project_id)
    except dal.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))

    return project


@router.get("")
async def get_projects(projects: dal.Projects = Depends(dal.get_projects)) -> schemas.Projects:
    return schemas.Projects(await projects.get_all())
