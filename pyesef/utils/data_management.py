"""Data management utils."""

from dataclasses import asdict as std_asdict


def asdict_with_properties(obj):
    """
    Allow setting properties on a dataclass.

    From https://stackoverflow.com/a/64778375.
    """
    return {
        **std_asdict(obj),
        **{a: getattr(obj, a) for a in getattr(obj, "__add_to_dict__", [])},
    }
