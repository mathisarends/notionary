from __future__ import annotations

from enum import StrEnum
from typing import Self


class BlockColor(StrEnum):
    BLUE = "blue"
    BROWN = "brown"
    DEFAULT = "default"
    GRAY = "gray"
    GREEN = "green"
    ORANGE = "orange"
    YELLOW = "yellow"
    PINK = "pink"
    PURPLE = "purple"
    RED = "red"

    BLUE_BACKGROUND = "blue_background"
    BROWN_BACKGROUND = "brown_background"
    DEFAULT_BACKGROUND = "default_background"
    GRAY_BACKGROUND = "gray_background"
    GREEN_BACKGROUND = "green_background"
    ORANGE_BACKGROUND = "orange_background"
    YELLOW_BACKGROUND = "yellow_background"
    PINK_BACKGROUND = "pink_background"
    PURPLE_BACKGROUND = "purple_background"
    RED_BACKGROUND = "red_background"

    def is_background(self) -> bool:
        return self.value.endswith("_background")

    def get_base_color(self) -> str:
        return self.value.replace("_background", "")


class BlockType(StrEnum):
    AUDIO = "audio"
    BOOKMARK = "bookmark"
    BREADCRUMB = "breadcrumb"
    BULLETED_LIST_ITEM = "bulleted_list_item"
    CALLOUT = "callout"
    CHILD_DATABASE = "child_database"
    CHILD_PAGE = "child_page"
    CODE = "code"
    COLUMN = "column"
    COLUMN_LIST = "column_list"
    DIVIDER = "divider"
    EMBED = "embed"
    EQUATION = "equation"
    FILE = "file"
    HEADING_1 = "heading_1"
    HEADING_2 = "heading_2"
    HEADING_3 = "heading_3"
    IMAGE = "image"
    LINK_PREVIEW = "link_preview"
    LINK_TO_PAGE = "link_to_page"
    NUMBERED_LIST_ITEM = "numbered_list_item"
    PARAGRAPH = "paragraph"
    PDF = "pdf"
    QUOTE = "quote"
    SYNCED_BLOCK = "synced_block"
    TABLE = "table"
    TABLE_OF_CONTENTS = "table_of_contents"
    TABLE_ROW = "table_row"
    TO_DO = "to_do"
    TOGGLE = "toggle"
    UNSUPPORTED = "unsupported"
    VIDEO = "video"


class CodingLanguage(StrEnum):
    ABAP = "abap"
    ARDUINO = "arduino"
    BASH = "bash"
    BASIC = "basic"
    C = "c"
    CLOJURE = "clojure"
    COFFEESCRIPT = "coffeescript"
    CPP = "c++"
    CSHARP = "c#"
    CSS = "css"
    DART = "dart"
    DIFF = "diff"
    DOCKER = "docker"
    ELIXIR = "elixir"
    ELM = "elm"
    ERLANG = "erlang"
    FLOW = "flow"
    FORTRAN = "fortran"
    FSHARP = "f#"
    GHERKIN = "gherkin"
    GLSL = "glsl"
    GO = "go"
    GRAPHQL = "graphql"
    GROOVY = "groovy"
    HASKELL = "haskell"
    HTML = "html"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    JSON = "json"
    JULIA = "julia"
    KOTLIN = "kotlin"
    LATEX = "latex"
    LESS = "less"
    LISP = "lisp"
    LIVESCRIPT = "livescript"
    LUA = "lua"
    MAKEFILE = "makefile"
    MARKDOWN = "markdown"
    MARKUP = "markup"
    MATLAB = "matlab"
    MERMAID = "mermaid"
    NIX = "nix"
    OBJECTIVE_C = "objective-c"
    OCAML = "ocaml"
    PASCAL = "pascal"
    PERL = "perl"
    PHP = "php"
    PLAIN_TEXT = "plain text"
    POWERSHELL = "powershell"
    PROLOG = "prolog"
    PROTOBUF = "protobuf"
    PYTHON = "python"
    R = "r"
    REASON = "reason"
    RUBY = "ruby"
    RUST = "rust"
    SASS = "sass"
    SCALA = "scala"
    SCHEME = "scheme"
    SCSS = "scss"
    SHELL = "shell"
    SQL = "sql"
    SWIFT = "swift"
    TYPESCRIPT = "typescript"
    VB_NET = "vb.net"
    VERILOG = "verilog"
    VHDL = "vhdl"
    VISUAL_BASIC = "visual basic"
    WEBASSEMBLY = "webassembly"
    XML = "xml"
    YAML = "yaml"
    JAVA_C_CPP_CSHARP = "java/c/c++/c#"

    @classmethod
    def from_string(cls, lang_str: str | None, default: Self | None = None) -> Self:
        if not lang_str:
            return default if default is not None else cls.PLAIN_TEXT

        normalized = lang_str.lower().strip()

        aliases = {
            "cpp": cls.CPP,
            "c++": cls.CPP,
            "js": cls.JAVASCRIPT,
            "py": cls.PYTHON,
            "ts": cls.TYPESCRIPT,
        }

        if normalized in aliases:
            return aliases[normalized]

        for member in cls:
            if member.value.lower() == normalized:
                return member

        return default if default is not None else cls.PLAIN_TEXT


class VideoFileType(StrEnum):
    AMV = ".amv"
    ASF = ".asf"
    AVI = ".avi"
    F4V = ".f4v"
    FLV = ".flv"
    GIFV = ".gifv"
    MKV = ".mkv"
    MOV = ".mov"
    MPG = ".mpg"
    MPEG = ".mpeg"
    MPV = ".mpv"
    MP4 = ".mp4"
    M4V = ".m4v"
    QT = ".qt"
    WMV = ".wmv"

    @classmethod
    def get_all_extensions(cls) -> set[str]:
        return {ext.value for ext in cls}

    @classmethod
    def is_valid_extension(cls, filename: str) -> bool:
        lower_filename = filename.lower()
        return any(lower_filename.endswith(ext.value) for ext in cls)
