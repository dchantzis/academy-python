"""The Session owns ORM state; transactions remain explicit."""
from academy_examples.models import seeded_session
session = seeded_session()
try:
    print("Session open:", session.is_active)
finally:
    session.close()
