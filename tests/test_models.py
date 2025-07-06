"""Tests for database models."""

import json

import pytest
from sqlmodel import Session, SQLModel, create_engine, select

from src.models.hero import Hero, HeroCreate
from src.models.user import User, UserCreate, UserUpdate
from src.utils.security import get_password_hash, verify_password


@pytest.fixture
def engine():
    """Create in-memory SQLite engine for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Create database session for testing."""
    with Session(engine) as session:
        yield session


class TestUserModel:
    """Test cases for User model."""

    def test_create_user(self, session):
        """Test creating a new user."""
        password_hash = get_password_hash("TestPass123")
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="TestPass123",
            password_hash=password_hash,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.created_at is not None
        assert verify_password("TestPass123", user.password_hash)

    def test_user_create_schema(self):
        """Test UserCreate schema validation."""
        user_data = UserCreate(
            username="newuser",
            email="new@example.com",
            password="ValidPass123",
            full_name="New User",
        )

        assert user_data.username == "newuser"
        assert user_data.email == "new@example.com"
        assert user_data.password == "ValidPass123"
        assert user_data.full_name == "New User"
        assert user_data.is_active is True

    def test_user_update_schema(self):
        """Test UserUpdate schema."""
        update_data = UserUpdate(full_name="Updated Name", is_active=False)

        assert update_data.full_name == "Updated Name"
        assert update_data.is_active is False
        assert update_data.username is None
        assert update_data.email is None

    def test_query_user_by_username(self, session):
        """Test querying user by username."""
        user = User(
            username="queryuser",
            email="query@example.com",
            password="password123",
            password_hash=get_password_hash("password123"),
        )
        session.add(user)
        session.commit()

        found_user = session.exec(
            select(User).where(User.username == "queryuser")
        ).first()

        assert found_user is not None
        assert found_user.username == "queryuser"
        assert found_user.email == "query@example.com"

    def test_query_user_by_email(self, session):
        """Test querying user by email."""
        user = User(
            username="emailuser",
            email="email@example.com",
            password="password123",
            password_hash=get_password_hash("password123"),
        )
        session.add(user)
        session.commit()

        found_user = session.exec(
            select(User).where(User.email == "email@example.com")
        ).first()

        assert found_user is not None
        assert found_user.username == "emailuser"
        assert found_user.email == "email@example.com"


class TestHeroModel:
    """Test cases for Hero model."""

    def test_create_hero(self, session):
        """Test creating a new hero."""
        hero = Hero(
            name="Spider-Man",
            secret_name="Peter Parker",
            age=25,
            power_level=75,
            description="Friendly neighborhood Spider-Man",
        )
        session.add(hero)
        session.commit()
        session.refresh(hero)

        assert hero.id is not None
        assert hero.name == "Spider-Man"
        assert hero.secret_name == "Peter Parker"
        assert hero.age == 25
        assert hero.power_level == 75
        assert hero.is_active is True
        assert hero.created_at is not None

    def test_hero_create_schema(self):
        """Test HeroCreate schema validation."""
        hero_data = HeroCreate(
            name="Iron Man",
            secret_name="Tony Stark",
            age=45,
            power_level=90,
            description="Genius, billionaire, playboy, philanthropist",
            team="Avengers",
            abilities=["Flight", "Repulsors", "Super Strength"],
        )

        assert hero_data.name == "Iron Man"
        assert hero_data.secret_name == "Tony Stark"
        assert hero_data.age == 45
        assert hero_data.power_level == 90
        assert hero_data.team == "Avengers"
        assert "Flight" in hero_data.abilities

    def test_hero_with_abilities_json(self, session):
        """Test hero with abilities stored as JSON."""
        abilities = ["Web-slinging", "Spider-sense", "Wall-crawling"]
        hero = Hero(
            name="Spider-Man",
            secret_name="Peter Parker",
            age=25,
            power_level=75,
            abilities=json.dumps(abilities),
        )
        session.add(hero)
        session.commit()
        session.refresh(hero)

        # Parse abilities back from JSON
        stored_abilities = json.loads(hero.abilities) if hero.abilities else []
        assert stored_abilities == abilities
        assert "Web-slinging" in stored_abilities

    def test_query_hero_by_name(self, session):
        """Test querying hero by name."""
        hero = Hero(name="Batman", secret_name="Bruce Wayne", age=35, power_level=85)
        session.add(hero)
        session.commit()

        found_hero = session.exec(select(Hero).where(Hero.name == "Batman")).first()

        assert found_hero is not None
        assert found_hero.name == "Batman"
        assert found_hero.secret_name == "Bruce Wayne"

    def test_query_heroes_by_team(self, session):
        """Test querying heroes by team."""
        heroes_data = [
            {
                "name": "Captain America",
                "secret_name": "Steve Rogers",
                "team": "Avengers",
                "power_level": 80,
            },
            {
                "name": "Iron Man",
                "secret_name": "Tony Stark",
                "team": "Avengers",
                "power_level": 90,
            },
            {
                "name": "Batman",
                "secret_name": "Bruce Wayne",
                "team": "Justice League",
                "power_level": 85,
            },
        ]

        for hero_data in heroes_data:
            hero = Hero(**hero_data)
            session.add(hero)

        session.commit()

        avengers = session.exec(select(Hero).where(Hero.team == "Avengers")).all()

        assert len(avengers) == 2
        avenger_names = [hero.name for hero in avengers]
        assert "Captain America" in avenger_names
        assert "Iron Man" in avenger_names

    def test_query_heroes_by_power_level(self, session):
        """Test querying heroes by power level range."""
        heroes_data = [
            {"name": "Hero1", "secret_name": "Secret1", "power_level": 30},
            {"name": "Hero2", "secret_name": "Secret2", "power_level": 60},
            {"name": "Hero3", "secret_name": "Secret3", "power_level": 90},
        ]

        for hero_data in heroes_data:
            hero = Hero(**hero_data)
            session.add(hero)

        session.commit()

        # Query heroes with power level >= 50
        powerful_heroes = session.exec(select(Hero).where(Hero.power_level >= 50)).all()

        assert len(powerful_heroes) == 2
        power_levels = [hero.power_level for hero in powerful_heroes]
        assert 60 in power_levels
        assert 90 in power_levels

    def test_update_hero(self, session):
        """Test updating a hero."""
        hero = Hero(name="Flash", secret_name="Barry Allen", age=28, power_level=85)
        session.add(hero)
        session.commit()
        session.refresh(hero)

        # Update hero
        hero.age = 29
        hero.power_level = 90
        hero.team = "Justice League"
        session.add(hero)
        session.commit()
        session.refresh(hero)

        assert hero.age == 29
        assert hero.power_level == 90
        assert hero.team == "Justice League"

    def test_soft_delete_hero(self, session):
        """Test soft deleting a hero (deactivate)."""
        hero = Hero(
            name="Green Lantern", secret_name="Hal Jordan", age=32, power_level=88
        )
        session.add(hero)
        session.commit()
        session.refresh(hero)

        # Soft delete (deactivate)
        hero.is_active = False
        session.add(hero)
        session.commit()
        session.refresh(hero)

        assert hero.is_active is False

        # Hero still exists in database
        found_hero = session.get(Hero, hero.id)
        assert found_hero is not None
        assert found_hero.is_active is False

    def test_delete_hero(self, session):
        """Test hard deleting a hero."""
        hero = Hero(name="Aquaman", secret_name="Arthur Curry", age=35, power_level=82)
        session.add(hero)
        session.commit()
        hero_id = hero.id

        # Hard delete
        session.delete(hero)
        session.commit()

        # Verify hero is deleted
        deleted_hero = session.get(Hero, hero_id)
        assert deleted_hero is None


class TestModelRelationships:
    """Test cases for model relationships and constraints."""

    def test_user_unique_constraints(self, session):
        """Test user unique constraints."""
        # Create first user
        user1 = User(
            username="uniqueuser",
            email="unique@example.com",
            password="password123",
            password_hash=get_password_hash("password123"),
        )
        session.add(user1)
        session.commit()

        # Try to create user with same username
        user2 = User(
            username="uniqueuser",  # Same username
            email="different@example.com",
            password="password123",
            password_hash=get_password_hash("password123"),
        )
        session.add(user2)

        with pytest.raises((Exception, ValueError)):  # Should raise integrity error
            session.commit()

    def test_hero_unique_constraints(self, session):
        """Test hero unique constraints."""
        # Create first hero
        hero1 = Hero(name="Unique Hero", secret_name="Secret Identity", power_level=75)
        session.add(hero1)
        session.commit()

        # Try to create hero with same name
        hero2 = Hero(
            name="Unique Hero",  # Same name
            secret_name="Different Secret",
            power_level=80,
        )
        session.add(hero2)

        with pytest.raises((Exception, ValueError)):  # Should raise integrity error
            session.commit()
