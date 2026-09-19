from fastapi import APIRouter

from app.api.unit_of_work import UnitOfWorkRoute

from app.api.v1.routes import (
    alerts,
    audit,
    auth,
    dashboard,
    environments,
    events,

    incidents,
    ingestion,
    investigation,
    reports,
    response,
    review,
    risk,
    threat_intel,
    users,
)

api_router = APIRouter(route_class=UnitOfWorkRoute)

for module in (

    auth,
    users,
    environments,
    ingestion,
    events,
    alerts,
    incidents,
    investigation,
    review,
    response,
    risk,
    threat_intel,
    dashboard,
    reports,
    audit,
):
    api_router.include_router(module.router)
