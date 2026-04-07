from nicegui import ui

from src._core.infrastructure.admin.auth import require_auth
from src._core.infrastructure.admin.base_admin_page import (
    BaseAdminPage,
    ColumnConfig,
)
from src._core.infrastructure.admin.layout import admin_layout
from src._core.infrastructure.admin.renderers import (
    render_detail_page,
    render_list_page,
)

user_admin_page = BaseAdminPage(
    domain_name="user",
    display_name="User",
    icon="person",
    columns=[
        ColumnConfig(field_name="id", header_name="ID", width=80),
        ColumnConfig(field_name="username", header_name="Username", searchable=True),
        ColumnConfig(field_name="full_name", header_name="Full Name"),
        ColumnConfig(field_name="email", header_name="Email", searchable=True),
        ColumnConfig(field_name="password", header_name="Password", masked=True),
        ColumnConfig(field_name="created_at", header_name="Created At"),
        ColumnConfig(field_name="updated_at", header_name="Updated At"),
    ],
    searchable_fields=["username", "email"],
    sortable_fields=["id", "username", "created_at"],
    default_sort_field="id",
)


def register_pages(all_page_configs, admin_container) -> None:
    """Register user domain admin pages."""
    user_container = admin_container.user_container

    @ui.page("/admin/user")
    async def user_list_page(page: int = 1, search: str = ""):
        if not require_auth():
            return
        admin_layout(all_page_configs, current_domain="user")

        service = user_container.user_service()
        await render_list_page(
            page_config=user_admin_page, service=service, page=page, search=search
        )

    @ui.page("/admin/user/{record_id}")
    async def user_detail_page(record_id: int):
        if not require_auth():
            return
        admin_layout(all_page_configs, current_domain="user")

        service = user_container.user_service()
        await render_detail_page(
            page_config=user_admin_page, service=service, record_id=record_id
        )
