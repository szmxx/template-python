from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from src.db.connection import get_db_session
from src.models.user import User, UserCreate, UserLogin, UserResponse, UserUpdate
from src.utils.pagination import PaginationParams, paginate_query
from src.utils.response import success_response
from src.utils.security import (
    is_password_strong,
    simple_password_check,
)

router = APIRouter()


@router.get("/")
def get_users(
    pagination: PaginationParams = Depends(), db: Session = Depends(get_db_session)
) -> JSONResponse:
    """Get all users with pagination."""
    query = select(User).where(User.is_active)
    result = paginate_query(db, query, pagination)

    return success_response(
        data={
            "users": [UserResponse.model_validate(user) for user in result.items],
            "pagination": {
                "total": result.total,
                "page": result.page,
                "size": result.size,
                "pages": result.pages,
                "has_next": result.has_next,
                "has_prev": result.has_prev,
            },
        },
        message="Users retrieved successfully",
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate, db: Session = Depends(get_db_session)
) -> JSONResponse:
    """Create a new user."""
    # 检查用户名是否已存在（只检查活跃用户）
    existing_user = db.exec(
        select(User).where(User.username == user.username, User.is_active)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    # 检查邮箱是否已存在（只检查活跃用户）
    existing_email = db.exec(
        select(User).where(User.email == user.email, User.is_active)
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
        )

    # 验证密码格式
    is_valid, issues = is_password_strong(user.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password validation failed: {', '.join(issues)}",
        )

    user_dict = user.model_dump()
    new_user = User(**user_dict)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return success_response(
        data=UserResponse.model_validate(new_user), message="User created successfully"
    )


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db_session)) -> JSONResponse:
    """Get a user by ID."""
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return success_response(
        data=UserResponse.model_validate(user), message="User retrieved successfully"
    )


@router.put("/{user_id}")
def update_user(
    user_id: int, user_update: UserUpdate, db: Session = Depends(get_db_session)
) -> JSONResponse:
    """Update a user."""
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # 更新用户数据
    update_data = user_update.model_dump(exclude_unset=True)

    if "password" in update_data:
        is_valid, issues = is_password_strong(update_data["password"])
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {', '.join(issues)}",
            )

    for field, value in update_data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)

    return success_response(
        data=UserResponse.model_validate(user), message="User updated successfully"
    )


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db_session)) -> JSONResponse:
    """Delete a user (soft delete)."""
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.is_active = False
    db.add(user)
    db.commit()

    return success_response(message="User deleted successfully")


@router.post("/login")
def login_user(
    login_data: UserLogin, db: Session = Depends(get_db_session)
) -> JSONResponse:
    """Simple user login (development only)."""
    # 查找用户
    user = db.exec(
        select(User).where(
            (User.username == login_data.username) | (User.email == login_data.username)
        )
    ).first()

    if not user or not simple_password_check(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User account is inactive"
        )

    # 更新最后登录时间

    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()

    return success_response(
        data=UserResponse.model_validate(user), message="Login successful"
    )
