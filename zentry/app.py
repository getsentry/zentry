import os

from aiohttp_client_cache import CachedSession, RedisBackend

from fasthtml.common import *

import sentry_api
import sentry_sdk

from components import (
    backend_requests_state,
    backend_state,
    cache_state,
    database_state,
    footer,
    frontend_requests_state,
    frontend_state,
    queue_state,
)

REDIS_URL = os.environ.get("ZENTRY_REDIS_URL", "redis://localhost:6379")

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    traces_sample_rate=1.0,
    # debug=True,
)

app, rt = fast_app(
    pico=False,
    hdrs=(
        Link(rel="stylesheet", href="assets/rest.css", type="text/css"),
        Link(rel="stylesheet", href="assets/zentry.css", type="text/css"),
        MarkdownJS(),
        Link(
            rel="icon",
            type="image/png",
            href="https://s1.sentry-cdn.com/_static/0c41bcfa548dfc7d27d582cd94b34af7/sentry/images/favicon.png",
        ),
    ),
)


async def header(title):
    return Div(
        Li(A("Issues", href="/"), A("State of the System", href="/state")),
        Titled(title),
        id="header",
    )


@app.get("/")
async def index():
    backend = RedisBackend(
        cache_name="z2",
        address=REDIS_URL,
        expire_after=60 * 60,
        allowed_codes=(200,),
        allowed_methods=("GET",),
        include_headers=True,
    )
    async with CachedSession(cache=backend) as client:
        sentry_api.client = client
        data = await sentry_api.get_data()

        return Title("Zentry"), Div(
            Div(
                H1(data["org"]["name"]),
            ),
            Div(
                # Left side of grid
                Div(
                    Div(
                        # Frontend Outbound Requests
                        Div(
                            await frontend_requests_state(
                                data["frontend_requests"],
                                data["frontend_requests_prev"],
                                data["org"],
                            ),
                        ),
                        Div(Span("↔"), cls="grid-cell-arrow"),
                        Div(),
                        Div(),
                        # Backend Outbound Requests
                        Div(
                            await backend_requests_state(
                                data["backend_requests"],
                                data["backend_requests_prev"],
                                data["org"],
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
                                data["frontend"],
                                data["frontend_prev"],
                                data["org"],
                            ),
                        ),
                        Div(Span("↕"), cls="grid-cell-arrow"),
                        # Backend
                        Div(
                            await backend_state(
                                data["backend"], data["backend_prev"], data["org"]
                            ),
                        ),
                        cls="grid-right-single",
                    ),
                    Div(
                        Div(Span("↕"), cls="grid-cell-arrow"),
                        Div(Span("↕"), cls="grid-cell-arrow"),
                        # Caches
                        Div(
                            await cache_state(
                                data["cache"], data["cache_prev"], data["org"]
                            ),
                        ),
                        # Queues
                        Div(
                            await queue_state(
                                data["queue"], data["queue_prev"], data["org"]
                            ),
                        ),
                        Div(Span("↕"), cls="grid-cell-arrow"),
                        Div(Span("↕"), cls="grid-cell-arrow"),
                        cls="grid-right-double",
                    ),
                    Div(
                        # Database
                        Div(
                            await database_state(data["database"], data["org"]),
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
