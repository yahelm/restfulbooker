from typing import Any

from pydantic import BaseModel


class BaseFactory[ModelT: BaseModel]:
    model: type[ModelT]

    def defaults(self) -> dict[str, Any]:
        raise NotImplementedError

    def build(self, **overrides: Any) -> ModelT:
        return self.model(**{**self.defaults(), **overrides})
