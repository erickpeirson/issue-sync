from enum import EnumMeta
from typing import Any, Union, List

from arxiv.util.serialize import ISO8601JSONEncoder


class EnumJSONEncoder(ISO8601JSONEncoder):
    """Renders enum values as native Python values."""

    def default(self, obj: Any) -> Union[str, List[Any]]:
        """Overriden to render date(time)s in isoformat."""
        try:
            if isinstance(type(obj), EnumMeta):
                return obj.value
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return ISO8601JSONEncoder.default(self, obj)  # type: ignore