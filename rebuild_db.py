#!/usr/bin/env python3
"""Rebuild database tables."""

# Import all models to ensure they are registered with SQLModel
from src.db.connection import db
from src.models import Hero, User  # noqa: F401

if __name__ == "__main__":
    print("Dropping existing tables...")
    db.drop_tables()

    print("Creating new tables...")
    db.create_tables()

    print("Database tables recreated successfully!")
