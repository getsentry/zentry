import datetime
import os
from aiohttp_client_cache import CachedSession, RedisBackend


TIME_PERIOD_IN_DAYS = 3
REFERRER = os.environ.get("REFERRER", "zentry")
API_BASE_URL = os.environ.get("SENTRY_API_BASE_URL", "https://sentry.io/api/0")
REDIS_URL = os.environ.get("ZENTRY_REDIS_URL", "redis://localhost:6379")

API_AUTH_TOKEN = os.environ.get("SENTRY_API_AUTH_TOKEN")
if not API_AUTH_TOKEN:
    raise ValueError(
        "Please set the SENTRY_API_AUTH_TOKEN environment variable. (See https://github.com/getsentry/zentry/blob/main/README.md)"
    )

ORG_SLUG = os.environ.get("SENTRY_ORG_SLUG")
if not ORG_SLUG:
    raise ValueError(
        "Please set the SENTRY_ORG_SLUG environment variable. (See https://github.com/getsentry/zentry/blob/main/README.md)"
    )

FRONTEND_ID = os.environ.get("SENTRY_FRONTEND_PROJECT_ID")
if not FRONTEND_ID:
    raise ValueError(
        "Please set the SENTRY_FRONTEND_PROJECT_ID environment variable. (See https://github.com/getsentry/zentry/blob/main/README.md)"
    )

FRONTEND_ENV = os.environ.get("SENTRY_FRONTEND_ENVIRONMENT")
if not FRONTEND_ENV:
    raise ValueError(
        "Please set the SENTRY_FRONTEND_ENVIRONMENT environment variable. (See https://github.com/getsentry/zentry/blob/main/README.md)"
    )

BACKEND_ID = os.environ.get("SENTRY_BACKEND_PROJECT_ID")
if not BACKEND_ID:
    raise ValueError(
        "Please set the SENTRY_BACKEND_PROJECT_ID environment variable. (See https://github.com/getsentry/zentry/blob/main/README.md)"
    )

BACKEND_ENV = os.environ.get("SENTRY_BACKEND_ENVIRONMENT")
if not BACKEND_ENV:
    raise ValueError(
        "Please set the SENTRY_BACKEND_ENVIRONMENT environment variable. (See https://github.com/getsentry/zentry/blob/main/README.md)"
    )


org_data = None
cache_backend = None


async def init():
    global cache_backend
    cache_backend = RedisBackend(
        cache_name="zentry_http_cache",
        address=REDIS_URL,
        expire_after=60 * 60,
        allowed_codes=(200,),
        allowed_methods=("GET",),
        include_headers=True,
    )

    global org_data
    org_data = await get_org_data()


def _get_time_period(preview_time_period):
    # We assume "now" is the end of the day today
    # Makes it way easier to cache results of the API calls
    now = datetime.datetime.now(datetime.timezone.utc)
    now = now.replace(hour=0, minute=0, second=0, microsecond=0)
    now += datetime.timedelta(days=1, microseconds=-1)

    if preview_time_period:
        start = now - datetime.timedelta(days=2 * TIME_PERIOD_IN_DAYS)
        end = now - datetime.timedelta(days=TIME_PERIOD_IN_DAYS)
    else:
        start = now - datetime.timedelta(days=TIME_PERIOD_IN_DAYS)
        end = now

    return (start, end)


async def _make_api_request(path, params={}, preview_time_period=False):
    url = API_BASE_URL + path
    headers = {"Authorization": f"Bearer {API_AUTH_TOKEN}"}

    start, end = _get_time_period(preview_time_period)

    base_params = {
        "referrer": REFERRER,
        "start": start.isoformat(),
        "end": end.isoformat(),
    }
    combined_params = {}
    combined_params.update(base_params)
    combined_params.update(params)

    async with CachedSession(cache=cache_backend) as client:
        async with client.get(url, headers=headers, params=combined_params) as response:
            return await response.json()


async def get_frontend_state(
    org_slug, project_id, environment, preview_time_period=False
):
    response = await _make_api_request(
        path=f"/organizations/{org_slug}/events/",
        params={
            "project": project_id,
            "environment": environment,
            "dataset": "metrics",
            "query": 'transaction.op:[pageload,""] span.op:[ui.interaction.click,ui.interaction.hover,ui.interaction.drag,ui.interaction.press,""] !transaction:"<< unparameterized >>"',
            "field": [
                "p75(measurements.ttfb)",
                "p75(measurements.fcp)",
                "p75(measurements.inp)",
                "performance_score(measurements.score.ttfb)",
                "performance_score(measurements.score.fcp)",
                "performance_score(measurements.score.inp)",
            ],
        },
        preview_time_period=preview_time_period,
    )

    if len(response["data"]) == 0:
        return None

    # Rename returned keys for better readability
    rename_keys = {
        "p75(measurements.ttfb)": "ttfb",
        "p75(measurements.fcp)": "fcp",
        "p75(measurements.inp)": "inp",
        "performance_score(measurements.score.ttfb)": "ttfb_score",
        "performance_score(measurements.score.fcp)": "fcp_score",
        "performance_score(measurements.score.inp)": "inp_score",
    }

    data = response["data"][0]
    clean_data = {}

    for key in data.keys():
        if key in rename_keys:
            clean_data[rename_keys[key]] = data[key]

    return clean_data


async def get_backend_state(
    org_slug, project_id, environment, preview_time_period=False
):
    response = await _make_api_request(
        path=f"/organizations/{org_slug}/events/",
        params={
            "project": project_id,
            "environment": environment,
            "dataset": "metrics",
            "query": "event.type:transaction",
            "field": [
                "failure_rate()",
                "apdex()",
            ],
        },
        preview_time_period=preview_time_period,
    )

    if len(response["data"]) == 0:
        return None

    # Rename returned keys for better readability
    rename_keys = {
        "failure_rate()": "failure_rate",
        "apdex()": "apdex",
    }

    data = response["data"][0]
    clean_data = {}

    for key in data.keys():
        if key in rename_keys:
            clean_data[rename_keys[key]] = data[key]

    return clean_data


async def get_requests_state(
    org_slug, project_id, environment, preview_time_period=False
):
    response = await _make_api_request(
        path=f"/organizations/{org_slug}/events/",
        params={
            "project": project_id,
            "environment": environment,
            "dataset": "spansMetrics",
            "query": "span.module:http span.op:http.client",
            "field": [
                "http_response_rate(3)",
                "http_response_rate(4)",
                "http_response_rate(5)",
                "avg(span.self_time)",
            ],
        },
        preview_time_period=preview_time_period,
    )

    if len(response["data"]) == 0:
        return None

    # Rename returned keys for better readability
    rename_keys = {
        "http_response_rate(3)": "response_rate_3xx",
        "http_response_rate(4)": "response_rate_4xx",
        "http_response_rate(5)": "response_rate_5xx",
        "avg(span.self_time)": "time_avg",
    }

    data = response["data"][0]
    clean_data = {}

    for key in data.keys():
        if key in rename_keys:
            clean_data[rename_keys[key]] = data[key]

    return clean_data


async def get_cache_state(org_slug, project_id, environment, preview_time_period=False):
    response = await _make_api_request(
        path=f"/organizations/{org_slug}/events/",
        params={
            "project": project_id,
            "environment": environment,
            "dataset": "spansMetrics",
            "per_page": 5,
            "query": "span.op:[cache.get_item,cache.get]",
            "field": [
                "project",
                "project.id",
                "transaction",
                "cache_miss_rate()",
                "sum(span.self_time)",
                "avg(cache.item_size)",
                "time_spent_percentage()",
            ],
            "sort": "-time_spent_percentage()",
        },
        preview_time_period=preview_time_period,
    )

    if len(response["data"]) == 0:
        return None

    # Rename returned keys for better readability
    rename_keys = {
        "cache_miss_rate()": "miss_rate",
        "sum(span.self_time)": "time_total",
        "avg(cache.item_size)": "time_avg",
    }

    data = response["data"][0]
    clean_data = {}

    for key in data.keys():
        if key in rename_keys:
            clean_data[rename_keys[key]] = data[key]

    return clean_data


async def get_queue_state(org_slug, project_id, environment, preview_time_period=False):
    response = await _make_api_request(
        path=f"/organizations/{org_slug}/events/",
        params={
            "project": project_id,
            "environment": environment,
            "dataset": "spansMetrics",
            "per_page": 5,
            "query": "span.op:[queue.process,queue.publish]",
            "field": [
                "avg_if(span.duration,span.op,queue.process)",
                "avg(messaging.message.receive.latency)",
                "trace_status_rate(ok)",
                "time_spent_percentage(app,span.duration)",
            ],
            "sort": "-time_spent_percentage(app,span.duration)",
        },
        preview_time_period=preview_time_period,
    )

    if len(response["data"]) == 0:
        return None

    # Rename returned keys for better readability
    rename_keys = {
        "avg_if(span.duration,span.op,queue.process)": "processing_time_avg",
        "avg(messaging.message.receive.latency)": "time_in_queue_avg",
        "trace_status_rate(ok)": "success_rate",
        "time_spent_percentage(app,span.duration)": "time_percentage",
    }

    data = response["data"][0]
    clean_data = {}

    for key in data.keys():
        if key in rename_keys:
            clean_data[rename_keys[key]] = data[key]

    return clean_data


async def get_database_state(
    org_slug, project_id, environment, preview_time_period=False
):
    response = await _make_api_request(
        path=f"/organizations/{org_slug}/events/",
        params={
            "project": project_id,
            "environment": environment,
            "dataset": "spansMetrics",
            "per_page": 5,
            "query": "span.module:db has:span.description",
            "field": [
                "span.description",
                "avg(span.self_time)",
                "sum(span.self_time)",
                "time_spent_percentage()",
            ],
            "sort": "-time_spent_percentage()",
        },
        preview_time_period=preview_time_period,
    )

    if len(response["data"]) == 0:
        return None

    # Rename returned keys for better readability
    data = response["data"]
    clean_data = []

    for item in data:
        clean_data.append(
            {
                "query": item["span.description"],
                "time_avg": item["avg(span.self_time)"],
                "time_total": item["sum(span.self_time)"],
                "time_percentage": item["time_spent_percentage()"],
            }
        )

    return clean_data


async def get_project_data(org_slug, project_id):
    path = f"/projects/{org_slug}/{project_id}/"
    url = API_BASE_URL + path
    headers = {"Authorization": f"Bearer {API_AUTH_TOKEN}"}

    async with CachedSession(cache=cache_backend) as client:
        async with client.get(url, headers=headers) as response:
            project_data = await response.json()

    return project_data


async def get_org_data():
    frontend_project_data = await get_project_data(ORG_SLUG, FRONTEND_ID)
    backend_project_data = await get_project_data(ORG_SLUG, BACKEND_ID)

    if (
        frontend_project_data["organization"]["name"]
        == backend_project_data["organization"]["name"]
    ):
        org_name = frontend_project_data["organization"]["name"]
    else:
        org_name = f"{frontend_project_data['organization']['name']} / {backend_project_data['organization']['name']}"

    data = {
        "name": org_name,
        "frontend_id": FRONTEND_ID,
        "frontend_url": frontend_project_data["organization"]["links"][
            "organizationUrl"
        ],
        "backend_id": BACKEND_ID,
        "backend_url": backend_project_data["organization"]["links"]["organizationUrl"],
    }

    return data


async def get_data():
    data = {}

    frontend_project_data = await get_project_data(ORG_SLUG, FRONTEND_ID)
    backend_project_data = await get_project_data(ORG_SLUG, BACKEND_ID)

    if (
        frontend_project_data["organization"]["name"]
        == backend_project_data["organization"]["name"]
    ):
        org_name = frontend_project_data["organization"]["name"]
    else:
        org_name = f"{frontend_project_data['organization']['name']} / {backend_project_data['organization']['name']}"

    data["org"] = {
        "name": org_name,
        "frontend_id": FRONTEND_ID,
        "frontend_url": frontend_project_data["organization"]["links"][
            "organizationUrl"
        ],
        "backend_id": BACKEND_ID,
        "backend_url": backend_project_data["organization"]["links"]["organizationUrl"],
    }

    data["frontend_requests"] = await get_requests_state(
        org_slug=ORG_SLUG,
        project_id=FRONTEND_ID,
        environment=FRONTEND_ENV,
    )
    data["frontend_requests_prev"] = await get_requests_state(
        org_slug=ORG_SLUG,
        project_id=FRONTEND_ID,
        environment=FRONTEND_ENV,
        preview_time_period=True,
    )

    data["backend"] = await get_backend_state(
        org_slug=ORG_SLUG,
        project_id=BACKEND_ID,
        environment=BACKEND_ENV,
    )
    data["backend_prev"] = await get_backend_state(
        org_slug=ORG_SLUG,
        project_id=BACKEND_ID,
        environment=BACKEND_ENV,
        preview_time_period=True,
    )

    data["backend_requests"] = await get_requests_state(
        org_slug=ORG_SLUG,
        project_id=BACKEND_ID,
        environment=BACKEND_ENV,
    )
    data["backend_requests_prev"] = await get_requests_state(
        org_slug=ORG_SLUG,
        project_id=BACKEND_ID,
        environment=BACKEND_ENV,
        preview_time_period=True,
    )

    data["cache"] = await get_cache_state(
        org_slug=ORG_SLUG,
        project_id=BACKEND_ID,
        environment=BACKEND_ENV,
    )
    data["cache_prev"] = await get_cache_state(
        org_slug=ORG_SLUG,
        project_id=BACKEND_ID,
        environment=BACKEND_ENV,
        preview_time_period=True,
    )

    data["queue"] = await get_queue_state(
        org_slug=ORG_SLUG,
        project_id=BACKEND_ID,
        environment=BACKEND_ENV,
    )
    data["queue_prev"] = await get_queue_state(
        org_slug=ORG_SLUG,
        project_id=BACKEND_ID,
        environment=BACKEND_ENV,
        preview_time_period=True,
    )

    data["database"] = await get_database_state(
        org_slug=ORG_SLUG,
        project_id=BACKEND_ID,
        environment=BACKEND_ENV,
    )

    return data
