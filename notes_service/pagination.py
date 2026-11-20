"""Shared pagination argument parsing."""
from flask import abort

DEFAULT_PER_PAGE = 20
MAX_PER_PAGE = 100


def parse_page_args(args) -> tuple[int, int]:
    """Parse and validate `page` (1-based) and `per_page` query params.

    Returns:
        (page, per_page) as ints. Aborts with 400 on bad input.
    """
    try:
        page = int(args.get("page", 1))
        per_page = int(args.get("per_page", DEFAULT_PER_PAGE))
    except ValueError:
        abort(400, "page and per_page must be integers")
    if page < 1 or not 1 <= per_page <= MAX_PER_PAGE:
        abort(400, f"page must be >= 1 and per_page between 1 and {MAX_PER_PAGE}")
    return page, per_page
