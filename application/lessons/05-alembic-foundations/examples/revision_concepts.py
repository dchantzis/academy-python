"""A migration's upgrade/downgrade functions are ordered schema changes.

Real Alembic configuration and migration history remain documented in README.md.
This example intentionally does not modify any database.
"""
def upgrade_plan() -> tuple[str, ...]:
    return ("create table", "add index")

def downgrade_plan() -> tuple[str, ...]:
    return tuple(reversed(upgrade_plan()))

if __name__ == "__main__":
    print("upgrade:", upgrade_plan())
    print("downgrade (conceptual only):", downgrade_plan())
