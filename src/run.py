import uvicorn
from agnostic_report import config

if __name__ == '__main__':
    uvicorn.run(
        'agnostic_report:app',
        port=config.web_port,
        host=config.web_host,
        reload=True,
    )
