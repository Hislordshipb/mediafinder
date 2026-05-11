# mfinder/db/migrations.py
from sqlalchemy import text
from mfinder.db.files_sql import SESSION, Files
from mfinder.db.settings_sql import SESSION as SETTINGS_SESSION
from mfinder import LOGGER
from datetime import datetime


def migrate_user_settings():
    """Migration for user search settings defaults"""
    session = SETTINGS_SESSION()
    try:
        LOGGER.info("🔄 Running User Settings Migration...")

        session.execute(text("""
            UPDATE settings 
            SET precise_mode = TRUE 
            WHERE precise_mode IS NULL
        """))
        
        session.execute(text("""
            UPDATE settings 
            SET button_mode = TRUE 
            WHERE button_mode IS NULL
        """))
        
        session.execute(text("""
            UPDATE settings 
            SET link_mode = FALSE 
            WHERE link_mode IS NULL
        """))
        
        session.execute(text("""
            UPDATE settings 
            SET list_mode = FALSE 
            WHERE list_mode IS NULL
        """))

        session.commit()
        LOGGER.info("✅ User Settings Migration Completed!")
        
    except Exception as e:
        session.rollback()
        LOGGER.error(f"User settings migration failed: {e}")
    finally:
        session.close()


def migrate_files_table():
    """All migrations related to the 'files' table"""
    session = SESSION()
    try:
        LOGGER.info("🔄 Running Files Table Migration...")

        # 1. indexed_at column
        result = session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'files' AND column_name = 'indexed_at'
        """))
        
        if not result.fetchone():
            LOGGER.info("Adding 'indexed_at' column...")
            session.execute(text("""
                ALTER TABLE files 
                ADD COLUMN IF NOT EXISTS indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """))
            LOGGER.info("✅ indexed_at column added")
        else:
            LOGGER.info("✅ indexed_at already exists")

        # 2. daily_search_count
        result = session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'files' AND column_name = 'daily_search_count'
        """))
        
        if not result.fetchone():
            LOGGER.info("Adding 'daily_search_count' column...")
            session.execute(text("""
                ALTER TABLE files 
                ADD COLUMN IF NOT EXISTS daily_search_count BIGINT DEFAULT 0
            """))
            LOGGER.info("✅ daily_search_count added")
        else:
            LOGGER.info("✅ daily_search_count already exists")

        # 3. weekly_search_count
        result = session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'files' AND column_name = 'weekly_search_count'
        """))
        
        if not result.fetchone():
            LOGGER.info("Adding 'weekly_search_count' column...")
            session.execute(text("""
                ALTER TABLE files 
                ADD COLUMN IF NOT EXISTS weekly_search_count BIGINT DEFAULT 0
            """))
            LOGGER.info("✅ weekly_search_count added")
        else:
            LOGGER.info("✅ weekly_search_count already exists")

        session.commit()
        LOGGER.info("✅ Files Table Migration Completed!")

    except Exception as e:
        session.rollback()
        LOGGER.error(f"Files migration failed: {e}")
    finally:
        session.close()


def run_all_migrations():
    """Run all migrations at once"""
    LOGGER.info("🚀 Starting All Database Migrations...")
    migrate_user_settings()
    migrate_files_table()
    LOGGER.info("🎉 All Migrations Finished!")


# Optional: One-time data backfill for indexed_at
def backfill_indexed_at():
    """Set indexed_at = created_at or current time for old records"""
    session = SESSION()
    try:
        LOGGER.info("🔄 Backfilling indexed_at for old files...")
        session.execute(text("""
            UPDATE files 
            SET indexed_at = CURRENT_TIMESTAMP 
            WHERE indexed_at IS NULL
        """))
        session.commit()
        LOGGER.info("✅ indexed_at backfill completed")
    except Exception as e:
        LOGGER.error(f"Backfill failed: {e}")
    finally:
        session.close()
