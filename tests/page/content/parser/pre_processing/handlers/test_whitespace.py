from textwrap import dedent

import pytest

from notionary.page.content.parser.pre_processsing.handlers.whitespace import WhitespacePreProcessor


@pytest.fixture
def processor() -> WhitespacePreProcessor:
    """Fixture that provides a WhitespacePreProcessor instance."""
    return WhitespacePreProcessor()


def test_empty_string_should_return_empty(processor: WhitespacePreProcessor) -> None:
    result = processor.process("")
    assert result == ""


def test_only_whitespace_should_return_empty_lines(processor: WhitespacePreProcessor) -> None:
    markdown = "   \n  \n\t\n"
    result = processor.process(markdown)
    assert result == "\n\n\n"


def test_simple_text_without_code_blocks_should_remove_leading_whitespace(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        # Heading
            Indented text
          Less indented
        Normal
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        # Heading
        Indented text
        Less indented
        Normal
        """
    )
    assert result == expected


def test_text_with_various_indentation_levels(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
                Deep indent
            Medium indent
          Small indent
        No indent
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        Deep indent
        Medium indent
        Small indent
        No indent
        """
    )
    assert result == expected


def test_code_block_should_preserve_relative_indentation(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        Text before code
        ```python
            def hello():
                print("world")
        ```
        Text after code
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        Text before code
        ```python
        def hello():
            print("world")
        ```
        Text after code
        """
    )
    assert result == expected


def test_code_block_with_different_indentation_levels(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        ```python
            if True:
                print("nested")
            print("less nested")
        ```
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        ```python
        if True:
            print("nested")
        print("less nested")
        ```
        """
    )
    assert result == expected


def test_code_block_with_deep_indentation(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        ```python
                def deeply_indented():
                    return True
        ```
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        ```python
        def deeply_indented():
            return True
        ```
        """
    )
    assert result == expected


def test_multiple_code_blocks_should_be_processed_independently(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        Erster Block:
        ```python
            def first():
                pass
        ```

        Zweiter Block:
        ```javascript
              const second = () => {
                  return true;
              };
        ```
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        Erster Block:
        ```python
        def first():
            pass
        ```

        Zweiter Block:
        ```javascript
        const second = () => {
            return true;
        };
        ```
        """
    )
    assert result == expected


def test_consecutive_code_blocks_without_text_between(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        ```python
            code1
        ```
        ```javascript
            code2
        ```
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        ```python
        code1
        ```
        ```javascript
        code2
        ```
        """
    )
    assert result == expected


def test_code_block_at_start_of_document(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        ```python
            def first():
                pass
        ```
        Text after
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        ```python
        def first():
            pass
        ```
        Text after
        """
    )
    assert result == expected


def test_code_block_at_end_of_document(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        Text before
        ```python
            def last():
                pass
        ```
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        Text before
        ```python
        def last():
            pass
        ```
        """
    )
    assert result == expected


def test_code_block_without_language_should_work(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        ```
            some code
                more indented
        ```
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        ```
        some code
            more indented
        ```
        """
    )
    assert result == expected


def test_code_block_with_language_and_extra_info(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        ```python filename="test.py"
            code here
        ```
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        ```python filename="test.py"
        code here
        ```
        """
    )
    assert result == expected


def test_empty_lines_in_code_block_should_be_preserved(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        ```python
            def hello():

                print("world")
        ```
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        ```python
        def hello():

            print("world")
        ```
        """
    )
    assert result == expected


def test_multiple_empty_lines_in_code_block(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        ```python
            line1


            line2
        ```
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        ```python
        line1


        line2
        ```
        """
    )
    assert result == expected


def test_code_block_with_no_content_should_work(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        ```python
        ```
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        ```python
        ```
        """
    )
    assert result == expected


def test_code_block_with_only_empty_lines_should_preserve_them(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        ```python


        ```
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        ```python


        ```
        """
    )
    assert result == expected


def test_code_block_with_only_whitespace_lines(processor: WhitespacePreProcessor) -> None:
    markdown = "```python\n    \n        \n```"
    result = processor.process(markdown)
    expected = "```python\n\n\n```"
    assert result == expected


def test_mixed_content_with_lists_and_code(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
          # Heading

          - List
            - Nested

          ```python
              def example():
                  return 42
          ```

          Further text
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        # Heading

        - List
        - Nested

        ```python
        def example():
            return 42
        ```

        Further text
        """
    )
    assert result == expected


def test_code_fence_with_leading_whitespace_should_be_recognized(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
            ```python
                code
            ```
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        ```python
        code
        ```
        """
    )
    assert result == expected


def test_code_fence_with_different_leading_whitespace_amounts(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
          ```python
              code line 1
                  code line 2
          ```
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        ```python
        code line 1
            code line 2
        ```
        """
    )
    assert result == expected


def test_code_block_already_normalized_should_remain_unchanged(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        ```python
        def hello():
            print("world")
        ```
        """
    )
    result = processor.process(markdown)
    assert result == markdown


def test_code_block_with_no_indentation_should_remain_unchanged(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        ```python
        no indent
        still no indent
        ```
        """
    )
    result = processor.process(markdown)
    assert result == markdown


def test_mixed_list_and_text_indentation(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
            - Item 1
              - Item 1.1
            - Item 2

            Regular text
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        - Item 1
        - Item 1.1
        - Item 2

        Regular text
        """
    )
    assert result == expected


def test_blockquote_with_indentation(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
            > Quote line 1
            > Quote line 2
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        > Quote line 1
        > Quote line 2
        """
    )
    assert result == expected


def test_complex_document_with_everything(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
          # Main Heading

              Indented paragraph

          ## Subheading

          - List item
            - Nested item

          ```python
              def function():
                  if True:
                      return 42
          ```

          > Blockquote
          > continues

          More text
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        # Main Heading

        Indented paragraph

        ## Subheading

        - List item
        - Nested item

        ```python
        def function():
            if True:
                return 42
        ```

        > Blockquote
        > continues

        More text
        """
    )
    assert result == expected


def test_code_block_with_mixed_empty_and_content_lines(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        ```python
            def test():

                pass

        ```
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        ```python
        def test():

            pass

        ```
        """
    )
    assert result == expected


def test_single_line_code_block(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        ```python
            single_line()
        ```
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        ```python
        single_line()
        ```
        """
    )
    assert result == expected


def test_code_block_with_trailing_whitespace_in_lines(processor: WhitespacePreProcessor) -> None:
    """Test that trailing whitespace in code lines is handled correctly."""
    markdown = "```python\n    code    \n        more    \n```"
    result = processor.process(markdown)
    expected = "```python\ncode    \n    more    \n```"
    assert result == expected
