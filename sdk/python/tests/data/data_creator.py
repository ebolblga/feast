from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo

import pandas as pd

from feast.types import FeastType, Float32, Int32, Int64, String
from feast.utils import _utc_now


def create_basic_driver_dataset(
    entity_type: FeastType = Int32,
    feature_dtype: Optional[str] = None,
    feature_is_list: bool = False,
    list_has_empty_list: bool = False,
) -> pd.DataFrame:
    now = _utc_now().replace(microsecond=0, second=0, minute=0)
    ts = pd.Timestamp(now).round("ms")
    data = {
        "driver_id": get_entities_for_feast_type(entity_type),
        "value": get_feature_values_for_dtype(
            feature_dtype, feature_is_list, list_has_empty_list
        ),
        "ts_1": [
            ts - timedelta(hours=4),
            ts,
            ts - timedelta(hours=3),
            # Use different time zones to test tz-naive -> tz-aware conversion
            (ts - timedelta(hours=4))
            .replace(tzinfo=timezone.utc)
            .astimezone(tz=ZoneInfo("Europe/Berlin")),
            (ts - timedelta(hours=1))
            .replace(tzinfo=timezone.utc)
            .astimezone(tz=ZoneInfo("US/Pacific")),
        ],
        "created_ts": [ts, ts, ts, ts, ts],
    }
    return pd.DataFrame.from_dict(data)


def get_entities_for_feast_type(feast_type: FeastType) -> List:
    feast_type_map: Dict[FeastType, List] = {
        Int32: [1, 2, 1, 3, 3],
        Int64: [1, 2, 1, 3, 3],
        Float32: [1.0, 2.0, 1.0, 3.0, 3.0],
        String: ["1", "2", "1", "3", "3"],
    }
    return feast_type_map[feast_type]


def get_feature_values_for_dtype(
    dtype: Optional[str], is_list: bool, has_empty_list: bool
) -> List:
    if dtype is None:
        return [0.1, None, 0.3, 4, 5]
    # TODO(adchia): for int columns, consider having a better error when dealing with None values (pandas int dfs can't
    #  have na)
    dtype_map: Dict[str, List] = {
        "int32": [1, 2, 3, 4, 5],
        "int64": [1, 2, 3, 4, 5],
        "float": [1.0, None, 3.0, 4.0, 5.0],
        "string": ["1", None, "3", "4", "5"],
        "bytes": [b"1", None, b"3", b"4", b"5"],
        "bool": [True, None, False, True, False],
        "datetime": [
            datetime(1980, 1, 1),
            None,
            datetime(1981, 1, 1),
            datetime(1982, 1, 1),
            datetime(1982, 1, 1),
        ],
    }
    non_list_val = dtype_map[dtype]
    if is_list:
        # TODO: Add test where all lists are empty and type inference is expected to fail.
        if has_empty_list:
            # Need at least one non-empty element for type inference
            return [[] for n in non_list_val[:-1]] + [non_list_val[-1:]]
        return [[n, n] if n is not None else None for n in non_list_val]
    else:
        return non_list_val


def create_document_dataset() -> pd.DataFrame:
    data = {
        "item_id": [1, 2, 3],
        "string_feature": ["a", "b", "c"],
        "float_feature": [1.0, 2.0, 3.0],
        "embedding_float": [[4.0, 5.0], [1.0, 2.0], [3.0, 4.0]],
        "embedding_double": [[4.0, 5.0], [1.0, 2.0], [3.0, 4.0]],
        "ts": [
            pd.Timestamp(_utc_now()).round("ms"),
            pd.Timestamp(_utc_now()).round("ms"),
            pd.Timestamp(_utc_now()).round("ms"),
        ],
        "created_ts": [
            pd.Timestamp(_utc_now()).round("ms"),
            pd.Timestamp(_utc_now()).round("ms"),
            pd.Timestamp(_utc_now()).round("ms"),
        ],
    }
    return pd.DataFrame(data)
