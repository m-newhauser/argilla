#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from abc import ABCMeta, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, ClassVar, Dict, Generic, Iterable, List, Optional, Type, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, Field, root_validator
from pydantic.generics import GenericModel

from argilla.server.enums import MetadataPropertyType, RecordSortField, ResponseStatusFilter, SortOrder
from argilla.server.models import Dataset, MetadataProperty, Record, Response, User

__all__ = [
    "SearchEngine",
    "StringQuery",
    "MetadataFilter",
    "TermsMetadataFilter",
    "IntegerMetadataFilter",
    "FloatMetadataFilter",
    "UserResponseStatusFilter",
    "SearchResponseItem",
    "SearchResponses",
    "SortBy",
    "MetadataMetrics",
    "TermsMetadataMetrics",
    "IntegerMetadataMetrics",
    "FloatMetadataMetrics",
]


class StringQuery(BaseModel):
    q: str
    field: Optional[str] = None


class UserResponseStatusFilter(BaseModel):
    statuses: List[ResponseStatusFilter]
    user: Optional[User] = None

    class Config:
        arbitrary_types_allowed = True


class MetadataFilter(BaseModel):
    metadata_property: MetadataProperty

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    @abstractmethod
    def from_string(cls, metadata_property: MetadataProperty, string: str) -> "MetadataFilter":
        pass


class TermsMetadataFilter(MetadataFilter):
    values: List[str]

    @classmethod
    def from_string(cls, metadata_property: MetadataProperty, string: str) -> "MetadataFilter":
        return cls(metadata_property=metadata_property, values=string.split(","))


NT = TypeVar("NT", int, float)


class _RangeModel(GenericModel, Generic[NT]):
    ge: Optional[NT]
    le: Optional[NT]


class NumericMetadataFilter(GenericModel, Generic[NT], MetadataFilter):
    ge: Optional[NT] = None
    le: Optional[NT] = None

    _json_model: ClassVar[Type[_RangeModel]]

    @root_validator
    def check_bounds(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        ge = values.get("ge")
        le = values.get("le")

        if ge is None and le is None:
            raise ValueError("One of 'ge' or 'le' values must be specified")

        if ge is not None and le is not None and ge > le:
            raise ValueError(f"'ge' ({ge}) must be lower or equal than 'le' ({le})")

        return values

    @classmethod
    def from_string(cls, metadata_property: MetadataProperty, string: str) -> "NumericMetadataFilter":
        model = cls._json_model.parse_raw(string)
        return cls(metadata_property=metadata_property, ge=model.ge, le=model.le)


class IntegerMetadataFilter(NumericMetadataFilter[int]):
    _json_model = _RangeModel[int]


class FloatMetadataFilter(NumericMetadataFilter[float]):
    _json_model = _RangeModel[float]


class SearchResponseItem(BaseModel):
    record_id: UUID
    score: Optional[float]


class SearchResponses(BaseModel):
    items: List[SearchResponseItem]
    total: int = 0


class SortBy(BaseModel):
    field: Union[MetadataProperty, RecordSortField]
    order: SortOrder = SortOrder.asc

    class Config:
        arbitrary_types_allowed = True


class TermsMetadataMetrics(BaseModel):
    class TermCount(BaseModel):
        term: str
        count: int

    type: MetadataPropertyType = Field(MetadataPropertyType.terms, const=True)
    total: int
    values: List[TermCount] = Field(default_factory=list)


class NumericMetadataMetrics(GenericModel, Generic[NT]):
    min: Optional[NT]
    max: Optional[NT]


class IntegerMetadataMetrics(NumericMetadataMetrics[int]):
    type: MetadataPropertyType = Field(MetadataPropertyType.integer, const=True)


class FloatMetadataMetrics(NumericMetadataMetrics[float]):
    type: MetadataPropertyType = Field(MetadataPropertyType.float, const=True)


MetadataMetrics = Union[TermsMetadataMetrics, IntegerMetadataMetrics, FloatMetadataMetrics]


class SearchEngine(metaclass=ABCMeta):
    registered_classes = {}

    @classmethod
    @abstractmethod
    async def new_instance(cls) -> "SearchEngine":
        pass

    @abstractmethod
    async def close(self):
        pass

    @classmethod
    def register(cls, engine_name: str):
        def decorator(engine_class):
            cls.registered_classes[engine_name] = engine_class
            return engine_class

        return decorator

    @classmethod
    @asynccontextmanager
    async def get_by_name(cls, engine_name: str) -> AsyncGenerator["SearchEngine", None]:
        engine_name = engine_name.lower().strip()

        if engine_name not in cls.registered_classes:
            raise ValueError(f"No engine class registered for '{engine_name}'")

        engine_class = cls.registered_classes[engine_name]

        engine = None

        try:
            engine = await engine_class.new_instance()
            yield engine
        except Exception as e:
            raise e
        finally:
            if engine is not None:
                await engine.close()

    @abstractmethod
    async def create_index(self, dataset: Dataset):
        pass

    @abstractmethod
    async def delete_index(self, dataset: Dataset):
        pass

    @abstractmethod
    async def configure_metadata_property(self, dataset: Dataset, metadata_property: MetadataProperty):
        pass

    @abstractmethod
    async def index_records(self, dataset: Dataset, records: Iterable[Record]):
        pass

    @abstractmethod
    async def delete_records(self, dataset: Dataset, records: Iterable[Record]):
        pass

    @abstractmethod
    async def update_record_response(self, response: Response):
        pass

    @abstractmethod
    async def delete_record_response(self, response: Response):
        pass

    @abstractmethod
    async def search(
        self,
        dataset: Dataset,
        query: Optional[Union[StringQuery, str]] = None,
        # TODO(@frascuchon): The search records method should receive a generic list of filters
        user_response_status_filter: Optional[UserResponseStatusFilter] = None,
        metadata_filters: Optional[List[MetadataFilter]] = None,
        offset: int = 0,
        limit: int = 100,
        sort_by: Optional[List[SortBy]] = None,
    ) -> SearchResponses:
        pass

    @abstractmethod
    async def compute_metrics_for(self, metadata_property: MetadataProperty) -> MetadataMetrics:
        pass
