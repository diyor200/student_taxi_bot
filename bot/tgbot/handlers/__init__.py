"""Import all routers and add them to routers_list."""
from .admin import admin_router
from .driver import driver_router
from .user import user_router
from .start import start_router
from .routes import routes_router
from .personal_account import account_router

routers_list = [
    admin_router,
    start_router,
    user_router,
    driver_router,
    routes_router,
    account_router,
]

__all__ = [
    "routers_list",
]
