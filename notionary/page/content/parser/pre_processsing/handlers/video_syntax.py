import re
from typing import override
from urllib.parse import urlparse

from notionary.blocks.enums import VideoFileType
from notionary.exceptions import UnsupportedVideoFormatError
from notionary.page.content.parser.pre_processsing.handlers.port import PreProcessor
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry
from notionary.utils.decorators import time_execution_sync
from notionary.utils.mixins.logging import LoggingMixin


class VideoFormatPreProcessor(PreProcessor, LoggingMixin):
    YOUTUBE_WATCH_PATTERN = re.compile(r"^https?://(?:www\.)?youtube\.com/watch\?.*v=[\w-]+", re.IGNORECASE)
    YOUTUBE_EMBED_PATTERN = re.compile(r"^https?://(?:www\.)?youtube\.com/embed/[\w-]+", re.IGNORECASE)

    def __init__(self, syntax_registry: SyntaxDefinitionRegistry | None = None) -> None:
        super().__init__()
        self._syntax_registry = syntax_registry or SyntaxDefinitionRegistry()
        self._video_syntax = self._syntax_registry.get_video_syntax()

    @override
    @time_execution_sync()
    def process(self, markdown_text: str) -> str:
        lines = markdown_text.split("\n")
        validated_lines = [self._validate_or_reject_line(line) for line in lines]
        return "\n".join(validated_lines)

    def _validate_or_reject_line(self, line: str) -> str:
        if not self._contains_video_block(line):
            return line

        url = self._extract_url_from_video_block(line)

        if self._is_supported_video_url(url):
            return line

        supported_formats = list(VideoFileType.get_all_extensions())
        raise UnsupportedVideoFormatError(url, supported_formats)

    def _contains_video_block(self, line: str) -> bool:
        return self._video_syntax.regex_pattern.search(line) is not None

    def _extract_url_from_video_block(self, line: str) -> str:
        match = self._video_syntax.regex_pattern.search(line)
        return match.group(1).strip() if match else ""

    def _is_supported_video_url(self, url: str) -> bool:
        return (
            self._is_youtube_video(url)
            or self._has_valid_video_extension(url)
            or self._url_path_has_valid_extension(url)
        )

    def _is_youtube_video(self, url: str) -> bool:
        return bool(self.YOUTUBE_WATCH_PATTERN.match(url) or self.YOUTUBE_EMBED_PATTERN.match(url))

    def _has_valid_video_extension(self, url: str) -> bool:
        return VideoFileType.is_valid_extension(url)

    def _url_path_has_valid_extension(self, url: str) -> bool:
        try:
            parsed_url = urlparse(url)
            return VideoFileType.is_valid_extension(parsed_url.path.lower())
        except Exception:
            return False
