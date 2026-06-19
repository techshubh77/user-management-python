from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event
from sqlalchemy.orm import ORMExecuteState, with_loader_criteria, Session


from app.config.settings import settings


engine = create_async_engine(
    settings.database_url,
    echo=False,
)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


@event.listens_for(Session, "do_orm_execute")
def _add_soft_delete_filter(execute_state: ORMExecuteState):
    """
    Global middleware to automatically exclude soft-deleted records.
    Behaves exactly like Sequelize's paranoid: true.
    """
    if (
        execute_state.is_select
        and not execute_state.is_column_load
        and not execute_state.is_relationship_load
    ):
        if not execute_state.execution_options.get("include_deleted", False):
            execute_state.statement = execute_state.statement.options(
                with_loader_criteria(
                    Base,
                    # Dynamically check if the model has a deleted_at column
                    lambda cls: (
                        cls.deleted_at.is_(None) if hasattr(cls, "deleted_at") else None
                    ),
                    include_aliases=True,
                )
            )


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()

        except Exception:
            await session.rollback()
            raise
