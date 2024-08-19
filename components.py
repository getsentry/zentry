from fasthtml.common import *


def frontend_state(data=None):
    if not data:
        return Div(
            H2("Frontend"),
            P("No data available"),
            id="frontend",
        )

    return Div(
        H2("Frontend"),
        P("Web Server Responsiveness (Time to first byte): ", data["ttfb"]),
        P(
            "Time the first content takes to render (First Contentful Paint): ",
            data["fcp"],
        ),
        P("Responsiveness (Interaction to Next Paint): ", data["inp"]),
        id="frontend",
    )


def backend_state(data=None):
    if not data:
        return Div(
            H2("Backend"),
            P("No data available"),
            id="backend",
        )

    return Div(
        H2("Backend"),
        P("Failure Rate: ", data["failure_rate"]),
        P("Apdex: ", data["apdex"]),
        id="backend",
    )


def requests_state(title, id, data=None):
    if not data:
        return Div(
            H2(title),
            P("No data available"),
            id=id,
        )

    return Div(
        H2(title),
        P("Average Duration: ", data["time_avg"]),
        P(
            "Failure Rate: ",
            data["response_rate_3xx"]
            + data["response_rate_4xx"]
            + data["response_rate_5xx"],
        ),
        id=id,
    )


def frontend_requests_state(data=None):
    return requests_state(
        "Frontend Outbound Requests", "frontend-outbound-requests", data
    )


def backend_requests_state(data=None):
    return requests_state(
        "Backend Outbound Requests", "backend-outbound-requests", data
    )


def cache_state(data=None):
    if not data:
        return Div(
            H2("Cache"),
            P("No data available"),
            id="cache",
        )

    return Div(
        H2("Cache"),
        P("Cache hit rate: ", 1 - data["miss_rate"]),
        id="cache",
    )


def queue_state(data=None):
    if not data:
        return Div(
            H2("Queues"),
            P("No data available"),
            id="queue",
        )

    return Div(
        H2("Queues"),
        P("Average processing time: ", data["processing_time_avg"]),
        P("Average time in queue: ", data["time_in_queue_avg"]),
        P("Failure Rate: ", 1 - data["success_rate"]),
        id="queue",
    )


def database_state(data=None):
    output = []
    for item in data:
        output.append(
            Div(
                P("Query:", item["query"]),
                P("Time avg:", item["time_avg"]),
                P("Time total::", item["time_total"]),
                P("Time percentage:", item["time_percentage"]),
            )
        )

    return Div(
        H2("Database"),
        *output,
        id="database",
    )
