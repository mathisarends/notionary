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


class UnsupportedVideoFormatError(ValueError):
    def __init__(self, url: str, supported_formats: list[str]) -> None:
        self.url = url
        self.supported_formats = supported_formats
        super().__init__(self._create_user_friendly_message())

    def _create_user_friendly_message(self) -> str:
        formats = ", ".join(self.supported_formats[:5])
        remaining = len(self.supported_formats) - 5

        if remaining > 0:
            formats += f" and {remaining} more"

        return (
            f"The video URL '{self.url}' uses an unsupported format.\n"
            f"Supported formats include: {formats}.\n"
            f"YouTube embed and watch URLs are also supported."
            f"Also see https://developers.notion.com/reference/block#video for more information."
        )
