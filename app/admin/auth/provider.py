from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminConfig, AdminUser, AuthProvider
from starlette_admin.exceptions import LoginFailed

from config import SETTINGS


class CustomAuthProvider(AuthProvider):
    """Simple username/password auth provider."""

    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        if username == SETTINGS.admin_login and password == SETTINGS.admin_password:
            request.session.update({"username": username})
            return response

        raise LoginFailed("Invalid username or password")

    async def is_authenticated(self, request: Request) -> bool:
        username = request.session.get("username")
        if username == SETTINGS.admin_login:
            request.state.user = {"username": username, "roles": ["admin"]}
            return True
        return False

    def get_admin_config(self, request: Request) -> AdminConfig:
        return AdminConfig(app_title="Mobile Cloaking Admin")

    def get_admin_user(self, request: Request) -> AdminUser:
        user = request.state.user
        return AdminUser(username=user["username"])

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response
