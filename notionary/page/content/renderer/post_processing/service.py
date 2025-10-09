from notionary.page.content.parser.post_processing.port import PostProcessor


class MarkdownRenderingPostProcessor:
    def __init__(self) -> None:
        self._processors: list[PostProcessor] = []

    def register(self, processor: PostProcessor) -> None:
        self._processors.append(processor)

    def process(self, markdown_text: str) -> str:
        result = markdown_text
        for processor in self._processors:
            result = processor.process(result)
        return result
