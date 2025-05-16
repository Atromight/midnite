from typing import List, Set
from unittest.mock import patch

from midnite_api.alerts import add_code_1100, add_code_30, add_code_300, add_code_123
from midnite_api.models import Event
from midnite_api.const import AlertCode, EventType
from midnite_api.schemas import EventSchema


class TestAlerts:
    test_add_code_1100_scenarios = [
        dict(
            description="""add_code_1100 triggers alert on withdraw over 100""",
            alert_codes=set(),
            event=EventSchema(user_id=1, amount=101.0, t=5, type=EventType.WITHDRAW),
            expected_alert_codes=set([AlertCode.CODE_1100]),
        ),
        dict(
            description="""add_code_1100 does NOT trigger alert on withdraw under 100""",
            alert_codes=set(),
            event=EventSchema(user_id=1, amount=99.0, t=5, type=EventType.WITHDRAW),
            expected_alert_codes=set(),
        ),
    ]

    def test_add_code_1100(
        self,
        alert_codes: Set[AlertCode],
        event: EventSchema,
        expected_alert_codes: Set[AlertCode],
    ) -> None:
        add_code_1100(alert_codes, event)

        assert alert_codes == expected_alert_codes

    test_add_code_30_scenarios = [
        dict(
            description="add_code_30 triggers when 3 last events are withdrawals",
            alert_codes=set(),
            event=EventSchema(user_id=1, amount=100.0, t=4, type=EventType.WITHDRAW),
            mock_events=[
                Event(user_id=1, amount=10.0, t=3, type=EventType.WITHDRAW),
                Event(user_id=1, amount=20.0, t=2, type=EventType.WITHDRAW),
                Event(user_id=1, amount=30.0, t=1, type=EventType.WITHDRAW),
            ],
            expected_alert_codes={AlertCode.CODE_30},
        ),
        dict(
            description="add_code_30 does NOT trigger if not all 3 last events are withdrawals",
            alert_codes=set(),
            event=EventSchema(user_id=1, amount=100.0, t=4, type=EventType.WITHDRAW),
            mock_events=[
                Event(user_id=1, amount=10.0, t=3, type=EventType.WITHDRAW),
                Event(user_id=1, amount=20.0, t=2, type=EventType.DEPOSIT),
                Event(user_id=1, amount=30.0, t=1, type=EventType.WITHDRAW),
            ],
            expected_alert_codes=set(),
        ),
    ]

    @patch("midnite_api.alerts.fetch_latest_n_user_events")
    def test_add_code_30(
        self,
        mock_fetch,
        alert_codes: Set[AlertCode],
        event: EventSchema,
        mock_events: List[Event],
        expected_alert_codes: Set[AlertCode],
    ) -> None:
        mock_fetch.return_value = mock_events
        add_code_30(alert_codes, event, db=None)

        assert alert_codes == expected_alert_codes

    test_add_code_300_scenarios = [
        dict(
            description="add_code_300 triggers alert when last 3 deposits are increasing",
            alert_codes=set(),
            event=EventSchema(user_id=1, amount=40.0, t=4, type=EventType.DEPOSIT),
            db_return_value=[
                Event(type=EventType.DEPOSIT, amount=40.0, user_id=1, t=4),
                Event(type=EventType.DEPOSIT, amount=30.0, user_id=1, t=3),
                Event(type=EventType.DEPOSIT, amount=20.0, user_id=1, t=2),
            ],
            expected_alert_codes={AlertCode.CODE_300},
        ),
        dict(
            description="add_code_300 does not trigger alert when deposits are not strictly increasing",
            alert_codes=set(),
            event=EventSchema(user_id=1, amount=30.0, t=4, type=EventType.DEPOSIT),
            db_return_value=[
                Event(type=EventType.DEPOSIT, amount=30.0, user_id=1, t=4),
                Event(type=EventType.DEPOSIT, amount=40.0, user_id=1, t=3),
                Event(type=EventType.DEPOSIT, amount=20.0, user_id=1, t=2),
            ],
            expected_alert_codes=set(),
        ),
    ]

    @patch("midnite_api.alerts.fetch_latest_n_user_deposits")
    def test_add_code_300(
        self,
        mock_fetch,
        alert_codes,
        event,
        db_return_value,
        expected_alert_codes,
    ):
        mock_fetch.return_value = db_return_value
        add_code_300(alert_codes, event, db=None)

        assert alert_codes == expected_alert_codes

    test_add_code_123_scenarios = [
        dict(
            description="add_code_123 triggers alert when deposits in last 30s >= 200",
            alert_codes=set(),
            event=EventSchema(user_id=1, amount=150.0, t=32, type=EventType.DEPOSIT),
            expected_alert_codes={AlertCode.CODE_123},
            mock_sum_return=250.0,
        ),
        dict(
            description="add_code_123 does not trigger alert when deposits < 200",
            alert_codes=set(),
            event=EventSchema(user_id=1, amount=100.0, t=32, type=EventType.DEPOSIT),
            expected_alert_codes=set(),
            mock_sum_return=150.0,
        ),
    ]

    @patch("midnite_api.alerts.fetch_sum_user_deposits_min_t")
    def test_add_code_123(
        self,
        mock_fetch_sum,
        alert_codes: Set[AlertCode],
        event: EventSchema,
        expected_alert_codes: Set[AlertCode],
        mock_sum_return: float,
    ) -> None:
        mock_fetch_sum.return_value = mock_sum_return
        add_code_123(alert_codes, event, db=None)

        assert alert_codes == expected_alert_codes
