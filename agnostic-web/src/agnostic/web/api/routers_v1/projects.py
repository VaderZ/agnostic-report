from uuid import UUID

from fastapi import Depends, APIRouter, HTTPException, Response, status

from agnostic.core import schemas_v1, dal_v1

router = APIRouter(tags=['Projects'])


@router.post('/projects', status_code=status.HTTP_201_CREATED)
async def create_project(project: schemas_v1.ProjectCreate, response: Response,
                         projects: dal_v1.Projects = Depends(dal_v1.get_projects)):
    try:
        project_id = await projects.create(project)
        response.headers.append('Location', f'/projects/{project_id}')
    except dal_v1.DuplicateError as e:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            str(e)
        )


@router.put('/projects/{project_id}')
async def update_project(project: schemas_v1.ProjectCreate, project_id: UUID,
                         response: Response, projects: dal_v1.Projects = Depends(dal_v1.get_projects)):
    project.id = project_id
    try:
        await projects.update(project)
    except dal_v1.DuplicateError as e:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            str(e)
        )
    except dal_v1.NotFoundError:
        try:
            await projects.create(project)
            response.status_code = status.HTTP_201_CREATED
            response.headers.append('Location', f'/projects/{project.id}')
        except dal_v1.DuplicateError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                str(e)
            )


@router.patch('/projects/{project_id}')
async def update_project_fields(project: schemas_v1.Project, project_id: UUID,
                                projects: dal_v1.Projects = Depends(dal_v1.get_projects)):
    print(project)
    project.id = project_id
    try:
        _project = await projects.update(project, exclude_unset=True)
    except dal_v1.DuplicateError as e:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            str(e)
        )
    except dal_v1.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )


@router.get('/projects/{project_id}', response_model=schemas_v1.Project)
async def get_project(project_id: UUID, projects: dal_v1.Projects = Depends(dal_v1.get_projects)):
    try:
        project = await projects.get(project_id)
    except dal_v1.NotFoundError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            str(e)
        )

    return project


@router.get('/projects', response_model=list[schemas_v1.Project])
async def get_projects(projects: dal_v1.Projects = Depends(dal_v1.get_projects)):
    return await projects.get_all()
