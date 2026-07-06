"""Base Repository Interface.

Abstract base class for all repositories.
Defines common CRUD operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar

T = TypeVar("T")


class BaseRepository(ABC):
    """Abstract base repository interface."""

    @abstractmethod
    def save(self, entity: T) -> None:
        """Save an entity."""
        pass

    @abstractmethod
    def get(self, entity_id: str) -> Optional[T]:
        """Get an entity by ID."""
        pass

    @abstractmethod
    def list_all(self) -> List[T]:
        """List all entities."""
        pass

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Delete an entity by ID."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count total entities."""
        pass

    def update(self, entity_id: str, data: Dict[str, Any]) -> bool:
        """Update an entity by ID."""
        raise NotImplementedError("Update not supported by this repository")

    def find_by(self, **kwargs) -> List[T]:
        """Find entities by criteria."""
        raise NotImplementedError("Find by not supported by this repository")
