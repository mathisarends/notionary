from unittest.mock import Mock

import pytest

from notionary.blocks.enums import VideoFileType
from notionary.exceptions import UnsupportedVideoFormatError
from notionary.page.content.parser.pre_processsing.handlers import (
    VideoFormatPreProcessor,
)
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


@pytest.fixture
def preprocessor(syntax_registry: SyntaxDefinitionRegistry) -> VideoFormatPreProcessor:
    processor = VideoFormatPreProcessor(syntax_registry)
    processor.logger = Mock()
    return processor


@pytest.fixture
def valid_mp4_video() -> str:
    return "[video](https://example.com/video.mp4)"


@pytest.fixture
def valid_youtube_watch_video() -> str:
    return "[video](https://www.youtube.com/watch?v=dQw4w9WgXcQ)"


@pytest.fixture
def valid_youtube_embed_video() -> str:
    return "[video](https://www.youtube.com/embed/dQw4w9WgXcQ)"


@pytest.fixture
def invalid_video() -> str:
    return "[video](https://example.com/document.pdf)"


@pytest.fixture
def multiline_markdown(
    valid_mp4_video: str,
    valid_youtube_watch_video: str,
    invalid_video: str,
) -> str:
    """Markdown with multiple video blocks."""
    return f"""
# My Document

Some text here.

{valid_mp4_video}

More text.

{valid_youtube_watch_video}

{invalid_video}

Final text.
"""


class TestVideoFormatValidation:
    def test_validates_mp4_extension(self, preprocessor: VideoFormatPreProcessor) -> None:
        assert preprocessor._is_supported_video_url("https://example.com/video.mp4")

    def test_validates_all_supported_extensions(self, preprocessor: VideoFormatPreProcessor) -> None:
        for video_type in VideoFileType:
            url = f"https://example.com/video{video_type.value}"
            assert preprocessor._is_supported_video_url(url)

    def test_validates_youtube_watch_url(self, preprocessor: VideoFormatPreProcessor) -> None:
        assert preprocessor._is_supported_video_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert preprocessor._is_supported_video_url("https://youtube.com/watch?v=dQw4w9WgXcQ")

    def test_validates_youtube_embed_url(self, preprocessor: VideoFormatPreProcessor) -> None:
        assert preprocessor._is_supported_video_url("https://www.youtube.com/embed/dQw4w9WgXcQ")
        assert preprocessor._is_supported_video_url("https://youtube.com/embed/dQw4w9WgXcQ")

    def test_rejects_unsupported_extension(self, preprocessor: VideoFormatPreProcessor) -> None:
        assert not preprocessor._is_supported_video_url("https://example.com/file.pdf")
        assert not preprocessor._is_supported_video_url("https://example.com/file.txt")

    def test_rejects_vimeo_urls(self, preprocessor: VideoFormatPreProcessor) -> None:
        assert not preprocessor._is_supported_video_url("https://vimeo.com/123456789")

    def test_validates_case_insensitive_extensions(self, preprocessor: VideoFormatPreProcessor) -> None:
        assert preprocessor._is_supported_video_url("https://example.com/video.MP4")
        assert preprocessor._is_supported_video_url("https://example.com/video.Mp4")


class TestVideoBlockDetection:
    def test_detects_video_block(self, preprocessor: VideoFormatPreProcessor, valid_mp4_video: str) -> None:
        assert preprocessor._contains_video_block(valid_mp4_video)

    def test_ignores_non_video_lines(self, preprocessor: VideoFormatPreProcessor) -> None:
        assert not preprocessor._contains_video_block("# Heading")
        assert not preprocessor._contains_video_block("Some text")
        assert not preprocessor._contains_video_block("[image](url.png)")

    def test_extracts_url_from_video_block(self, preprocessor: VideoFormatPreProcessor, valid_mp4_video: str) -> None:
        url = preprocessor._extract_url_from_video_block(valid_mp4_video)
        assert url == "https://example.com/video.mp4"


class TestMarkdownProcessing:
    def test_preserves_valid_video_blocks(self, preprocessor: VideoFormatPreProcessor, valid_mp4_video: str) -> None:
        result = preprocessor.process(valid_mp4_video)
        assert result == valid_mp4_video

    def test_raises_error_for_invalid_video_blocks(
        self, preprocessor: VideoFormatPreProcessor, invalid_video: str
    ) -> None:
        with pytest.raises(UnsupportedVideoFormatError):
            preprocessor.process(invalid_video)

    def test_preserves_non_video_lines(self, preprocessor: VideoFormatPreProcessor) -> None:
        markdown = "# Heading\n\nSome text\n\n- List item"
        result = preprocessor.process(markdown)
        assert result == markdown

    def test_processes_multiline_markdown_with_invalid_video(
        self,
        preprocessor: VideoFormatPreProcessor,
        valid_mp4_video: str,
        valid_youtube_watch_video: str,
        invalid_video: str,
    ) -> None:
        markdown = f"{valid_mp4_video}\n{valid_youtube_watch_video}\n{invalid_video}"
        with pytest.raises(UnsupportedVideoFormatError):
            preprocessor.process(markdown)

    def test_preserves_youtube_videos(
        self,
        preprocessor: VideoFormatPreProcessor,
        valid_youtube_watch_video: str,
        valid_youtube_embed_video: str,
    ) -> None:
        markdown = f"{valid_youtube_watch_video}\n{valid_youtube_embed_video}"
        result = preprocessor.process(markdown)

        assert valid_youtube_watch_video in result
        assert valid_youtube_embed_video in result


class TestErrorHandling:
    def test_exception_contains_user_friendly_message(self) -> None:
        url = "https://example.com/video.pdf"
        supported = [".mp4", ".avi", ".mov"]

        error = UnsupportedVideoFormatError(url, supported)
        message = str(error)

        assert url in message
        assert "unsupported format" in message.lower()
        assert ".mp4" in message
        assert "YouTube" in message


class TestEdgeCases:
    def test_handles_empty_markdown(self, preprocessor: VideoFormatPreProcessor) -> None:
        result = preprocessor.process("")
        assert result == ""

    def test_handles_whitespace_only_markdown(self, preprocessor: VideoFormatPreProcessor) -> None:
        markdown = "   \n\n   "
        result = preprocessor.process(markdown)
        assert result == markdown

    def test_handles_video_url_with_query_parameters(self, preprocessor: VideoFormatPreProcessor) -> None:
        markdown = "[video](https://example.com/video.mp4?autoplay=1&muted=1)"
        result = preprocessor.process(markdown)
        assert result == markdown

    def test_handles_malformed_video_syntax(self, preprocessor: VideoFormatPreProcessor) -> None:
        """Test that malformed video syntax is ignored."""
        markdown = "[video(https://example.com/video.mp4)"
        result = preprocessor.process(markdown)
        assert result == markdown
