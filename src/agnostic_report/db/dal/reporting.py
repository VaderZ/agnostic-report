import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import aliased
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.expression import func, cast, text, and_, case as case_, or_
from sqlalchemy.types import Float

from .. import models
from ...api import schemas

NOT_SET = '<not set>'


def get_interval_filter(interval: str | None = None) -> tuple[str, list[BinaryExpression]]:
    match interval.lower() if interval else None:
        case 'week':
            return 'day', [models.TestRun.start >= datetime.datetime.utcnow() - datetime.timedelta(days=7)]
        case 'month':
            return 'day', [models.TestRun.start >= datetime.datetime.utcnow() - datetime.timedelta(days=30)]
        case 'quarter':
            return 'week', [models.TestRun.start >= datetime.datetime.utcnow() - datetime.timedelta(days=90)]
        case 'year':
            return 'month', [models.TestRun.start >= datetime.datetime.utcnow() - datetime.timedelta(days=365)]
        case 'all':
            return 'month', []
        case _:
            return 'month', []


def get_variant_filter(variant: list[str] | None = None) -> list[BinaryExpression]:
    filters = []
    if variant:
        for var in variant:
            parts = var.split(' -eq ')
            filters.append(and_(models.TestRunVariant.name == parts[0], models.TestRunVariant.value == parts[1]))
    return filters


def get_branch_filter(field: str, branches: list[str] | None = None) -> list[BinaryExpression]:
    if branches:
        branch_filters = []
        in_branches = []
        for branch in branches:
            if branch == NOT_SET:
                branch_filters.append(getattr(models.TestRun, field).is_(None))
            else:
                in_branches.append(branch)
        if in_branches:
            branch_filters.append(getattr(models.TestRun, field).in_(in_branches))

        return branch_filters
    return []


def get_test_run_filter(project_id: UUID,
                        sut_branch: list[str] | None = None,
                        test_branch: list[str] | None = None,
                        variant: list[str] | None = None,
                        interval: str | None = None,
                        test_run_id: UUID | None = None) -> tuple[list[BinaryExpression], str]:
    trunc_to = None
    tr_filters = [models.TestRun.project_id == project_id, ]
    if not test_run_id:
        trunc_to, filters = get_interval_filter(interval)
        tr_filters.extend(filters)
        tr_filters.append(or_(*get_variant_filter(variant)))
        tr_filters.append(or_(*get_branch_filter('sut_branch', sut_branch)))
        tr_filters.append(or_(*get_branch_filter('test_branch', test_branch)))
    else:
        tr_filters.append(models.TestRun.id == test_run_id)

    return tr_filters, trunc_to


def get_test_filter(test_run_id: UUID, result: list[str] | None, search: list[str] | None) -> list[BinaryExpression]:
    test_filter = [models.Test.test_run_id == test_run_id,]

    result_filter = models.Test.result.in_(result or [])
    if result and 'unknown' in result:
        result_filter = or_(result_filter, models.Test.result.is_(None))

    test_filter.append(result_filter)

    if search:
        search_filter = []
        for term in search:
            search_filter.append(func.concat(models.Test.path, '/', models.Test.name).like(f'%{term}%'))
        test_filter.append(or_(*search_filter))

    return test_filter


class Reporting:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_projects(self, order_by: str, order: str,
                           page: int, page_size: int) -> schemas.PagedProjects:
        pages = (
            await self.session.execute(
                select(
                    func.count(models.Project.id).label('count'),
                    func.ceil(cast(func.count(models.Project.id), Float) / page_size).label('pages')
                )
            )
        ).first()

        projects = (
            await self.session.execute(
                select(
                    models.Project.id,
                    func.max(models.Project.name).label('name'),
                    func.count(models.TestRun.id).label('test_runs_count'),
                    func.coalesce(
                        func.max(models.TestRun.start), None
                    ).label('latest_test_run')
                ).join(
                    models.TestRun, models.TestRun.project_id == models.Project.id, isouter=True
                ).group_by(
                    models.Project.id,
                ).order_by(
                    text(f'{order_by} {order}')
                ).limit(page_size).offset((page - 1) * page_size)
            )
        ).all()
        return schemas.PagedProjects(
            data=[schemas.ProjectStatistics.from_orm(project) for project in projects],
            count=pages.count,
            pages=pages.pages,
            page=page,
            page_size=page_size
        )

    async def get_test_runs(self,
                            project_id: UUID,
                            order_by: str,
                            order: str,
                            page: int,
                            page_size: int,
                            sut_branch: list[str] | None = None,
                            test_branch: list[str] | None = None,
                            variant: list[str] | None = None,
                            interval: str | None = None,
                            test_run_id: UUID | None = None) -> schemas.PagedTestRuns:

        tr_filters, _ = get_test_run_filter(project_id, sut_branch, test_branch, variant, interval, test_run_id)

        pages = (
            await self.session.execute(
                select(
                    func.count(func.distinct(models.TestRun.id)).label('count'),
                    func.ceil(cast(func.count(func.distinct(models.TestRun.id)), Float) / page_size).label('pages')
                ).join(
                    models.TestRunVariant, models.TestRunVariant.test_run_id == models.TestRun.id, isouter=True
                ).where(
                    and_(*tr_filters)
                )
            )
        ).first()

        t_count = select(
            models.Test.test_run_id,
            func.count(models.Test.id).label('tests_executed'),
            func.count(models.Test.id).filter(models.Test.result == 'failed').label('tests_failed'),
        ).group_by(
            models.Test.test_run_id
        ).subquery()

        trv = aliased(models.TestRunVariant)

        test_runs = (
            await self.session.execute(
                select(
                    models.TestRun.id,
                    models.TestRun.sut_branch,
                    models.TestRun.sut_version,
                    models.TestRun.test_branch,
                    models.TestRun.test_version,
                    models.TestRun.start,
                    models.TestRun.finish,
                    models.TestRun.heartbeat,
                    models.TestRun.properties,
                    (models.TestRun.finish - models.TestRun.start).label('execution_time'),
                    func.jsonb_object_agg(
                        trv.name, trv.value
                    ).filter(trv.name.is_not(None)).label('variant'),
                    case_(
                        (func.max(t_count.c.tests_executed).is_(None), 0), else_=func.max(t_count.c.tests_executed)
                    ).label('tests_executed'),
                    case_(
                            (func.max(t_count.c.tests_failed).is_(None), 0), else_=func.max(t_count.c.tests_failed)
                        ).label('tests_failed')
                ).join(
                    t_count, t_count.c.test_run_id == models.TestRun.id, isouter=True
                ).join(
                    models.TestRunVariant, models.TestRun.id == models.TestRunVariant.test_run_id, isouter=True
                ).join(
                    trv, models.TestRun.id == trv.test_run_id, isouter=True
                ).where(
                    and_(*tr_filters)
                ).group_by(
                    models.TestRun.id
                ).order_by(
                    text(f'{order_by} {order}')
                ).limit(
                    page_size
                ).offset(
                    (page - 1) * page_size
                )
            )
        ).all()

        def is_terminated(test_run, alive_interval=60) -> bool:
            return (not test_run.finish
                    and test_run.heartbeat
                    and ((datetime.datetime.utcnow() - test_run.heartbeat).total_seconds() > alive_interval)) \
                   or (not test_run.finish and not test_run.heartbeat)

        def make_test_run_statistics(test_run) -> schemas.TestRunsStatistics:
            terminated = is_terminated(test_run)
            tr = schemas.TestRunsStatistics.from_orm(test_run)
            status = schemas.TestRunStatus(
                running=test_run.finish is None and not terminated,
                failed=test_run.tests_failed > 0,
                terminated=terminated
            )
            tr.status = status
            return tr

        return schemas.PagedTestRuns(
            data=[make_test_run_statistics(test_run) for test_run in test_runs],
            count=pages.count,
            pages=pages.pages,
            page=page,
            page_size=page_size
        )

    async def get_tests_over_time(self, project_id: UUID,
                                  sut_branch: list[str] | None = None,
                                  test_branch: list[str] | None = None,
                                  variant: list[str] | None = None,
                                  interval: str | None = None) -> schemas.TestsOverTime:
        tr_filters, trunc_to = get_test_run_filter(project_id, sut_branch, test_branch, variant, interval)

        by_date = select(
            # TODO: func.max is redundant here, but sqlalchemy wants it
            func.max(func.date_trunc(trunc_to, models.TestRun.start)).label('date'),
            func.count(func.distinct(models.Test.id)).label('total'),
            func.count(
                func.distinct(models.Test.id)
            ).filter(models.Test.result == schemas.TestResult.PASSED).label('passed'),
            func.count(
                func.distinct(models.Test.id)
            ).filter(models.Test.result == schemas.TestResult.FAILED).label('failed'),
            func.count(
                func.distinct(models.Test.id)
            ).filter(models.Test.result == schemas.TestResult.XPASSED).label('xpassed'),
            func.count(
                func.distinct(models.Test.id)
            ).filter(models.Test.result == schemas.TestResult.XFAILED).label('xfailed'),
            func.count(
                func.distinct(models.Test.id)
            ).filter(models.Test.result == schemas.TestResult.SKIPPED).label('skipped'),
        ).join(
            models.Test, models.Test.test_run_id == models.TestRun.id
        ).join(
            models.TestRunVariant, models.TestRunVariant.test_run_id == models.TestRun.id, isouter=True
        ).where(
            and_(*tr_filters)
        ).group_by(
            func.date_trunc(trunc_to, models.TestRun.start)
        ).order_by(
            # TODO: func.max is redundant here, but sqlalchemy wants it
            func.max(func.date_trunc(trunc_to, models.TestRun.start))
        )

        by_date = (
            await self.session.execute(
                select(
                    func.array_agg(by_date.c.date).label('date'),
                    func.array_agg(by_date.c.total).label('total'),
                    func.array_agg(by_date.c.passed).label('passed'),
                    func.array_agg(by_date.c.failed).label('failed'),
                    func.array_agg(by_date.c.xpassed).label('xpassed'),
                    func.array_agg(by_date.c.xfailed).label('xfailed'),
                    func.array_agg(by_date.c.skipped).label('skipped'),
                )
            )
        ).first()

        return schemas.TestsOverTime(
            data=schemas.TestsOverTimeData(
                series=[schemas.TestsOverTimeSeries(name=name, data=getattr(by_date, name) or []) for name in
                        ['skipped', 'xfailed', 'xpassed', 'failed', 'passed']],
                categories=by_date.date or []
            )
        )

    async def get_test_run_filters(self, project_id: UUID, interval: str | None = None) -> schemas.TestRunFilters:
        tr_filters = get_interval_filter(interval)[1]
        branch_filters = (
            await self.session.execute(
                select(
                    func.array_agg(
                        func.distinct(
                            case_(
                                (models.TestRun.sut_branch.is_not(None), models.TestRun.sut_branch), else_=NOT_SET
                            )
                        )
                    ).label('sut_branch'),
                    func.array_agg(
                        func.distinct(
                            case_(
                                (models.TestRun.test_branch.is_not(None), models.TestRun.test_branch), else_=NOT_SET
                            )
                        )
                    ).label('test_branch')
                ).join(
                    models.Project, and_(
                        models.TestRun.project_id == models.Project.id,
                        models.Project.id == project_id,
                        *tr_filters
                    )
                )
            )
        ).first()

        variant_filters = (
            await self.session.execute(
                select(
                    models.TestRunVariant.name.label('name'),
                    func.array_agg(func.distinct(models.TestRunVariant.value)).label('variant')
                ).join(
                    models.TestRun, models.TestRunVariant.test_run_id == models.TestRun.id
                ).join(
                    models.Project, and_(
                        models.TestRun.project_id == models.Project.id,
                        models.Project.id == project_id,
                        *tr_filters
                    )
                ).where(
                    models.TestRunVariant.name.is_not(None)
                ).group_by(
                    models.TestRunVariant.name
                )
            )
        ).all()

        return schemas.TestRunFilters(
            data=schemas.TestRunFiltersData(
                sut_branch=sorted(branch_filters.sut_branch) if branch_filters.sut_branch else [],
                test_branch=sorted(branch_filters.test_branch) if branch_filters.test_branch else [],
                variant=sorted(variant_filters) if variant_filters else []
            )
        )

    async def get_top_failed_test(self,
                                  project_id: UUID,
                                  sut_branch: list[str] | None = None,
                                  test_branch: list[str] | None = None,
                                  variant: list[str] | None = None,
                                  interval: str | None = None,
                                  limit: int | None = 5) -> schemas.TopFailedTests:

        tr_filters, _ = get_test_run_filter(project_id, sut_branch, test_branch, variant, interval)

        stat = select(
            models.Test.path,
            models.Test.name,
            func.count(func.distinct(models.Test.id)).label('total'),
            func.count(
                func.distinct(models.Test.id)
            ).filter(
                models.Test.result == schemas.TestResult.FAILED
            ).label('failed')
        ).join(
            models.TestRun, models.Test.test_run_id == models.TestRun.id, isouter=True
        ).join(
            models.TestRunVariant, models.TestRun.id == models.TestRunVariant.test_run_id, isouter=True
        ).where(
            and_(*tr_filters)
        ).group_by(
            models.Test.path, models.Test.name
        ).having(
            func.count(
                func.distinct(models.Test.id)
            ).filter(
                models.Test.result == schemas.TestResult.FAILED
            ) > 0
        ).subquery()

        top_failed = (
            await self.session.execute(
                select(
                    stat.c.path,
                    stat.c.name,
                    stat.c.total,
                    stat.c.failed,
                    func.round((cast(stat.c.failed, Float) / cast(stat.c.total, Float)) * 100).label('percent_failed')
                ).order_by(
                    cast(stat.c.failed, Float) / cast(stat.c.total, Float).desc(), stat.c.path, stat.c.name
                ).limit(
                    limit
                )
            )
        ).all()

        return schemas.TopFailedTests(
            data=[schemas.TopFailedTestsData.from_orm(test) for test in top_failed]
        )

    async def get_project_metrics(self,
                                  project_id: UUID,
                                  sut_branch: list[str] | None = None,
                                  test_branch: list[str] | None = None,
                                  variant: list[str] | None = None,
                                  interval: str | None = None,
                                  metrics: list[schemas.MetricRequest] | None = None) -> schemas.MetricsAggregate:
        tr_filters, trunc_to = get_test_run_filter(project_id, sut_branch, test_branch, variant, interval)

        trs = select(
            models.TestRun.id
        ).join(
            models.TestRunVariant, models.TestRun.id == models.TestRunVariant.test_run_id, isouter=True
        ).where(
            and_(*tr_filters)
        ).group_by(
            models.TestRun.id
        ).subquery()

        metrics_sql = []
        metrics_ot_sql = []
        for metric in metrics:
            if metric.table == 'metrics':
                aggregate = getattr(func, metric.func)(models.Metric.value)
                col_filter = models.Metric.name == metric.name
                if metric.filter:
                    aggregate = aggregate.filter(
                        and_(
                            col_filter,
                            text(f"metrics.value {metric.filter}")
                        )
                    )
                metrics_sql.append(
                    aggregate.label(metric.title)
                )
            elif metric.table == 'metrics_over_time':
                aggregate = getattr(func, metric.func)(cast(models.MetricOverTime.values[metric.field], Float))
                col_filter = models.MetricOverTime.name == metric.name
                if metric.filter:
                    aggregate = aggregate.filter(
                        and_(
                            col_filter,
                            text(f"cast(metrics_over_time.values::jsonb->'{metric.filter_field}' as float) "
                                 f"{metric.filter}"))
                    )
                metrics_ot_sql.append(
                    aggregate.label(metric.title)
                )

        project_metrics = (
            await self.session.execute(
                select(
                    *metrics_sql
                ).where(
                    models.Metric.test_run_id.in_(trs)
                )
            )
        ).first()

        project_ot_metrics = (
            await self.session.execute(
                select(
                    *metrics_ot_sql
                ).where(
                    models.MetricOverTime.test_run_id.in_(trs)
                )
            )
        ).first()

        result = schemas.MetricsAggregate(data=[])
        for metric in metrics:
            if metric.table == 'metrics':
                table = project_metrics
            else:
                table = project_ot_metrics
            result.data.append(
                schemas.MetricsData(
                    name=metric.title,
                    value=table[metric.title]
                )
            )

        return result

    async def get_tests_by_result(self,
                                  project_id: UUID,
                                  test_run_id: UUID,
                                  result: list[str] | None,
                                  search: list[str] | None) -> schemas.TestsByResult:
        by_result = (
            await self.session.execute(
                select(
                    case_((models.Test.result.is_not(None), models.Test.result), else_='unknown').label('label'),
                    func.count(models.Test.id).label('value')
                ).where(
                    and_(*get_test_filter(test_run_id, result, search))
                ).group_by(
                    models.Test.result
                ).order_by(
                    case_(
                        {
                            schemas.TestResult.PASSED: 1,
                            schemas.TestResult.FAILED: 2,
                            schemas.TestResult.XPASSED: 3,
                            schemas.TestResult.XFAILED: 4,
                            schemas.TestResult.SKIPPED: 5
                        },
                        value=models.Test.result,
                        else_=6
                    )
                )
            )
        ).all()

        return schemas.TestsByResult(
            data=schemas.TestsByResultData(
               series=[result.value for result in by_result],
               labels=[result.label for result in by_result]
            )
        )

    async def get_tests(self,
                        project_id: UUID,
                        test_run_id: UUID,
                        result: list[str] | None,
                        search: list[str] | None,
                        order: str,
                        order_by: str,
                        page: int,
                        page_size: int) -> schemas.PagedTests:

        test_filters = and_(*get_test_filter(test_run_id, result, search))

        pages = (
            await self.session.execute(
                select(
                    func.count(func.distinct(models.Test.id)).label('count'),
                    func.ceil(cast(func.count(models.Test.id), Float) / page_size).label('pages')
                ).where(
                    test_filters
                )
            )
        ).first()

        order_sql = [text(f'{order_by} {order}')]
        if order_by != 'name':
            order_sql.append(models.Test.name)

        tests = (
            await self.session.execute(
                select(
                    models.Test.id,
                    case_((models.Test.result.is_not(None), models.Test.result), else_='unknown').label('result'),
                    models.Test.name,
                    models.Test.path,
                    (models.Test.finish - models.Test.start).label('execution_time')
                ).where(
                    test_filters
                ).order_by(
                    *order_sql
                ).limit(
                    page_size
                ).offset(
                    (page - 1) * page_size
                )
            )
        ).all()

        return schemas.PagedTests(
            data=[schemas.TestsStatistics.from_orm(test) for test in tests],
            count=pages.count,
            pages=pages.pages,
            page=page,
            page_size=page_size
        )

    async def get_test_run_metrics_list(self,
                                        project_id: UUID,
                                        test_run_id: UUID,
                                        order: str,
                                        order_by: str,
                                        page: int,
                                        page_size: int) -> schemas.PagedTestRunMetricsList:
        pages = (
            await self.session.execute(
                select(
                    func.count(func.distinct(models.Metric.id)).label('count'),
                    func.ceil(cast(func.count(models.Metric.id), Float) / page_size).label('pages')
                ).where(
                    models.Metric.test_run_id == test_run_id
                )
            )
        ).first()

        order_sql = [text(f'{order_by} {order}')]
        if order_by != 'name':
            order_sql.append(models.Metric.name)

        metrics = (
            await self.session.execute(
                select(
                    models.Metric.id,
                    models.Metric.name,
                    models.Metric.value,
                    models.Metric.description
                ).where(
                    models.Metric.test_run_id == test_run_id
                ).order_by(
                    *order_sql
                ).limit(
                    page_size
                ).offset(
                    (page - 1) * page_size
                )
            )
        ).all()

        data = []
        for metric in metrics:
            data.append(schemas.TestRunMetricsListStatistics(
                name=metric.name,
                value=metric.value,
                description=metric.description.format(metric.value)
            ))

        return schemas.PagedTestRunMetricsList(
            data=data,
            count=pages.count,
            pages=pages.pages,
            page=page,
            page_size=page_size
        )

    async def get_test_run_progress(self,
                                    project_id: UUID,
                                    test_run_id: UUID,
                                    result: list[str] | None,
                                    search: list[str] | None,
                                    order: str,
                                    order_by: str,
                                    page: int,
                                    page_size: int) -> schemas.PagedTestRunProgressRecords:
        if (result and len(result) < 6) or not result or search:
            filters = and_(*get_test_filter(test_run_id, result, search))
        else:
            filters = models.Progress.test_run_id == test_run_id
        pages = (
            await self.session.execute(
                select(
                    func.count(func.distinct(models.Progress.id)).label('count'),
                    func.ceil(cast(func.count(models.Progress.id), Float) / page_size).label('pages')
                ).join(
                    models.Test, models.Test.id == models.Progress.test_id, isouter=True
                ).where(
                    filters
                )
            )
        ).first()

        order_sql = [text(f'{order_by} {order}')]
        if order_by != 'timestamp':
            order_sql.append(models.Progress.timestamp)

        progress = (
            await self.session.execute(
                select(
                    models.Progress.id,
                    models.Progress.timestamp,
                    models.Progress.level,
                    models.Progress.message,
                    models.Progress.details
                ).join(
                    models.Test, models.Test.id == models.Progress.test_id, isouter=True
                ).where(
                    filters
                ).order_by(
                    *order_sql
                ).limit(
                    page_size
                ).offset(
                    (page - 1) * page_size
                )
            )
        ).all()

        return schemas.PagedTestRunProgressRecords(
            data=[schemas.TestRunProgressRecord.from_orm(record) for record in progress],
            count=pages.count,
            pages=pages.pages,
            page=page,
            page_size=page_size
        )

    async def get_test_run_logs(self,
                                project_id: UUID,
                                test_run_id: UUID,
                                order: str,
                                order_by: str,
                                page: int,
                                page_size: int) -> schemas.PagedTestRunLog:
        pages = (
            await self.session.execute(
                select(
                    func.count(func.distinct(models.Log.id)).label('count'),
                    func.ceil(cast(func.count(models.Log.id), Float) / page_size).label('pages')
                ).where(
                    models.Log.test_run_id == test_run_id, models.Log.test_id.is_(None)
                )
            )
        ).first()

        order_sql = [text(f'{order_by} {order}')]
        if order_by != 'name':
            order_sql.append(models.Log.name)

        logs = (
            await self.session.execute(
                select(
                    models.Log.id,
                    models.Log.name,
                    models.Log.start,
                    models.Log.finish
                ).where(
                    models.Log.test_run_id == test_run_id, models.Log.test_id.is_(None)
                ).order_by(
                    *order_sql
                ).limit(
                    page_size
                ).offset(
                    (page - 1) * page_size
                )
            )
        ).all()

        return schemas.PagedTestRunLog(
            data=[schemas.TestRunLog.from_orm(log) for log in logs],
            count=pages.count,
            pages=pages.pages,
            page=page,
            page_size=page_size
        )

    async def get_test_run_over_time_metric(self,
                                            project_id: UUID,
                                            test_run_id: UUID,
                                            result: list[str] | None,
                                            search: list[str] | None,
                                            name: str | None,
                                            key: list[str] | None):
        if not name or not key:
            return schemas.MetricOverTimeReport()

        if (result and len(result) < 6) or not result or search:
            filters = and_(models.MetricOverTime.name == name, *get_test_filter(test_run_id, result, search))
        else:
            filters = and_(models.MetricOverTime.name == name, models.MetricOverTime.test_run_id == test_run_id)

        series = select(
            models.MetricOverTime.timestamp.label('date'),
            *[models.MetricOverTime.values[k].label(k) for k in key]
        ).join(
            models.Test, models.Test.id == models.MetricOverTime.test_id, isouter=True
        ).where(
            filters
        ).order_by(
            models.MetricOverTime.timestamp.desc()
        )

        series = (
            await self.session.execute(
                select(
                    func.array_agg(series.c.date).label('date'),
                    *[func.array_agg(getattr(series.c, k)).label(k) for k in key]
                )
            )
        ).first()

        return schemas.MetricOverTimeReport(
            data=schemas.MetricOverTimeData(
                series=[schemas.MetricOverTimeSeries(name=k, data=getattr(series, k) or []) for k in key],
                categories=series.date or []
            )
        )

    async def get_test_details(self,
                               project_id: UUID,
                               test_run_id: UUID,
                               test_id: UUID) -> schemas.TestReport:

        attachments = select(
            models.Attachment.id,
            models.Attachment.test_id,
            models.Attachment.timestamp,
            models.Attachment.name,
            models.Attachment.mime_type,
            models.Attachment.size
        ).where(
            models.Attachment.test_id == test_id
        ).order_by(
            models.Attachment.name
        ).subquery()

        logs = select(
            models.Log.id,
            models.Log.test_id,
            models.Log.name,
            models.Log.start,
            models.Log.finish,
            models.Log.body
        ).where(
            models.Log.test_id == test_id
        ).order_by(
            models.Log.name
        ).subquery()

        metrics = select(
            models.Metric.id,
            models.Metric.test_id,
            models.Metric.timestamp,
            models.Metric.name,
            models.Metric.value,
            models.Metric.description
        ).where(
            models.Metric.test_id == test_id
        ).order_by(
            models.Metric.name
        ).subquery()

        requests = select(
            models.Request.id,
            models.Request.test_id,
            models.Request.request_type,
            models.Request.timestamp,
            models.Request.contents
        ).where(
            models.Request.test_id == test_id
        ).order_by(
            models.Request.timestamp
        ).subquery()

        test = (
            await self.session.execute(
                select(
                    func.to_jsonb(models.Test.__table__.table_valued()).label('details'),
                    func.array_agg(func.distinct(func.to_jsonb(attachments.table_valued()))).label('attachments'),
                    func.array_agg(func.distinct(func.to_jsonb(logs.table_valued()))).label('logs'),
                    func.array_agg(func.distinct(func.to_jsonb(metrics.table_valued()))).label('metrics'),
                    func.array_agg(func.distinct(func.to_jsonb(requests.table_valued()))).label('requests'),
                ).select_from(
                    models.Test,
                    attachments,
                    logs,
                    metrics,
                    requests
                ).join(
                    attachments, attachments.c.test_id == models.Test.id, isouter=True
                ).join(
                    logs, logs.c.test_id == models.Test.id, isouter=True
                ).join(
                    metrics, metrics.c.test_id == models.Test.id, isouter=True
                ).join(
                    requests, requests.c.test_id == models.Test.id, isouter=True
                ).where(
                    models.Test.id == test_id
                ).group_by(
                    models.Test.id
                )
            )
        ).first()

        metrics = []
        for metric in test.metrics:
            if metric:
                d = dict(metric)
                d['description'] = d['description'].format(d['value'])
                metrics.append(d)

        def fix_timestamp(timestamp):
            # ISO timestamp has to have 3 or 6 numbers at the end, but Postgres omits them if they're 0
            return datetime.datetime.fromisoformat(timestamp + (26 - len(timestamp)) * '0')

        # TODO: Figure out how to carry sorting through json aggregate in SQL
        return schemas.TestReport(
            details=test.details,
            attachments=sorted(test.attachments, key=lambda a: a.get('name', '')) if test.attachments[0] else [],
            logs=sorted(test.logs, key=lambda l: l.get('name', '')) if test.logs[0] else [],
            metrics=metrics,
            requests=sorted(test.requests,
                            key=lambda t: fix_timestamp(
                                t.get('timestamp', datetime.datetime.utcnow().isoformat()))
                            ) if test.requests[0] else []
        )

    async def get_test_run_metrics_and_properties(self,
                                                  project_id: UUID,
                                                  test_run_id: UUID,
                                                  result: list[str] | None,
                                                  search: list[str] | None,
                                                  metrics: list[schemas.MetricRequest] | None = None) -> schemas.MetricsAggregate:
        test_filters = and_(*get_test_filter(test_run_id, result, search))

        tests = select(
            func.distinct(models.Test.id)
        ).where(
            and_(*test_filters)
        ).subquery()

        metrics_sql = []
        properties_sql = []
        metrics_ot_sql = []
        for metric in metrics:
            if metric.table == 'metrics':
                metrics_sql.append(
                    func.max(
                        models.Metric.value
                    ).filter(
                        models.Metric.name == metric.name
                    ).label(metric.title)
                )
            elif metric.table == 'properties':
                path = '->'.join([f"'{node}'" for node in metric.path])
                properties_sql.append(
                    text(f"test_runs.properties::jsonb->{path} as \"{metric.title}\"")
                )
            elif metric.table == 'metrics_over_time':
                aggregate = getattr(func, metric.func)(cast(models.MetricOverTime.values[metric.field], Float))
                col_filter = models.MetricOverTime.name == metric.name
                if metric.filter:
                    aggregate = aggregate.filter(
                        and_(
                            col_filter,
                            text(f"cast(metrics_over_time.values::jsonb->'{metric.filter_field}' as float) "
                                 f"{metric.filter}"))
                    )
                metrics_ot_sql.append(
                    aggregate.label(metric.title)
                )

        tr_properties = (
            await self.session.execute(
                select(
                    *properties_sql
                ).where(
                    models.TestRun.id == test_run_id
                )
            )
        ).first()

        tr_metrics = (
            await self.session.execute(
                select(
                    *metrics_sql
                ).where(
                    models.Metric.test_run_id == test_run_id
                )
            )
        ).first()

        tr_ot_metrics = (
            await self.session.execute(
                select(
                    *metrics_ot_sql
                ).where(
                    models.MetricOverTime.test_id.in_(tests)
                )
            )
        ).first()

        result = schemas.MetricsAggregate(data=[])
        for metric in metrics:
            if metric.table == 'metrics':
                table = tr_metrics
            elif metric.table == 'properties':
                table = tr_properties
            else:
                table = tr_ot_metrics
            result.data.append(
                schemas.MetricsData(
                    name=metric.title,
                    value=table[metric.title]
                )
            )

        return result
