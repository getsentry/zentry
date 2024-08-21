from fasthtml.common import *
import sentry_api
from components.ui import loading_placeholder, no_data, metric, metric_simple, query
from utils import (
    fmt_duration,
    fmt_percentage,
    fmt_round_2,
    get_score,
)


async def frontend_status(org_data=None, loading=False):
    header = H2(
        "Frontend",
        A(
            "⌕",
            href=f'{org_data["frontend_url"]}/insights/browser/pageloads/?project={org_data["frontend_id"]}',
            title="Dig deeper into the data",
            target="_blank",
        ),
    )

    # If desired, render loading state
    if loading:
        return loading_placeholder(header, "/status/frontend")

    # Load data
    data = await sentry_api.get_frontend_status(
        org_slug=sentry_api.ORG_SLUG,
        project_id=sentry_api.FRONTEND_ID,
        environment=sentry_api.FRONTEND_ENV,
    )
    data_prev = await sentry_api.get_frontend_status(
        org_slug=sentry_api.ORG_SLUG,
        project_id=sentry_api.FRONTEND_ID,
        environment=sentry_api.FRONTEND_ENV,
        preview_time_period=True,
    )

    # If no data, render no data state
    if not data:
        return no_data(header)

    # Render the frontend state
    return Div(
        header,
        Div(
            metric(
                title="Time to First Byte",
                id="ttfb",
                value=data["ttfb"],
                value_prev=data_prev["ttfb"],
                score=get_score("ttfb", data["ttfb"]),
                formatter=fmt_duration,
            ),
            metric(
                title="First Contentful Paint",
                id="fcp",
                value=data["fcp"],
                value_prev=data_prev["fcp"],
                score=get_score("fcp", data["fcp"]),
                formatter=fmt_duration,
            ),
            metric(
                title="Interaction to Next Paint",
                id="inp",
                value=data["inp"],
                value_prev=data_prev["inp"],
                score=get_score("inp", data["inp"]),
                formatter=fmt_duration,
            ),
            cls="body",
        ),
        id="frontend",
        cls="card",
    )


async def backend_status(org_data=None, loading=False):
    header = H2(
        "Backend",
        A(
            "⌕",
            href=f'{org_data["backend_url"]}/performance/?project={org_data["backend_id"]}',
            title="Dig deeper into the data",
            target="_blank",
        ),
    )

    # If desired, render loading state
    if loading:
        return loading_placeholder(header, "/status/backend")

    # Load data
    data = await sentry_api.get_backend_status(
        org_slug=sentry_api.ORG_SLUG,
        project_id=sentry_api.FRONTEND_ID,
        environment=sentry_api.FRONTEND_ENV,
    )
    data_prev = await sentry_api.get_backend_status(
        org_slug=sentry_api.ORG_SLUG,
        project_id=sentry_api.FRONTEND_ID,
        environment=sentry_api.FRONTEND_ENV,
        preview_time_period=True,
    )

    # If no data, render no data state
    if not data:
        return no_data(header)

    # Render the backend state
    return Div(
        header,
        Div(
            metric(
                title="Failure Rate",
                id="failure-rate",
                value=data["failure_rate"],
                value_prev=data_prev["failure_rate"],
                score=get_score("backend_failure_rate", data["failure_rate"]),
                formatter=fmt_percentage,
            ),
            metric(
                title="Apdex",
                id="apdex",
                value=data["apdex"],
                value_prev=data_prev["apdex"],
                score=get_score("inverse_apdex", 1 - data["apdex"]),
                formatter=fmt_round_2,
            ),
            cls="body",
        ),
        id="backend",
        cls="card",
    )


async def requests_status(title, id, org_data=None, loading=False):
    header = H2(
        title,
        A(
            "⌕",
            href=f'{org_data["url"]}/insights/http/?project={org_data["id"]}',
            title="Dig deeper into the data",
            target="_blank",
        ),
    )

    is_frontend = "frontend" in id
    if is_frontend:
        route = "/status/frontend_requests"
    else:
        route = "/status/backend_requests"

    # If desired, render loading state
    if loading:
        return loading_placeholder(header, route)

    # Load data
    if is_frontend:
        data = await sentry_api.get_requests_status(
            org_slug=sentry_api.ORG_SLUG,
            project_id=sentry_api.FRONTEND_ID,
            environment=sentry_api.FRONTEND_ENV,
        )
        data_prev = await sentry_api.get_requests_status(
            org_slug=sentry_api.ORG_SLUG,
            project_id=sentry_api.FRONTEND_ID,
            environment=sentry_api.FRONTEND_ENV,
            preview_time_period=True,
        )
    else:
        data = await sentry_api.get_requests_status(
            org_slug=sentry_api.ORG_SLUG,
            project_id=sentry_api.BACKEND_ID,
            environment=sentry_api.BACKEND_ENV,
        )
        data_prev = await sentry_api.get_requests_status(
            org_slug=sentry_api.ORG_SLUG,
            project_id=sentry_api.BACKEND_ID,
            environment=sentry_api.BACKEND_ENV,
            preview_time_period=True,
        )

    # If no data, render no data state
    if not data:
        return no_data(header)

    # Render the requests state
    failure_rate = (
        data["response_rate_3xx"]
        + data["response_rate_4xx"]
        + data["response_rate_5xx"]
    )

    failure_rate_prev = (
        data_prev["response_rate_3xx"]
        + data_prev["response_rate_4xx"]
        + data_prev["response_rate_5xx"]
    )

    return Div(
        header,
        Div(
            metric(
                title="Failure Rate",
                id="time_avg",
                value=failure_rate,
                value_prev=failure_rate_prev,
                score=get_score("http_failure_rate", failure_rate),
                formatter=fmt_percentage,
            ),
            metric(
                title="Avg Duration",
                id="time_avg",
                value=data["time_avg"],
                value_prev=data_prev["time_avg"],
                score=get_score("http_avg_duration", data["time_avg"]),
                formatter=fmt_duration,
            ),
            cls="body",
        ),
        id=id,
        cls="card",
    )


async def frontend_requests_status(org_data=None, loading=False):
    return await requests_status(
        "Outbound API Requests",
        "frontend-outbound-requests",
        {"url": org_data["frontend_url"], "id": org_data["frontend_id"]},
        loading=loading,
    )


async def backend_requests_status(org_data=None, loading=False):
    return await requests_status(
        "Outbound API Requests",
        "backend-outbound-requests",
        {"url": org_data["backend_url"], "id": org_data["backend_id"]},
        loading=loading,
    )


async def caches_status(org_data=None, loading=False):
    header = H2(
        "Caches",
        A(
            "⌕",
            href=f'{org_data["backend_url"]}/insights/caches/?project={org_data["backend_id"]}',
            title="Dig deeper into the data",
            target="_blank",
        ),
    )

    # If desired, render loading state
    if loading:
        return loading_placeholder(header, "/status/caches")

    # Load data
    data = await sentry_api.get_caches_status(
        org_slug=sentry_api.ORG_SLUG,
        project_id=sentry_api.BACKEND_ID,
        environment=sentry_api.BACKEND_ENV,
    )
    data_prev = await sentry_api.get_caches_status(
        org_slug=sentry_api.ORG_SLUG,
        project_id=sentry_api.BACKEND_ID,
        environment=sentry_api.BACKEND_ENV,
        preview_time_period=True,
    )

    # If no data, render no data state
    if not data:
        return no_data(header)

    # Render the caches state
    return Div(
        header,
        metric(
            title="Cache hit rate",
            id="cahe_hit_rate",
            value=1 - data["miss_rate"],
            value_prev=1 - data_prev["miss_rate"],
            score=get_score("cache_miss_rate", data["miss_rate"]),
            formatter=fmt_percentage,
        ),
        id="cache",
    )


async def queues_status(org_data=None, loading=False):
    header = H2(
        "Queues",
        A(
            "⌕",
            href=f'{org_data["backend_url"]}/insights/queues/?project={org_data["backend_id"]}',
            title="Dig deeper into the data",
            target="_blank",
        ),
    )

    # If desired, render loading state
    if loading:
        return loading_placeholder(header, "/status/queues")

    # Load data
    data = await sentry_api.get_queues_status(
        org_slug=sentry_api.ORG_SLUG,
        project_id=sentry_api.BACKEND_ID,
        environment=sentry_api.BACKEND_ENV,
    )
    data_prev = await sentry_api.get_queues_status(
        org_slug=sentry_api.ORG_SLUG,
        project_id=sentry_api.BACKEND_ID,
        environment=sentry_api.BACKEND_ENV,
        preview_time_period=True,
    )

    # If no data, render no data state
    if not data:
        return no_data(header)

    # Render the queues state
    return Div(
        header,
        Div(
            # TODO: if we add this, the UI looks ugly, so disabling for now
            # metric(
            #     title="Failure Rate",
            #     id="queue_failure_rate",
            #     value=1 - data["success_rate"],
            #     value_prev=1 - data_prev["success_rate"],
            #     score="TODO",
            #     formatter=fmt_percentage,
            # ),
            metric(
                title="Avg Processing Time",
                id="processing_time_avg",
                value=data["processing_time_avg"],
                value_prev=data_prev["processing_time_avg"],
                score=get_score("queue_avg_processing", data["processing_time_avg"]),
                formatter=fmt_duration,
            ),
            metric(
                title="Avg Time in Queue",
                id="time_in_queue_avg",
                value=data["time_in_queue_avg"],
                value_prev=data_prev["time_in_queue_avg"],
                score=get_score("queue_avg_time_in_queue", data["time_in_queue_avg"]),
                formatter=fmt_duration,
            ),
            cls="body",
        ),
        id="queue",
        cls="card",
    )


async def database_status(org_data=None, loading=False):
    header = H2(
        "Database",
        A(
            "⌕",
            href=f'{org_data["backend_url"]}/insights/database/?project={org_data["backend_id"]}',
            title="Dig deeper into the data",
            target="_blank",
        ),
    )

    if loading:
        return loading_placeholder(header, "/status/database")

    # Load data
    data = await sentry_api.get_database_status(
        org_slug=sentry_api.ORG_SLUG,
        project_id=sentry_api.BACKEND_ID,
        environment=sentry_api.BACKEND_ENV,
    )

    # If no data, render no data state
    if len(data) == 0:
        return no_data(header)

    # Render the database state
    output = []
    for item in data:
        output += [
            query(
                item["query"],
                id="query",
                cls="row query",
            ),
            metric_simple(
                value=item["time_avg"],
                id="time_avg",
                formatter=fmt_duration,
                cls="row right",
            ),
            metric_simple(
                value=item["time_total"],
                id="time_total",
                formatter=fmt_duration,
                cls="row right",
            ),
        ]

    return Div(
        header,
        Div(
            Div(
                # Headline
                Div("Query", cls="row-header"),
                Div("Avg Duration", cls="row-header right"),
                Div("Time Spent", cls="row-header right"),
                # Queries
                *output,
                cls="grid-card-list",
            ),
            cls="body",
        ),
        id="database",
        cls="card",
        style="min-height: 400px; height: unset;",
    )
