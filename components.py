from fasthtml.common import *

from utils import fmt_duration, fmt_percentage, fmt_percentage_signed


def metric(title, id, value, value_prev, score, formatter=lambda x: x):
    """
    The card representing one metric.
    """
    change = (value_prev - value) / value_prev

    return Div(
        Div(title, cls="title"),
        Div(formatter(value), cls="value"),
        Div(fmt_percentage_signed(change), cls="change"),
        Div(score, cls="score"),
        id=id,
        cls="metric",
    )


async def frontend_state(data=None, data_prev=None):
    if not data:
        return Div(
            H2("Frontend"),
            P("No data available"),
            id="frontend",
        )

    return Div(
        H2("Frontend"),
        metric(
            title="Web Server Responsiveness (Time to first byte)",
            id="ttfb",
            value=data["ttfb"],
            value_prev=data_prev["ttfb"],
            score="TODO",
            formatter=fmt_duration,
        ),
        metric(
            title="Time the first content takes to render (First Contentful Paint)",
            id="fcp",
            value=data["fcp"],
            value_prev=data_prev["fcp"],
            score="TODO",
            formatter=fmt_duration,
        ),
        metric(
            title="Responsiveness (Interaction to Next Paint)",
            id="inp",
            value=data["inp"],
            value_prev=data_prev["inp"],
            score="TODO",
        ),
        id="frontend",
    )


async def backend_state(data=None, data_prev=None):
    if not data:
        return Div(
            H2("Backend"),
            P("No data available"),
            id="backend",
        )

    return Div(
        H2("Backend"),
        metric(
            title="Failure Rate",
            id="failure-rate",
            value=data["failure_rate"],
            value_prev=data_prev["failure_rate"],
            score="TODO",
            formatter=fmt_percentage,
        ),
        metric(
            title="Apdex",
            id="apdex",
            value=data["apdex"],
            value_prev=data_prev["apdex"],
            score="TODO",
        ),
        id="backend",
    )


async def requests_state(title, id, data=None, data_prev=None):
    if not data:
        return Div(
            H2(title),
            P("No data available"),
            id=id,
        )

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
        H2(title),
        metric(
            title="Average Duration",
            id="time_avg",
            value=data["time_avg"],
            value_prev=data_prev["time_avg"],
            score="TODO",
            formatter=fmt_duration,
        ),
        metric(
            title="Failure Rate",
            id="time_avg",
            value=failure_rate,
            value_prev=failure_rate_prev,
            score="TODO",
            formatter=fmt_percentage,
        ),
        id=id,
    )


async def frontend_requests_state(data=None, data_prev=None):
    return await requests_state(
        "Frontend Outbound Requests",
        "frontend-outbound-requests",
        data,
        data_prev,
    )


async def backend_requests_state(data=None, data_prev=None):
    return await requests_state(
        "Backend Outbound Requests",
        "backend-outbound-requests",
        data,
        data_prev,
    )


async def cache_state(data=None, data_prev=None):
    if not data:
        return Div(
            H2("Cache"),
            P("No data available"),
            id="cache",
        )

    return Div(
        H2("Cache"),
        metric(
            title="Cache hit rate",
            id="cahe_hit_rate",
            value=1 - data["miss_rate"],
            value_prev=1 - data_prev["miss_rate"],
            score="TODO",
            formatter=fmt_percentage,
        ),
        id="cache",
    )


async def queue_state(data=None, data_prev=None):
    if not data:
        return Div(
            H2("Queues"),
            P("No data available"),
            id="queue",
        )

    return Div(
        H2("Queues"),
        metric(
            title="Average processing time",
            id="processing_time_avg",
            value=data["processing_time_avg"],
            value_prev=data_prev["processing_time_avg"],
            score="TODO",
            formatter=fmt_duration,
        ),
        metric(
            title="Average time in queue",
            id="time_in_queue_avg",
            value=data["time_in_queue_avg"],
            value_prev=data_prev["time_in_queue_avg"],
            score="TODO",
            formatter=fmt_duration,
        ),
        metric(
            title="Failure Rate",
            id="queue_failure_rate",
            value=1 - data["success_rate"],
            value_prev=1 - data_prev["success_rate"],
            score="TODO",
            formatter=fmt_percentage,
        ),
        id="queue",
    )


async def database_state(data=None, data_prev=None):
    output = []
    for item in data:
        output.append(
            Div(
                Div(item["query"], id="query"),
                Div("Time avg", item["time_avg"], id="time_avg"),
                Div("Time total", item["time_total"], id="time_total"),
                Div("Time percentage", item["time_percentage"], id="time_percentage"),
                id="database-query",
            )
        )

    return Div(
        H2("Database"),
        *output,
        id="database",
    )
