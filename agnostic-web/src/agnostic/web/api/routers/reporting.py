from uuid import UUID

from fastapi import Depends, APIRouter, Query

from agnostic.core import dal
from agnostic.core.schemas import reporting as rs

router = APIRouter(prefix="/reporting", tags=["Reporting"])


@router.get("/projects", response_model=rs.PagedProjects)
async def get_projects_report(
    reporting: dal.Reporting = Depends(dal.get_reporting),
    order_by: str = Query("name", regex="^(name|test_runs_count|latest_test_run)$"),
    order: str = Query("asc", regex="^asc|desc$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
):
    return await reporting.get_projects(order_by, order, page, page_size)


@router.get("/projects/{project_id}/test-runs", response_model=rs.PagedTestRuns)
async def get_project_test_runs_report(
    project_id: UUID,
    reporting: dal.Reporting = Depends(dal.get_reporting),
    order_by: str = Query(
        "start",
        regex="^(start|finish|sut_branch|sut_version|test_branch|test_version)$",
    ),
    order: str = Query("asc", regex="^asc|desc$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    sut_branch: list[str] | None = Query(None),
    test_branch: list[str] | None = Query(None),
    variant: list[str] | None = Query(None),
    interval: str | None = Query(None),
    test_run_id: UUID | None = Query(None),
):
    return await reporting.get_test_runs(
        project_id,
        order_by,
        order,
        page,
        page_size,
        sut_branch,
        test_branch,
        variant,
        interval,
        test_run_id,
    )


@router.get("/projects/{project_id}/tests-over-time", response_model=rs.TestsOverTime)
async def get_project_tests_over_time_report(
    project_id: UUID,
    reporting: dal.Reporting = Depends(dal.get_reporting),
    sut_branch: list[str] | None = Query(None),
    test_branch: list[str] | None = Query(None),
    variant: list[str] | None = Query(None),
    interval: str | None = Query(None),
):
    return await reporting.get_tests_over_time(
        project_id, sut_branch, test_branch, variant, interval
    )


@router.get("/projects/{project_id}/test-run-filters", response_model=rs.TestRunFilters)
async def get_project_test_run_reporting_filters(
    project_id: UUID,
    reporting: dal.Reporting = Depends(dal.get_reporting),
    interval: str | None = Query(None),
):
    return await reporting.get_test_run_filters(project_id, interval)


@router.get("/projects/{project_id}/top-failed-tests", response_model=rs.TopFailedTests)
async def get_project_top_failed_tests_report(
    project_id: UUID,
    reporting: dal.Reporting = Depends(dal.get_reporting),
    sut_branch: list[str] | None = Query(None),
    test_branch: list[str] | None = Query(None),
    variant: list[str] | None = Query(None),
    interval: str | None = Query(None),
    limit: int | None = Query(5),
):
    return await reporting.get_top_failed_test(
        project_id, sut_branch, test_branch, variant, interval, limit
    )


@router.post("/projects/{project_id}/project-metrics", response_model=rs.MetricsAggregate)
async def get_project_metrics_report(
    project_id: UUID,
    metrics: list[rs.MetricRequest],
    reporting: dal.Reporting = Depends(dal.get_reporting),
    sut_branch: list[str] | None = Query(None),
    test_branch: list[str] | None = Query(None),
    variant: list[str] | None = Query(None),
    interval: str | None = Query(None),
):
    return await reporting.get_project_metrics(
        project_id, sut_branch, test_branch, variant, interval, metrics
    )


@router.get(
    "/projects/{project_id}/test-runs/{test_run_id}/tests-by-result",
    response_model=rs.widgets.TestsByResult,
)
async def get_test_run_tests_by_result(
    project_id: UUID,
    test_run_id: UUID,
    result: list[str] | None = Query(None),
    search: list[str] | None = Query(None),
    reporting: dal.Reporting = Depends(dal.get_reporting),
):
    return await reporting.get_tests_by_result(project_id, test_run_id, result, search)


@router.get("/projects/{project_id}/test-runs/{test_run_id}/tests", response_model=rs.PagedTests)
async def get_test_run_tests_report(
    project_id: UUID,
    test_run_id: UUID,
    result: list[str] | None = Query(None),
    search: list[str] | None = Query(None),
    order_by: str = Query("path", regex="^(result|name|path|execution_time)$"),
    order: str = Query("asc", regex="^asc|desc$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    reporting: dal.Reporting = Depends(dal.get_reporting),
):
    return await reporting.get_tests(
        project_id, test_run_id, result, search, order, order_by, page, page_size
    )


@router.get(
    "/projects/{project_id}/test-runs/{test_run_id}/metrics-list",
    response_model=rs.PagedTestRunMetricsList,
)
async def get_test_run_metrics_list_report(
    project_id: UUID,
    test_run_id: UUID,
    order_by: str = Query("name", regex="^(name|value|description)$"),
    order: str = Query("asc", regex="^asc|desc$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    reporting: dal.Reporting = Depends(dal.get_reporting),
):
    return await reporting.get_test_run_metrics_list(
        project_id, test_run_id, order, order_by, page, page_size
    )


@router.get(
    "/projects/{project_id}/test-runs/{test_run_id}/progress",
    response_model=rs.PagedTestRunProgressRecords,
)
async def get_test_run_progress(
    project_id: UUID,
    test_run_id: UUID,
    result: list[str] | None = Query(None),
    search: list[str] | None = Query(None),
    order_by: str = Query("timestamp", regex="^(timestamp|level|message|details)$"),
    order: str = Query("desc", regex="^asc|desc$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    reporting: dal.Reporting = Depends(dal.get_reporting),
):
    return await reporting.get_test_run_progress(
        project_id, test_run_id, result, search, order, order_by, page, page_size
    )


@router.get(
    "/projects/{project_id}/test-runs/{test_run_id}/logs",
    response_model=rs.PagedTestRunLog,
)
async def get_test_run_metrics_list(
    project_id: UUID,
    test_run_id: UUID,
    order_by: str = Query("name", regex="^(name|start|finish)$"),
    order: str = Query("asc", regex="^asc|desc$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    reporting: dal.Reporting = Depends(dal.get_reporting),
):
    return await reporting.get_test_run_logs(
        project_id, test_run_id, order, order_by, page, page_size
    )


@router.get(
    "/projects/{project_id}/test-runs/{test_run_id}/metrics-ot",
    response_model=rs.MetricOverTimeReport,
)
async def get_test_run_over_time_metric(
    project_id: UUID,
    test_run_id: UUID,
    result: list[str] | None = Query(None),
    search: list[str] | None = Query(None),
    name: str | None = Query(None),
    key: list[str] | None = Query(None),
    reporting: dal.Reporting = Depends(dal.get_reporting),
):
    return await reporting.get_test_run_over_time_metric(
        project_id, test_run_id, result, search, name, key
    )


@router.get(
    "/projects/{project_id}/test-runs/{test_run_id}/tests/{test_id}",
    response_model=rs.TestReport,
)
async def get_test_details(
    project_id: UUID,
    test_run_id: UUID,
    test_id: UUID,
    reporting: dal.Reporting = Depends(dal.get_reporting),
):
    return await reporting.get_test_details(project_id, test_run_id, test_id)


@router.post(
    "/projects/{project_id}/test-runs/{test_run_id}/test-run-metrics",
    response_model=rs.MetricsAggregate,
)
async def get_test_run_metrics_report(
    project_id: UUID,
    test_run_id: UUID,
    metrics: list[rs.MetricRequest],
    result: list[str] | None = Query(None),
    search: list[str] | None = Query(None),
    reporting: dal.Reporting = Depends(dal.get_reporting),
):
    return await reporting.get_test_run_metrics_and_properties(
        project_id, test_run_id, result, search, metrics
    )
