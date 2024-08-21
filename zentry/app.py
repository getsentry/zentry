import os
from aiohttp_client_cache import CachedSession
from fasthtml.common import *
import sentry_api
import sentry_sdk

from components import (
    backend_requests_state,
    backend_state,
    caches_state,
    database_state,
    footer,
    frontend_requests_state,
    frontend_state,
    queues_state,
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


@app.get("/frontend_requests_state")
async def get_frontend_requests_state():
    return await frontend_requests_state(
        org_data=sentry_api.org_data,
    )


@app.get("/backend_requests_state")
async def get_backend_requests_state():
    return await backend_requests_state(
        org_data=sentry_api.org_data,
    )


@app.get("/frontend_state")
async def get_frontend_state():
    return await frontend_state(
        org_data=sentry_api.org_data,
    )


@app.get("/backend_state")
async def get_backend_state():
    return await backend_state(
        org_data=sentry_api.org_data,
    )


@app.get("/caches_state")
async def get_caches_state():
    return await caches_state(
        org_data=sentry_api.org_data,
    )


@app.get("/queues_state")
async def get_queues_state():
    return await queues_state(
        org_data=sentry_api.org_data,
    )


@app.get("/database_state")
async def get_database_state():
    return await database_state(
        org_data=sentry_api.org_data,
    )


@app.get("/")
async def index():
    await sentry_api.init()
    data = await sentry_api.get_data()

    if sentry_api.TIME_PERIOD_IN_DAYS == 1:
        tagline = Div(f"Today (until now), compared to yesterday.", cls="tagline")
    else:
        tagline = Div(
            f"The last {sentry_api.TIME_PERIOD_IN_DAYS} days, compared to the {sentry_api.TIME_PERIOD_IN_DAYS} days before.",
            cls="tagline",
        )

    return Title("Zentry"), Div(
        Div(
            H1(data["org"]["name"]),
            tagline,
        ),
        Div(
            # Left side of grid
            Div(
                Div(
                    # Frontend Outbound Requests
                    Div(
                        await frontend_requests_state(
                            org_data=sentry_api.org_data,
                            loading=True,
                        ),
                    ),
                    Div(Span("↔"), cls="grid-cell-arrow"),
                    Div(),
                    Div(),
                    # Backend Outbound Requests
                    Div(
                        await backend_requests_state(
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
                        await frontend_state(
                            org_data=sentry_api.org_data,
                            loading=True,
                        ),
                    ),
                    Div(Span("↕"), cls="grid-cell-arrow"),
                    # Backend
                    Div(
                        await backend_state(
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
                        await caches_state(
                            org_data=sentry_api.org_data,
                            loading=True,
                        ),
                    ),
                    # Queues
                    Div(
                        await queues_state(
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
                        await database_state(
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
