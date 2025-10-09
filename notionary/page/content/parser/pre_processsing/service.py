from notionary.page.content.parser.pre_processsing.handlers.port import PreProcessor


class MarkdownPreProcessor:
    def __init__(self) -> None:
        self._processors: list[PreProcessor] = []

    def register(self, processor: PreProcessor) -> None:
        self._processors.append(processor)

    def process(self, markdown_text: str) -> str:
        result = markdown_text
        for processor in self._processors:
            result = processor.process(result)
        return result
