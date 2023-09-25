from fastapi import APIRouter

router = APIRouter(tags=['System'])


@router.get('/ping')
async def ping():
    return {'ping': 'pong!'}
