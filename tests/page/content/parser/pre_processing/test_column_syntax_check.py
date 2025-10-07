from textwrap import dedent

import pytest

from notionary.page.content.parser.pre_processsing.syntax_check import validate_columns_syntax


def test_no_columns_block_should_pass() -> None:
    valid_markdown = dedent(
        """
        # Normale Überschrift

        Normaler Text ohne columns.

        ## Weitere Überschrift

        - Liste
        - Elemente
        """
    )
    validate_columns_syntax(valid_markdown)


def test_valid_columns_with_two_columns_should_pass() -> None:
    valid_markdown = dedent(
        """
        ::: columns
        ::: column
        Linker Inhalt
        :::

        ::: column
        Rechter Inhalt
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
        Erste Spalte
        :::

        ::: column
        Zweite Spalte
        :::

        ::: column
        Dritte Spalte
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
        Nur eine Spalte
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
        Erste Spalte (50%)
        :::

        ::: column 0.3
        Zweite Spalte (30%)
        :::

        ::: column 0.2
        Dritte Spalte (20%)
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
        Breitere Spalte
        :::

        ::: column 0.4
        Schmalere Spalte
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
        Erste Spalte
        :::

        ::: column 0.4
        Zweite Spalte
        :::

        ::: column 0.2
        Dritte Spalte (Summe = 1.1)
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
        Erste Spalte
        :::

        ::: column 0.2
        Zweite Spalte (Summe = 0.5)
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
        Mit Ratio
        :::

        ::: column
        Ohne Ratio
        :::
        :::
        """
    )
    validate_columns_syntax(valid_markdown)


def test_multiple_columns_blocks_should_validate_all() -> None:
    valid_markdown = dedent(
        """
        # Erste Sektion

        ::: columns
        ::: column
        Erste Spalte Block 1
        :::

        ::: column
        Zweite Spalte Block 1
        :::
        :::

        # Zweite Sektion

        ::: columns
        ::: column
        Erste Spalte Block 2
        :::

        ::: column
        Zweite Spalte Block 2
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
        ## Überschrift in Spalte

        - Liste
        - Elemente

        ```python
        code block
        ```
        :::

        ::: column
        **Fetter Text**

        > Zitat
        :::
        :::
        """
    )
    validate_columns_syntax(invalid_markdown)
