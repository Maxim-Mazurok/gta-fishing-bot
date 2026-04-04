"""Generic markdown table formatting utility."""


def format_markdown_table(
    headers: tuple[str, ...],
    rows: list[tuple[str, ...]],
    right_aligned_columns: set[int] | None = None,
) -> str:
    """Build a padded markdown table with auto-calculated column widths.

    Args:
        headers: Column header labels.
        rows: Data rows (each a tuple of strings, same length as headers).
        right_aligned_columns: Set of 0-based column indices to right-align.
    """
    if right_aligned_columns is None:
        right_aligned_columns = set()

    column_count = len(headers)
    widths = [
        max(
            len(headers[column]),
            max((len(row[column]) for row in rows), default=0),
        )
        for column in range(column_count)
    ]

    def format_row(values: tuple[str, ...]) -> str:
        return "| " + " | ".join(
            f"{value:>{widths[column]}}" if column in right_aligned_columns
            else f"{value:<{widths[column]}}"
            for column, value in enumerate(values)
        ) + " |"

    separator = "|"
    for column in range(column_count):
        if column in right_aligned_columns:
            separator += f"{'-' * (widths[column] + 1)}:|"
        else:
            separator += f"{'-' * (widths[column] + 2)}|"

    lines = [format_row(headers), separator]
    for row in rows:
        lines.append(format_row(row))
    return "\n".join(lines)
