import uuid

from fastapi import Depends, APIRouter, HTTPException, Response, Query, status

from agnostic.core import crud
from agnostic.core.schemas import v2 as s

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
    project: s.ProjectCreate,
    response: Response,
    projects: crud.Projects = Depends(crud.get_projects),
):
    try:
        project_id = await projects.create(project)
        response.headers.append("Location", f"/projects/{project_id}")
    except crud.DuplicateError as e:
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
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_project(
    project: s.ProjectUpdate,
    project_id: uuid.UUID,
    response: Response,
    projects: crud.Projects = Depends(crud.get_projects),
):
    try:
        await projects.update(project_id, project)
    except crud.DuplicateError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    except crud.NotFoundError:
        try:
            await projects.create(project)
            response.status_code = status.HTTP_201_CREATED
            response.headers.append("Location", f"/projects/{project_id}")
        except crud.DuplicateError as e:
            raise HTTPException(status.HTTP_409_CONFLICT, str(e))


@router.patch(
    "/{project_id}",
    responses={
        status.HTTP_201_CREATED: {
            "headers": {"Location": {"description": "URL of the created project", "type": "string"}}
        },
        status.HTTP_204_NO_CONTENT: {},
        status.HTTP_409_CONFLICT: {},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def patch_project(
    project: s.ProjectPatch,
    project_id: uuid.UUID,
    projects: crud.Projects = Depends(crud.get_projects),
):
    project.id = project_id
    try:
        _project = await projects.update(project_id, project, exclude_unset=True)
    except crud.DuplicateError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    except crud.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.get(
    "/{project_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {},
    },
)
async def get_project(
    project_id: uuid.UUID, projects: crud.Projects = Depends(crud.get_projects)
) -> s.Project:
    try:
        project = await projects.get(project_id)
    except crud.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))

    return project


@router.get(
    "",
    responses={
        status.HTTP_200_OK: {
            "headers": {
                "X-Total-Count": {"description": "Total number of projects", "type": "int"}
            }
        },
    },
)
async def get_projects(
    response: Response,
    page: int = Query(1),
    page_size: int = Query(100),
    projects: crud.Projects = Depends(crud.get_projects),
) -> s.Projects:
    projects = await projects.get_all(page, page_size)
    response.headers.append("X-Total-Count", str(projects.count))
    return projects.items
