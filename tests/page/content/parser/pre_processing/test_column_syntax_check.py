from textwrap import dedent

import pytest

from notionary.page.content.parser.pre_processsing.syntax_check import validate_columns_syntax


def test_no_columns_block_should_pass() -> None:
    valid_markdown = dedent(
        """
        # Normal heading

        Normal text without columns.

        ## Another heading

        - List
        - Items
        """
    )
    validate_columns_syntax(valid_markdown)


def test_valid_columns_with_two_columns_should_pass() -> None:
    valid_markdown = dedent(
        """
        ::: columns
        ::: column
        Left content
        :::

        ::: column
        Right content
        :::
        :::
        """
    )
    validate_columns_syntax(valid_markdown)


def test_valid_columns_with_three_columns_should_pass() -> None:
    valid_markdown = dedent(
        """
        ::: columns
        ::: column
        First column
        :::

        ::: column
        Second column
        :::

        ::: column
        Third column
        :::
        :::
        """
    )
    validate_columns_syntax(valid_markdown)


def test_columns_with_only_one_column_should_fail() -> None:
    invalid_markdown = dedent(
        """
        ::: columns
        ::: column
        Only one column
        :::
        :::
        """
    )
    with pytest.raises(ValueError, match=r"muss mindestens 2 column Blöcke enthalten"):
        validate_columns_syntax(invalid_markdown)


def test_valid_width_ratios_that_sum_to_one_should_pass() -> None:
    valid_markdown = dedent(
        """
        ::: columns
        ::: column 0.5
        First column (50%)
        :::

        ::: column 0.3
        Second column (30%)
        :::

        ::: column 0.2
        Third column (20%)
        :::
        :::
        """
    )
    validate_columns_syntax(valid_markdown)


def test_valid_width_ratios_60_40_should_pass() -> None:
    valid_markdown = dedent(
        """
        ::: columns
        ::: column 0.6
        Wider column
        :::

        ::: column 0.4
        Narrower column
        :::
        :::
        """
    )
    validate_columns_syntax(valid_markdown)


def test_invalid_width_ratios_not_summing_to_one_should_fail() -> None:
    invalid_markdown = dedent(
        """
        ::: columns
        ::: column 0.5
        First column
        :::

        ::: column 0.4
        Second column
        :::

        ::: column 0.2
        Third column (sum = 1.1)
        :::
        :::
        """
    )
    with pytest.raises(ValueError, match=r"width_ratios müssen sich zu 1.0 addieren"):
        validate_columns_syntax(invalid_markdown)


def test_invalid_width_ratios_summing_to_less_than_one_should_fail() -> None:
    invalid_markdown = dedent(
        """
        ::: columns
        ::: column 0.3
        First column
        :::

        ::: column 0.2
        Second column (sum = 0.5)
        :::
        :::
        """
    )
    with pytest.raises(ValueError, match=r"width_ratios müssen sich zu 1.0 addieren.*aber Summe ist 0.5"):
        validate_columns_syntax(invalid_markdown)


def test_mixed_columns_with_and_without_ratios_should_pass() -> None:
    valid_markdown = dedent(
        """
        ::: columns
        ::: column 0.6
        With ratio
        :::

        ::: column
        Without ratio
        :::
        :::
        """
    )
    validate_columns_syntax(valid_markdown)


def test_multiple_columns_blocks_should_validate_all() -> None:
    valid_markdown = dedent(
        """
        # First section

        ::: columns
        ::: column
        First column block 1
        :::

        ::: column
        Second column block 1
        :::
        :::

        # Second section

        ::: columns
        ::: column
        First column block 2
        :::

        ::: column
        Second column block 2
        :::
        :::
        """
    )
    validate_columns_syntax(valid_markdown)


def test_nested_content_in_columns_should_pass() -> None:
    invalid_markdown = dedent(
        """
        ::: columns
        ::: column
        ## Heading in column

        - List
        - Items

        ```python
        code block
        ```
        :::

        ::: column
        **Bold text**

        > Quote
        :::
        :::
        """
    )
    validate_columns_syntax(invalid_markdown)
