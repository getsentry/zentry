import os
from aiohttp_client_cache import CachedSession
from fasthtml.common import *
import sentry_api
import sentry_sdk

from components import (
    backend_requests_status,
    backend_status,
    caches_status,
    database_status,
    footer,
    frontend_requests_status,
    frontend_status,
    queues_status,
)

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    traces_sample_rate=1.0,
    # debug=True,
)

headers = (
    Link(rel="stylesheet", href="assets/reset.css", type="text/css"),
    Link(rel="stylesheet", href="assets/zentry.css", type="text/css"),
    MarkdownJS(),
    Link(
        rel="icon",
        type="image/png",
        href="https://s1.sentry-cdn.com/_static/0c41bcfa548dfc7d27d582cd94b34af7/sentry/images/favicon.png",
    ),
)


app, rt = fast_app(
    pico=False,
    hdrs=headers,
)


@app.get("/status/frontend_requests")
async def get_frontend_requests_status():
    return await frontend_requests_status(
        org_data=sentry_api.org_data,
    )


@app.get("/status/backend_requests")
async def get_backend_requests_status():
    return await backend_requests_status(
        org_data=sentry_api.org_data,
    )


@app.get("/status/frontend")
async def get_frontend_status():
    return await frontend_status(
        org_data=sentry_api.org_data,
    )


@app.get("/status/backend")
async def get_backend_status():
    return await backend_status(
        org_data=sentry_api.org_data,
    )


@app.get("/status/caches")
async def get_caches_status():
    return await caches_status(
        org_data=sentry_api.org_data,
    )


@app.get("/status/queues")
async def get_queues_status():
    return await queues_status(
        org_data=sentry_api.org_data,
    )


@app.get("/status/database")
async def get_database_status():
    return await database_status(
        org_data=sentry_api.org_data,
    )


@app.get("/")
async def index():
    await sentry_api.init()

    if sentry_api.TIME_PERIOD_IN_DAYS == 1:
        tagline = Div(f"Today (until now), compared to yesterday.", cls="tagline")
    else:
        tagline = Div(
            f"The last {sentry_api.TIME_PERIOD_IN_DAYS} days, compared to the {sentry_api.TIME_PERIOD_IN_DAYS} days before.",
            cls="tagline",
        )

    return Title("Zentry"), Div(
        Div(
            H1(sentry_api.org_data["name"]),
            tagline,
        ),
        Div(
            # Left side of grid
            Div(
                Div(
                    # Frontend Outbound Requests
                    Div(
                        await frontend_requests_status(
                            org_data=sentry_api.org_data,
                            loading=True,
                        ),
                    ),
                    Div(Span("↔"), cls="grid-cell-arrow"),
                    Div(),
                    Div(),
                    # Backend Outbound Requests
                    Div(
                        await backend_requests_status(
                            org_data=sentry_api.org_data,
                            loading=True,
                        ),
                    ),
                    Div(Span("↔"), cls="grid-cell-arrow"),
                    cls="grid-left",
                ),
            ),
            # Right side of grid
            Div(
                Div(
                    # Frontend
                    Div(
                        await frontend_status(
                            org_data=sentry_api.org_data,
                            loading=True,
                        ),
                    ),
                    Div(Span("↕"), cls="grid-cell-arrow"),
                    # Backend
                    Div(
                        await backend_status(
                            org_data=sentry_api.org_data,
                            loading=True,
                        ),
                    ),
                    cls="grid-right-single",
                ),
                Div(
                    Div(Span("↕"), cls="grid-cell-arrow"),
                    Div(Span("↕"), cls="grid-cell-arrow"),
                    # Caches
                    Div(
                        await caches_status(
                            org_data=sentry_api.org_data,
                            loading=True,
                        ),
                    ),
                    # Queues
                    Div(
                        await queues_status(
                            org_data=sentry_api.org_data,
                            loading=True,
                        ),
                    ),
                    Div(Span("↕"), cls="grid-cell-arrow"),
                    Div(Span("↕"), cls="grid-cell-arrow"),
                    cls="grid-right-double",
                ),
                Div(
                    # Database
                    Div(
                        await database_status(
                            org_data=sentry_api.org_data,
                            loading=True,
                        ),
                    ),
                    cls="grid-right-single",
                ),
            ),
            cls="grid-wrapper",
        ),
        footer(),
        cls="wrapper",
    )


serve()
