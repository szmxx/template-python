"""Pagination utilities for database queries."""

from typing import Any, Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field
from sqlmodel import Session, SQLModel, func, select

T = TypeVar("T", bound=SQLModel)


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = Field(default=1, ge=1, description="Page number (starting from 1)")

    size: int = Field(
        default=20, ge=1, le=1000, description="Number of items per page (1-1000)"
    )

    @property
    def skip(self) -> int:
        """Calculate number of items to skip."""
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        """Get limit value."""
        return self.size


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model."""

    items: list[T] = Field(description="List of items")
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    size: int = Field(description="Number of items per page")
    pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")

    @classmethod
    def create(
        cls, items: list[T], total: int, page: int, size: int
    ) -> "PaginatedResponse[T]":
        """Create a paginated response.

        Args:
            items: List of items for current page
            total: Total number of items
            page: Current page number
            size: Number of items per page

        Returns:
            PaginatedResponse instance
        """
        pages = (total + size - 1) // size if total > 0 else 0

        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1,
        )


def create_pagination_params(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    size: int = Query(
        20, ge=1, le=1000, description="Number of items per page (1-1000)"
    ),
) -> PaginationParams:
    """Create pagination parameters from query parameters.

    Args:
        page: Page number
        size: Page size

    Returns:
        PaginationParams instance
    """
    return PaginationParams(page=page, size=size)


def paginate_query(
    db: Session, query, pagination: PaginationParams, count_query: Any | None = None
) -> PaginatedResponse:
    """Paginate a SQLModel query.

    Args:
        db: Database session
        query: SQLModel select query
        pagination: Pagination parameters
        count_query: Optional custom count query

    Returns:
        PaginatedResponse with paginated results
    """
    # 获取总数
    if count_query is not None:
        total = db.exec(count_query).first()
    else:
        # 从原查询构建计数查询
        count_query = select(func.count()).select_from(query.subquery())
        total = db.exec(count_query).first()

    # 获取分页数据
    paginated_query = query.offset(pagination.skip).limit(pagination.limit)
    items = db.exec(paginated_query).all()

    return PaginatedResponse.create(
        items=items, total=total, page=pagination.page, size=pagination.size
    )


class SearchParams(BaseModel):
    """Search parameters."""

    q: str | None = Field(
        default=None, min_length=1, max_length=100, description="Search query"
    )

    sort_by: str | None = Field(default=None, description="Field to sort by")

    sort_order: str = Field(
        default="asc", pattern="^(asc|desc)$", description="Sort order (asc or desc)"
    )

    @property
    def is_descending(self) -> bool:
        """Check if sort order is descending."""
        return self.sort_order.lower() == "desc"


def create_search_params(
    q: str | None = Query(
        None, min_length=1, max_length=100, description="Search query"
    ),
    sort_by: str | None = Query(None, description="Field to sort by"),
    sort_order: str = Query(
        "asc", pattern="^(asc|desc)$", description="Sort order (asc or desc)"
    ),
) -> SearchParams:
    """Create search parameters from query parameters.

    Args:
        q: Search query
        sort_by: Field to sort by
        sort_order: Sort order

    Returns:
        SearchParams instance
    """
    return SearchParams(q=q, sort_by=sort_by, sort_order=sort_order)


class FilterParams(BaseModel):
    """Base filter parameters."""

    active_only: bool = Field(default=True, description="Filter only active items")

    created_after: str | None = Field(
        default=None, description="Filter items created after this date (ISO format)"
    )

    created_before: str | None = Field(
        default=None, description="Filter items created before this date (ISO format)"
    )


def create_filter_params(
    active_only: bool = Query(True, description="Filter only active items"),
    created_after: str | None = Query(
        None, description="Filter items created after this date (ISO format)"
    ),
    created_before: str | None = Query(
        None, description="Filter items created before this date (ISO format)"
    ),
) -> FilterParams:
    """Create filter parameters from query parameters.

    Args:
        active_only: Filter only active items
        created_after: Filter items created after this date
        created_before: Filter items created before this date

    Returns:
        FilterParams instance
    """
    return FilterParams(
        active_only=active_only,
        created_after=created_after,
        created_before=created_before,
    )
