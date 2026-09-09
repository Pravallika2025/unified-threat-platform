from fastapi import APIRouter, Depends

from app.core.unit_of_work import UnitOfWorkRoute
from app.core.security.dependencies import CurrentUser, get_current_user
from app.modules.detection.domain.entities import Severity
from app.modules.risk.domain.scoring_model import compute
from app.modules.risk.schemas import RiskBreakdown

router = APIRouter(route_class=UnitOfWorkRoute, prefix="/risk", tags=["risk"])


@router.get("/explain", response_model=RiskBreakdown)
async def explain_score(
    severity: Severity,
    environment_type: str = "enterprise",
    event_count: int = 1,
    intel_confirmed: bool = False,
    _: CurrentUser = Depends(get_current_user),
):
    """Shows exactly how a score is built. Analysts should be able to audit the maths."""
    result = compute(
        severity=severity,
        environment_type=environment_type,
        event_count=event_count,
        intel_confirmed=intel_confirmed,
    )
    return RiskBreakdown(score=result.score, band=result.band, factors=result.factors)
