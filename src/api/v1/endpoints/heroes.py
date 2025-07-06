"""Hero endpoints."""

import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, func, select

from src.db import get_db_session
from src.models.hero import Hero, HeroCreate, HeroListResponse, HeroResponse, HeroUpdate
from src.utils.api_response import ApiResponse, MessageResponse

router = APIRouter()


@router.post(
    "/", response_model=ApiResponse[HeroResponse], status_code=status.HTTP_201_CREATED
)
async def create_hero(
    hero_data: HeroCreate, db: Session = Depends(get_db_session)
) -> ApiResponse[HeroResponse]:
    """Create a new hero."""
    # 检查英雄名称是否已存在
    existing_hero = db.exec(select(Hero).where(Hero.name == hero_data.name)).first()
    if existing_hero:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Hero name already exists"
        )

    # 创建新英雄
    hero_dict = hero_data.model_dump()

    # 处理能力列表(转换为 JSON 字符串)
    if hero_dict.get("abilities"):
        hero_dict["abilities"] = json.dumps(hero_dict["abilities"])

    hero = Hero(**hero_dict)
    db.add(hero)
    db.commit()
    db.refresh(hero)

    return ApiResponse.success_response(
        data=HeroResponse.model_validate(hero), message="英雄创建成功"
    )


@router.get("/", response_model=ApiResponse[HeroListResponse])
async def get_heroes(
    skip: int = Query(0, ge=0, description="Number of heroes to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of heroes to return"),
    active_only: bool = Query(True, description="Return only active heroes"),
    team: str | None = Query(None, description="Filter by team"),
    min_power_level: int | None = Query(
        None, ge=1, le=100, description="Minimum power level"
    ),
    max_power_level: int | None = Query(
        None, ge=1, le=100, description="Maximum power level"
    ),
    search: str | None = Query(None, description="Search in hero name or description"),
    db: Session = Depends(get_db_session),
):
    """Get all heroes with pagination and filtering."""
    query = select(Hero)

    # 应用过滤条件
    if active_only:
        query = query.where(Hero.is_active)

    if team:
        query = query.where(Hero.team == team)

    if min_power_level is not None:
        query = query.where(Hero.power_level >= min_power_level)

    if max_power_level is not None:
        query = query.where(Hero.power_level <= max_power_level)

    if search:
        search_term = f"%{search}%"
        query = query.where(
            (Hero.name.ilike(search_term)) | (Hero.description.ilike(search_term))
        )

    # 获取总数
    total_query = select(func.count(Hero.id))
    if active_only:
        total_query = total_query.where(Hero.is_active)
    if team:
        total_query = total_query.where(Hero.team == team)
    if min_power_level is not None:
        total_query = total_query.where(Hero.power_level >= min_power_level)
    if max_power_level is not None:
        total_query = total_query.where(Hero.power_level <= max_power_level)
    if search:
        search_term = f"%{search}%"
        total_query = total_query.where(
            (Hero.name.ilike(search_term)) | (Hero.description.ilike(search_term))
        )

    total = db.exec(total_query).first()

    # 获取分页数据
    heroes = db.exec(query.offset(skip).limit(limit)).all()

    # 计算分页信息
    pages = (total + limit - 1) // limit if total > 0 else 0
    current_page = (skip // limit) + 1

    hero_list_response = HeroListResponse(
        heroes=heroes, total=total, page=current_page, size=limit, pages=pages
    )
    return ApiResponse.success_response(
        data=hero_list_response, message="英雄列表获取成功"
    )


@router.get("/{hero_id}", response_model=ApiResponse[HeroResponse])
async def get_hero(
    hero_id: int, db: Session = Depends(get_db_session)
) -> ApiResponse[HeroResponse]:
    """Get a hero by ID."""
    hero = db.get(Hero, hero_id)
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found"
        )
    return ApiResponse.success_response(
        data=HeroResponse.model_validate(hero), message="英雄信息获取成功"
    )


@router.get("/name/{hero_name}", response_model=ApiResponse[HeroResponse])
async def get_hero_by_name(
    hero_name: str, db: Session = Depends(get_db_session)
) -> ApiResponse[HeroResponse]:
    """Get a hero by name."""
    hero = db.exec(select(Hero).where(Hero.name.ilike(f"%{hero_name}%"))).first()
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found"
        )
    return ApiResponse.success_response(
        data=HeroResponse.model_validate(hero), message="英雄信息获取成功"
    )


@router.put("/{hero_id}", response_model=ApiResponse[HeroResponse])
async def update_hero(
    hero_id: int, hero_data: HeroUpdate, db: Session = Depends(get_db_session)
) -> ApiResponse[HeroResponse]:
    """Update a hero."""
    hero = db.get(Hero, hero_id)
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found"
        )

    # 更新英雄数据
    update_data = hero_data.model_dump(exclude_unset=True)

    # 检查英雄名称唯一性
    if "name" in update_data:
        existing_hero = db.exec(
            select(Hero).where(Hero.name == update_data["name"], Hero.id != hero_id)
        ).first()
        if existing_hero:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hero name already exists",
            )

    # 处理能力列表
    if update_data.get("abilities"):
        update_data["abilities"] = json.dumps(update_data["abilities"])

    # 应用更新
    for field, value in update_data.items():
        setattr(hero, field, value)

    db.add(hero)
    db.commit()
    db.refresh(hero)

    return ApiResponse.success_response(
        data=HeroResponse.model_validate(hero), message="英雄信息更新成功"
    )


@router.delete("/{hero_id}", response_model=MessageResponse)
async def delete_hero(
    hero_id: int, db: Session = Depends(get_db_session)
) -> MessageResponse:
    """Delete a hero."""
    hero = db.get(Hero, hero_id)
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found"
        )

    db.delete(hero)
    db.commit()

    return MessageResponse.success_message("英雄删除成功")


@router.post("/{hero_id}/deactivate", response_model=ApiResponse[HeroResponse])
async def deactivate_hero(
    hero_id: int, db: Session = Depends(get_db_session)
) -> ApiResponse[HeroResponse]:
    """Deactivate a hero (soft delete)."""
    hero = db.get(Hero, hero_id)
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found"
        )

    hero.is_active = False
    db.add(hero)
    db.commit()
    db.refresh(hero)

    return ApiResponse.success_response(
        data=HeroResponse.model_validate(hero), message="英雄已停用"
    )


@router.post("/{hero_id}/activate", response_model=ApiResponse[HeroResponse])
async def activate_hero(
    hero_id: int, db: Session = Depends(get_db_session)
) -> ApiResponse[HeroResponse]:
    """Activate a hero."""
    hero = db.get(Hero, hero_id)
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found"
        )

    hero.is_active = True
    db.add(hero)
    db.commit()
    db.refresh(hero)

    return ApiResponse.success_response(
        data=HeroResponse.model_validate(hero), message="英雄已激活"
    )


@router.get("/teams/list", response_model=ApiResponse[list[str]])
async def get_teams(db: Session = Depends(get_db_session)) -> ApiResponse[list[str]]:
    """Get list of all teams."""
    teams = db.exec(
        select(Hero.team).where(Hero.team.isnot(None), Hero.is_active).distinct()
    ).all()

    team_list = [team for team in teams if team]
    return ApiResponse.success_response(data=team_list, message="团队列表获取成功")


@router.get("/stats/power-distribution", response_model=ApiResponse[dict])
async def get_power_distribution(
    db: Session = Depends(get_db_session),
) -> ApiResponse[dict]:
    """Get hero power level distribution statistics."""
    # 获取功率级别分布
    power_stats = db.exec(
        select(
            func.min(Hero.power_level).label("min_power"),
            func.max(Hero.power_level).label("max_power"),
            func.avg(Hero.power_level).label("avg_power"),
            func.count(Hero.id).label("total_heroes"),
        ).where(Hero.is_active)
    ).first()

    # 按功率级别范围分组
    power_ranges = [
        (1, 20, "Low"),
        (21, 50, "Medium"),
        (51, 80, "High"),
        (81, 100, "Legendary"),
    ]

    distribution = []
    for min_power, max_power, label in power_ranges:
        count = db.exec(
            select(func.count(Hero.id)).where(
                Hero.power_level >= min_power,
                Hero.power_level <= max_power,
                Hero.is_active,
            )
        ).first()

        distribution.append(
            {"range": f"{min_power}-{max_power}", "label": label, "count": count}
        )

    power_distribution_data = {
        "statistics": {
            "min_power": power_stats.min_power,
            "max_power": power_stats.max_power,
            "avg_power": (
                round(power_stats.avg_power, 2) if power_stats.avg_power else 0
            ),
            "total_heroes": power_stats.total_heroes,
        },
        "distribution": distribution,
    }
    return ApiResponse.success_response(
        data=power_distribution_data, message="能力分布统计获取成功"
    )
