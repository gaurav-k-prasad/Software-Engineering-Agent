import dataclasses
import json
from typing import IO, overload
from code_retriever.search_base import SearchResult
from structs import ChunkMetaData, Import


class ChunkStore:
    def __init__(self) -> None:
        self.docs: dict[str, ChunkMetaData] = {}

    @overload
    def insert(self, docs: ChunkMetaData) -> None:
        pass

    @overload
    def insert(self, docs: list[ChunkMetaData]) -> None:
        pass

    def insert(self, docs: ChunkMetaData | list[ChunkMetaData]) -> None:
        if isinstance(docs, ChunkMetaData):
            docs = [docs]

        for doc in docs:
            self.docs[doc.chunk_id] = doc

    @overload
    def get(self, chunk_ids: str) -> ChunkMetaData:
        pass

    @overload
    def get(self, chunk_ids: list[str]) -> list[ChunkMetaData]:
        pass

    def get(self, chunk_ids: str | list[str]) -> ChunkMetaData | list[ChunkMetaData]:
        is_single_query = False
        if isinstance(chunk_ids, str):
            chunk_ids = [chunk_ids]
            is_single_query = True

        res: list[ChunkMetaData] = []

        for chunk_id in chunk_ids:
            if chunk_id not in self.docs:
                raise KeyError("Chunk id not found in document store")

            res.append(self.docs[chunk_id])

        if is_single_query:
            return res[0]
        return res

    @overload
    def get_from_search_result(self, search_results: SearchResult) -> ChunkMetaData: ...

    @overload
    def get_from_search_result(
        self, search_results: list[SearchResult]
    ) -> list[ChunkMetaData]: ...

    def get_from_search_result(
        self, search_results: SearchResult | list[SearchResult]
    ) -> ChunkMetaData | list[ChunkMetaData]:
        is_single_query = False
        if isinstance(search_results, SearchResult):
            search_results = [search_results]
            is_single_query = True

        ids = [res.chunk_id for res in search_results]
        if is_single_query:
            ids = ids[0]

        return self.get(ids)

    def jsonl_to_metadata(self, s: str) -> ChunkMetaData:
        json_dict = json.loads(s)
        json_dict["imports"] = [
            Import(**_import) for _import in json_dict["imports"]
        ]  # converting

        return ChunkMetaData(**json_dict)

    def metadata_to_search_text(self, datadict: ChunkMetaData) -> str:
        res = ""
        if "class" in datadict.chunk_type:
            res += f"""Type: Class

Qualified Name: {datadict.qualified_name}

"""

            if datadict.methods:
                res += f"Methods:\n"
                for method in datadict.methods:
                    res += f"{method}\n"

                res += "\n"

            if datadict.base_classes:
                res += "Inherits From:\n"
                for base_class in datadict.base_classes:
                    res += base_class + "\n"

                res += "\n"

        elif "function" in datadict.chunk_type or "method" in datadict.chunk_type:
            is_method = "method" in datadict.chunk_type

            res += f"""Type: {"Method" if is_method else "Function"}

Qualified Name: {datadict.qualified_name}

"""
            if is_method:
                res += f"Parent Class: {datadict.parent_name}\n\n"

            if not datadict.parameters:
                res += "Parameters: None\n\n"
            else:
                res += "Parameters:\n"
                for parameter in datadict.parameters:
                    res += parameter + "\n"
                res += "\n"

            if datadict.return_type:
                res += f"Return Type: {datadict.return_type}\n\n"

        elif "module" in datadict.chunk_type:
            res += f"""Type: Module

Qualified Name: {datadict.module_path}

File: {datadict.file_name}

"""
        else:
            raise NotImplementedError(f"{datadict.chunk_type} is not implemented")

        if (
            datadict.imports and "module" not in datadict.chunk_type
        ):  # useless imports information in module level information
            res += "Imports:\n"

            for i, _import in enumerate(datadict.imports):
                res += f"{str(_import)}"
                res += ", " if i < len(datadict.imports) - 1 else ""

            res += "\n\n"

        if datadict.decorators:
            res += "Decorators:\n"

            for decorator in datadict.decorators:
                res += f"{decorator}\n"

            res += "\n"

        if "class" not in datadict.chunk_type:  # class need not have full source code
            res += "Source Code:\n"
            res += datadict.source_code

        return res

    def chunks_to_jsonl(
        self, chunks: list[ChunkMetaData], file: IO[str] | None
    ) -> None:
        if file is None:
            raise ValueError("No file stream found")

        for chunk in chunks:
            file.write(json.dumps(dataclasses.asdict(chunk)) + "\n")
