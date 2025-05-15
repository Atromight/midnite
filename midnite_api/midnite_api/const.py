from enum import IntEnum, StrEnum


APP_NAME = "midnite_api"


class AlertCode(IntEnum):
    CODE_30 = 30  # 3 consecutive withdraws
    CODE_123 = (
        123  # Accumulative deposit amount over a window of 30 seconds is over 200
    )
    CODE_300 = 300  # 3 consecutive increasing deposits (ignoring withdraws)
    CODE_1100 = 1100  # A withdraw amount over 100


class EventType(StrEnum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
