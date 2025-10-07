from textwrap import dedent

from notionary.page.content.parser.pre_processsing.whitespace import process_markdown_whitespace


def test_empty_string_should_return_empty() -> None:
    result = process_markdown_whitespace("")
    assert result == ""


def test_simple_text_without_code_blocks_should_remove_leading_whitespace() -> None:
    markdown = dedent(
        """
        # Heading
            Indented text
          Less indented
        Normal
        """
    )
    result = process_markdown_whitespace(markdown)

    expected = dedent(
        """
        # Heading
        Indented text
        Less indented
        Normal
        """
    )
    assert result == expected


def test_code_block_should_preserve_relative_indentation() -> None:
    markdown = dedent(
        """
        Text vor Code
        ```python
            def hello():
                print("world")
        ```
        Text nach Code
        """
    )
    result = process_markdown_whitespace(markdown)

    expected = dedent(
        """
        Text vor Code
        ```python
        def hello():
            print("world")
        ```
        Text nach Code
        """
    )
    assert result == expected


def test_code_block_with_different_indentation_levels() -> None:
    markdown = dedent(
        """
        ```python
            if True:
                print("nested")
            print("less nested")
        ```
        """
    )
    result = process_markdown_whitespace(markdown)

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


def test_multiple_code_blocks_should_be_processed_independently() -> None:
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
    result = process_markdown_whitespace(markdown)

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


def test_code_block_without_language_should_work() -> None:
    markdown = dedent(
        """
        ```
            some code
                more indented
        ```
        """
    )
    result = process_markdown_whitespace(markdown)

    expected = dedent(
        """
        ```
        some code
            more indented
        ```
        """
    )
    assert result == expected


def test_empty_lines_in_code_block_should_be_preserved() -> None:
    markdown = dedent(
        """
        ```python
            def hello():

                print("world")
        ```
        """
    )
    result = process_markdown_whitespace(markdown)

    expected = dedent(
        """
        ```python
        def hello():

            print("world")
        ```
        """
    )
    assert result == expected


def test_code_block_with_no_content_should_work() -> None:
    markdown = dedent(
        """
        ```python
        ```
        """
    )
    result = process_markdown_whitespace(markdown)

    expected = dedent(
        """
        ```python
        ```
        """
    )
    assert result == expected


def test_code_block_with_only_empty_lines_should_preserve_them() -> None:
    markdown = dedent(
        """
        ```python


        ```
        """
    )
    result = process_markdown_whitespace(markdown)

    expected = dedent(
        """
        ```python


        ```
        """
    )
    assert result == expected


def test_mixed_content_with_lists_and_code() -> None:
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
    result = process_markdown_whitespace(markdown)

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


def test_code_fence_with_leading_whitespace_should_be_recognized() -> None:
    markdown = dedent(
        """
            ```python
                code
            ```
        """
    )
    result = process_markdown_whitespace(markdown)

    expected = dedent(
        """
        ```python
        code
        ```
        """
    )
    assert result == expected


def test_code_block_already_normalized_should_remain_unchanged() -> None:
    markdown = dedent(
        """
        ```python
        def hello():
            print("world")
        ```
        """
    )
    result = process_markdown_whitespace(markdown)
    assert result == markdown


def test_code_block_with_language_and_extra_spaces() -> None:
    markdown = dedent(
        """
          ```python
              code here
          ```
        """
    )
    result = process_markdown_whitespace(markdown)

    expected = dedent(
        """
        ```python
        code here
        ```
        """
    )
    assert result == expected
