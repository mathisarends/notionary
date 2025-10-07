from notionary.exceptions.base import NotionaryError

RATIO_TOLERANCE = 0.0001


class InsufficientColumnsError(NotionaryError):
    def __init__(self, column_count: int) -> None:
        self.column_count = column_count
        super().__init__(f"Columns container must contain at least 2 column blocks, but only {column_count} found")


class InvalidColumnRatioSumError(NotionaryError):
    def __init__(self, total: float, tolerance: float = RATIO_TOLERANCE) -> None:
        self.total = total
        self.tolerance = tolerance
        super().__init__(f"Width ratios must sum to 1.0 (±{tolerance}), but sum is {total}")
