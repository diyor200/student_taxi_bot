"""Import all routers and add them to routers_list."""
from .admin import admin_router
from .driver import driver_router
from .user import user_router
from .start import start_router

routers_list = [
    admin_router,
    start_router,
    user_router,
    driver_router,
]

__all__ = [
    "routers_list",
]
