from enum import StrEnum


class ActionType(StrEnum):
    BLOCK_IP = "block_ip"
    BLOCK_PORT = "block_port"
    BLOCK_URL = "block_url"
    ISOLATE_HOST = "isolate_host"
    DISABLE_ACCOUNT = "disable_account"
    KILL_PROCESS = "kill_process"
    MONITOR = "monitor"
    NOTIFY_ONLY = "notify_only"


DESTRUCTIVE: set[ActionType] = {
    ActionType.BLOCK_IP,
    ActionType.BLOCK_PORT,
    ActionType.BLOCK_URL,
    ActionType.ISOLATE_HOST,
    ActionType.DISABLE_ACCOUNT,
    ActionType.KILL_PROCESS,
}


def is_destructive(action: ActionType) -> bool:
    return action in DESTRUCTIVE


class ActionStatus(StrEnum):
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    EXECUTING = "executing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
