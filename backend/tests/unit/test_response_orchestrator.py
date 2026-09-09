import pytest

from app.modules.response.domain.action_type import ActionType
from app.modules.response.infrastructure.executors.account_disable_executor import (
    AccountDisableExecutor,
)
from app.modules.response.infrastructure.executors.edr_isolate_executor import (
    EdrIsolateExecutor,
)
from app.modules.response.infrastructure.executors.firewall_executor import (
    FirewallExecutor,
)


@pytest.mark.asyncio
async def test_firewall_executor_allowlist_and_rollback():
    executor = FirewallExecutor()

    # 1. Protection on localhost / DNS
    res_allow = await executor.execute(target="127.0.0.1", params={})
    assert res_allow.success is False
    assert "allowlist" in res_allow.message

    # 2. Block malicious target
    res_block = await executor.execute(target="203.0.113.99", params={"protocol": "tcp"})
    assert res_block.success is True
    assert res_block.rollback_token is not None

    # 3. Rollback
    res_rollback = await executor.rollback(rollback_token=res_block.rollback_token)
    assert res_rollback.success is True
    assert "unblocked" in res_rollback.message


@pytest.mark.asyncio
async def test_account_disable_and_edr_executors():
    acct = AccountDisableExecutor()
    res_acct = await acct.execute(target="compromised_user", params={})
    assert res_acct.success is True
    assert res_acct.rollback_token is not None

    rb_acct = await acct.rollback(rollback_token=res_acct.rollback_token)
    assert rb_acct.success is True

    edr = EdrIsolateExecutor()
    res_edr = await edr.execute(target="laptop-finance-02", params={})
    assert res_edr.success is True
    assert res_edr.rollback_token is not None

    rb_edr = await edr.rollback(rollback_token=res_edr.rollback_token)
    assert rb_edr.success is True
