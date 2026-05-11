from sqlalchemy import inspect as sa_inspect


def _to_dict(self) -> dict:
    return {c.key: getattr(self, c.key) for c in sa_inspect(self).mapper.column_attrs}
