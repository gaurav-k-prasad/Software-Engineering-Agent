from dataclasses import dataclass, field

@dataclass
class Import:
    module_name: str
    alias: str

    def __str__(self) -> str:
        return f"{self.module_name}"


@dataclass
class ChunkMetaData:
    chunk_id: str = ""
    chunk_type: str = ""
    name: str = ""
    qualified_name: str = ""
    parent_name: str | None = None
    parent_type: str | None = None
    file_path: str = ""
    file_name: str = ""
    module_path: str = ""
    language: str = ""
    start_line: int = 0
    end_line: int = 0
    source_code: str = ""
    parameters: list[str] = field(default_factory=list)
    return_type: str | None = None
    decorators: list[str] = field(default_factory=list)
    is_async: bool = False
    base_classes: list[str] = field(default_factory=list)
    imports: list[Import] = field(default_factory=list)
    contains: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)
    contained_in: str | None = None
