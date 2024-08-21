from fasthtml.common import *
from components import (
    backend_requests_status,
    backend_status,
    caches_status,
    database_status,
    frontend_requests_status,
    frontend_status,
    queues_status,
)
import sentry_api

status_app, rt = fast_app()


@status_app.get("/frontend_requests")
async def get_frontend_requests_status():
    return await frontend_requests_status(
        org_data=sentry_api.org_data,
    )


@status_app.get("/backend_requests")
async def get_backend_requests_status():
    return await backend_requests_status(
        org_data=sentry_api.org_data,
    )


@status_app.get("/frontend")
async def get_frontend_status():
    return await frontend_status(
        org_data=sentry_api.org_data,
    )


@status_app.get("/backend")
async def get_backend_status():
    return await backend_status(
        org_data=sentry_api.org_data,
    )


@status_app.get("/caches")
async def get_caches_status():
    return await caches_status(
        org_data=sentry_api.org_data,
    )


@status_app.get("/queues")
async def get_queues_status():
    return await queues_status(
        org_data=sentry_api.org_data,
    )


@status_app.get("/database")
async def get_database_status():
    return await database_status(
        org_data=sentry_api.org_data,
    )
