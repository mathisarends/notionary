from __future__ import annotations

from typing import Dict, Any, List, Optional, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import re

SPACER_MARKER = "---spacer---"


class LineType(Enum):
    """Enum for different line types"""

    EMPTY = "empty"
    HEADING = "heading"
    DIVIDER = "divider"
    CODE_BLOCK_MARKER = "code_block_marker"
    SPACER_MARKER = SPACER_MARKER
    PIPE_SYNTAX = "pipe_syntax"
    TODO_ITEM = "todo_item"
    REGULAR_CONTENT = "regular_content"


@dataclass
class LineContext:
    """Context of a line for spacer rule application"""

    line: str
    line_number: int
    line_type: LineType
    is_empty: bool
    content: str
    in_code_block: bool
    last_line_was_spacer: bool
    last_non_empty_was_heading: bool
    has_content_before: bool
    processed_lines: List[str]


@dataclass
class SpacerDecision:
    """Decision about inserting a spacer"""

    should_add_spacer: bool
    reason: str
    rule_name: str


@dataclass
class ProcessingResult:
    """Result of processing a single line"""

    output_lines: List[str]
    new_state: Dict[str, Any]
    spacer_added: bool = False


class SpacerRule(ABC):
    """Abstract base class for spacer rules"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the rule for debugging"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the rule does"""
        pass

    @abstractmethod
    def applies_to(self, context: LineContext) -> bool:
        """Checks if this rule is relevant for the context"""
        pass

    @abstractmethod
    def should_add_spacer(self, context: LineContext) -> SpacerDecision:
        """Decides whether a spacer should be added"""
        pass


class HeadingSpacerRule(SpacerRule):
    """Rule: Add spacer before headings (except after other headings)"""

    @property
    def name(self) -> str:
        return "HeadingSpacerRule"

    @property
    def description(self) -> str:
        return "Adds spacer before headings, except when the previous line was already a heading"

    def applies_to(self, context: LineContext) -> bool:
        return context.line_type == LineType.HEADING

    def should_add_spacer(self, context: LineContext) -> SpacerDecision:
        # Rule: Insert spacer before heading when:
        # 1. There is content before this heading
        # 2. The last line was not a spacer
        # 3. The last non-empty line was not a heading

        if not context.has_content_before:
            return SpacerDecision(False, "No content before this heading", self.name)

        if context.last_line_was_spacer:
            return SpacerDecision(
                False, "Previous line was already a spacer", self.name
            )

        if context.last_non_empty_was_heading:
            return SpacerDecision(
                False,
                "Previous non-empty line was a heading (consecutive headings)",
                self.name,
            )

        return SpacerDecision(
            True,
            "Adding spacer before heading to separate from previous content",
            self.name,
        )


class DividerSpacerRule(SpacerRule):
    """Rule: Add spacer before dividers"""

    @property
    def name(self) -> str:
        return "DividerSpacerRule"

    @property
    def description(self) -> str:
        return "Adds spacer before dividers (---) to create visual distance"

    def applies_to(self, context: LineContext) -> bool:
        return context.line_type == LineType.DIVIDER

    def should_add_spacer(self, context: LineContext) -> SpacerDecision:
        # Rule: Insert spacer before divider except when last line was already a spacer

        if context.last_line_was_spacer:
            return SpacerDecision(
                False, "Previous line was already a spacer", self.name
            )

        return SpacerDecision(
            True, "Adding spacer before divider for visual separation", self.name
        )


class ConsecutiveSpacerRule(SpacerRule):
    """Rule: Prevent consecutive spacers"""

    @property
    def name(self) -> str:
        return "ConsecutiveSpacerRule"

    @property
    def description(self) -> str:
        return "Prevents consecutive spacer markers"

    def applies_to(self, context: LineContext) -> bool:
        return context.line_type == LineType.SPACER_MARKER

    def should_add_spacer(self, context: LineContext) -> SpacerDecision:
        # Rule: Never allow consecutive spacers

        if context.last_line_was_spacer:
            return SpacerDecision(False, "Preventing consecutive spacers", self.name)

        return SpacerDecision(True, "Adding spacer marker", self.name)


class CodeBlockSpacerRule(SpacerRule):
    """Rule: No spacers inside code blocks"""

    @property
    def name(self) -> str:
        return "CodeBlockSpacerRule"

    @property
    def description(self) -> str:
        return "Prevents spacer processing inside code blocks"

    def applies_to(self, context: LineContext) -> bool:
        return context.in_code_block and context.line_type != LineType.CODE_BLOCK_MARKER

    def should_add_spacer(self, context: LineContext) -> SpacerDecision:
        return SpacerDecision(
            False, "Inside code block - no spacer processing", self.name
        )


class StateBuilder:
    """Builder for creating and updating state"""

    def __init__(self, initial_state: Dict[str, Any]):
        self._state = initial_state.copy()

    def toggle_code_block(self) -> StateBuilder:
        """Toggle the code block state"""
        self._state["in_code_block"] = not self._state.get("in_code_block", False)
        return self

    def set_last_line_was_spacer(self, value: bool) -> StateBuilder:
        """Set whether the last line was a spacer"""
        self._state["last_line_was_spacer"] = value
        return self

    def update_content_tracking(
        self, line_type: LineType, has_content: bool
    ) -> StateBuilder:
        """Update content tracking state"""
        if has_content:
            self._state["last_non_empty_was_heading"] = line_type == LineType.HEADING
            self._state["has_content_before"] = True
        return self

    def build(self) -> Dict[str, Any]:
        """Build the final state"""
        return self._state


class LineProcessor(ABC):
    """Abstract processor for different line types"""

    @abstractmethod
    def can_process(self, line_type: LineType) -> bool:
        """Check if this processor can handle the line type"""
        pass

    @abstractmethod
    def process(self, context: LineContext, state: Dict[str, Any]) -> ProcessingResult:
        """Process the line and return the result"""
        pass


class EmptyLineProcessor(LineProcessor):
    """Processor for empty lines"""

    def can_process(self, line_type: LineType) -> bool:
        return line_type == LineType.EMPTY

    def process(self, context: LineContext, state: Dict[str, Any]) -> ProcessingResult:
        new_state = StateBuilder(state).set_last_line_was_spacer(False).build()

        return ProcessingResult(output_lines=[context.line], new_state=new_state)


class CodeBlockMarkerProcessor(LineProcessor):
    """Processor for code block markers"""

    def can_process(self, line_type: LineType) -> bool:
        return line_type == LineType.CODE_BLOCK_MARKER

    def process(self, context: LineContext, state: Dict[str, Any]) -> ProcessingResult:
        new_state = (
            StateBuilder(state)
            .toggle_code_block()
            .set_last_line_was_spacer(False)
            .update_content_tracking(context.line_type, bool(context.content))
            .build()
        )

        return ProcessingResult(output_lines=[context.line], new_state=new_state)


class SpacerMarkerProcessor(LineProcessor):
    """Processor for spacer marker lines"""

    def __init__(self, spacer_marker: str, rules: List[SpacerRule]):
        self.spacer_marker = spacer_marker
        self.rules = rules

    def can_process(self, line_type: LineType) -> bool:
        return line_type == LineType.SPACER_MARKER

    def process(self, context: LineContext, state: Dict[str, Any]) -> ProcessingResult:
        # Apply spacer rules
        spacer_decision = self._get_spacer_decision(context)

        output_lines = []
        spacer_added = False

        if spacer_decision.should_add_spacer:
            output_lines.append(context.line)
            spacer_added = True

        new_state = StateBuilder(state).set_last_line_was_spacer(spacer_added).build()

        return ProcessingResult(
            output_lines=output_lines, new_state=new_state, spacer_added=spacer_added
        )

    def _get_spacer_decision(self, context: LineContext) -> SpacerDecision:
        """Get spacer decision from rules"""
        for rule in self.rules:
            if rule.applies_to(context):
                return rule.should_add_spacer(context)

        # Default: don't add spacer
        return SpacerDecision(False, "No applicable rule found", "DefaultRule")


class RegularContentProcessor(LineProcessor):
    """Processor for regular content lines"""

    def __init__(self, spacer_marker: str, rules: List[SpacerRule]):
        self.spacer_marker = spacer_marker
        self.rules = rules

    def can_process(self, line_type: LineType) -> bool:
        return line_type in [
            LineType.HEADING,
            LineType.DIVIDER,
            LineType.TODO_ITEM,
            LineType.REGULAR_CONTENT,
            LineType.PIPE_SYNTAX,
        ]

    def process(self, context: LineContext, state: Dict[str, Any]) -> ProcessingResult:
        output_lines = []
        spacer_added = False

        # Check if we should add a spacer before this line
        spacer_decision = self._get_spacer_decision(context)

        if spacer_decision.should_add_spacer:
            output_lines.append(self.spacer_marker)
            spacer_added = True

        # Add the original line
        output_lines.append(context.line)

        # Build new state
        new_state = (
            StateBuilder(state)
            .set_last_line_was_spacer(spacer_added)
            .update_content_tracking(context.line_type, bool(context.content))
            .build()
        )

        return ProcessingResult(
            output_lines=output_lines, new_state=new_state, spacer_added=spacer_added
        )

    def _get_spacer_decision(self, context: LineContext) -> SpacerDecision:
        """Get spacer decision from rules"""
        for rule in self.rules:
            if rule.applies_to(context):
                return rule.should_add_spacer(context)

        # Default: don't add spacer
        return SpacerDecision(False, "No applicable rule found", "DefaultRule")


class LineProcessorFactory:
    """Factory for creating line processors"""

    def __init__(self, spacer_marker: str, rules: List[SpacerRule]):
        self.processors = [
            EmptyLineProcessor(),
            CodeBlockMarkerProcessor(),
            SpacerMarkerProcessor(spacer_marker, rules),
            RegularContentProcessor(spacer_marker, rules),
        ]

    def get_processor(self, line_type: LineType) -> Optional[LineProcessor]:
        """Get appropriate processor for the line type"""
        for processor in self.processors:
            if processor.can_process(line_type):
                return processor
        return None


class ContextFactory:
    """Factory for creating line contexts"""

    @staticmethod
    def create_context(
        line: str, line_number: int, line_type: LineType, state: Dict[str, Any]
    ) -> LineContext:
        """Create a LineContext from line and state"""
        return LineContext(
            line=line,
            line_number=line_number,
            line_type=line_type,
            is_empty=not line.strip(),
            content=line.strip(),
            in_code_block=state.get("in_code_block", False),
            last_line_was_spacer=state.get("last_line_was_spacer", False),
            last_non_empty_was_heading=state.get("last_non_empty_was_heading", False),
            has_content_before=state.get("has_content_before", False),
            processed_lines=state.get("processed_lines", []),
        )


class SpacerRuleEngine:
    """Refactored engine with reduced complexity"""

    def __init__(self, rules: Optional[List[SpacerRule]] = None):
        self.rules = rules or self._get_default_rules()
        self.SPACER_MARKER = SPACER_MARKER

        # Initialize factories
        self.processor_factory = LineProcessorFactory(
            self.SPACER_MARKER,
            self.rules,
        )
        self.context_factory = ContextFactory()

    def process_line(
        self, line: str, line_number: int, context_state: Dict[str, Any]
    ) -> Tuple[List[str], Dict[str, Any]]:
        """
        Processes a line and returns the resulting lines + new state

        Returns:
            Tuple[List[str], Dict[str, Any]]: (processed_lines, new_state)
        """
        # Step 1: Determine line type (single responsibility)
        line_type = self._determine_line_type(
            line, context_state.get("in_code_block", False)
        )

        # Step 2: Create context (factory pattern)
        context = self.context_factory.create_context(
            line, line_number, line_type, context_state
        )

        # Step 3: Get appropriate processor (strategy pattern)
        processor = self.processor_factory.get_processor(line_type)
        if not processor:
            # Fallback to original line
            return [line], context_state.copy()

        # Step 4: Process line (delegation)
        result = processor.process(context, context_state)

        return result.output_lines, result.new_state

    def _get_default_rules(self) -> List[SpacerRule]:
        """Default rule set"""
        return [
            CodeBlockSpacerRule(),  # Highest priority - code blocks
            ConsecutiveSpacerRule(),  # Prevent duplicate spacers
            HeadingSpacerRule(),  # Spacer before headings
            DividerSpacerRule(),  # Spacer before dividers
        ]

    def _determine_line_type(self, line: str, in_code_block: bool) -> LineType:
        """Determines the type of a line"""
        content = line.strip()

        # Guard clauses for early returns
        if not content:
            return LineType.EMPTY

        if content.startswith("```"):
            return LineType.CODE_BLOCK_MARKER

        if in_code_block:
            return LineType.REGULAR_CONTENT

        if content == self.SPACER_MARKER:
            return LineType.SPACER_MARKER

        # Pattern matching with early returns
        patterns = [
            (r"^\|\s?(.*)$", LineType.PIPE_SYNTAX),
            (r"^(#{1,6})\s+(.+)$", LineType.HEADING),
            (r"^-{3,}$", LineType.DIVIDER),
            (r"^\s*[-*+]\s+\[[ x]\]", LineType.TODO_ITEM),
        ]

        for pattern, line_type in patterns:
            if re.match(pattern, content if pattern.startswith("^#{") else line):
                return line_type

        return LineType.REGULAR_CONTENT
