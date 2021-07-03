from abc import abstractmethod
from typing import (
    Optional,
    List,
    TypeVar,
    Union,
    Type,
    Dict,
    Any,
    Generic,
    cast,
)

from pydantic.main import BaseModel

ResultQueryType = TypeVar("ResultQueryType")


class BaseCursorQuery(Generic[ResultQueryType]):
    """
    BaseCursorQuery class. Wrapper over AsyncIOMotorCursor,
    which parse result with model
    """

    @abstractmethod
    def get_projection_model(self) -> Optional[Type[BaseModel]]:
        ...

    @property
    @abstractmethod
    def motor_cursor(self):
        ...

    def __aiter__(self):
        return self

    async def __anext__(self) -> Union[BaseModel, Dict[str, Any]]:
        if getattr(self, "cursor", None) is None:
            self.cursor = self.motor_cursor
        next_item = await self.cursor.__anext__()
        projection = self.get_projection_model()
        return (
            projection.parse_obj(next_item)
            if projection is not None
            else next_item
        )

    async def to_list(
        self, length: Optional[int] = None
    ) -> List[ResultQueryType]:  # noqa
        """
        Get list of documents

        :param length: Optional[int] - length of the list
        :return: Union[List[BaseModel], List[Dict[str, Any]]]
        """
        motor_list: List[Dict[str, Any]] = await self.motor_cursor.to_list(
            length
        )
        projection = self.get_projection_model()
        if projection is not None:
            return cast(
                List[ResultQueryType],
                [projection.parse_obj(i) for i in motor_list],
            )
        return cast(List[ResultQueryType], motor_list)
