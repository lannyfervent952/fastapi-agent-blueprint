from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from nicegui import ui

from src._core.domain.value_objects.query_filter import QueryFilter
from src._core.exceptions.base_exception import BaseCustomException

if TYPE_CHECKING:
    from src._core.infrastructure.admin.base_admin_page import BaseAdminPage

logger = logging.getLogger(__name__)


async def render_list_page(
    page_config: BaseAdminPage,
    service,
    page: int = 1,
    search: str = "",
) -> None:
    """Render a paginated AG Grid list view from BaseAdminPage config."""
    query_filter = QueryFilter(
        sort_field=page_config.default_sort_field,
        sort_order=page_config.default_sort_order,
        search_query=search or None,
        search_fields=page_config.searchable_fields if search else None,
    )

    try:
        dtos, pagination = await service.get_datas(
            page=page,
            page_size=page_config.page_size,
            query_filter=query_filter,
        )
    except BaseCustomException as e:
        logger.warning("Admin list load failed: %s", e)
        ui.notify(e.message, type="negative")
        return
    except Exception:
        logger.exception(
            "Unexpected error loading admin list for %s", page_config.domain_name
        )
        ui.notify("Failed to load data. Please try again later.", type="negative")
        return

    column_defs = _build_column_defs(page_config)
    masked_fields = page_config.get_masked_field_names()
    row_data = _build_row_data(dtos, masked_fields)

    ui.label(f"{page_config.display_name} Management").classes("text-h5 q-mb-md")

    # Search bar
    if page_config.searchable_fields:
        field_labels = ", ".join(page_config.searchable_fields)

        def _on_search(e) -> None:
            query = e.value.strip() if e.value else ""
            params = f"?search={query}" if query else ""
            ui.navigate.to(f"/admin/{page_config.domain_name}{params}")

        ui.input(
            placeholder=f"Search by {field_labels}...",
            value=search,
            on_change=lambda: None,
        ).on("keydown.enter", _on_search).props("outlined dense clearable").classes(
            "w-80 q-mb-sm"
        )

    with ui.row().classes("items-center q-mb-sm"):
        ui.label(
            f"Total: {pagination.total_items} | "
            f"Page {pagination.current_page} / {pagination.total_pages}"
        ).classes("text-caption")

    grid = (
        ui.aggrid(
            {
                "columnDefs": column_defs,
                "rowData": row_data,
                "rowSelection": {"mode": "singleRow"},
                "defaultColDef": {"resizable": True, "filter": True},
            }
        )
        .classes("w-full")
        .style("height: 600px")
    )

    grid.on(
        "cellClicked",
        lambda e: ui.navigate.to(
            f"/admin/{page_config.domain_name}/{e.args['data']['id']}"
        ),
    )

    def _build_page_url(target_page: int) -> str:
        params = f"page={target_page}"
        if search:
            params += f"&search={search}"
        return f"/admin/{page_config.domain_name}?{params}"

    with ui.row().classes("items-center q-mt-md q-gutter-sm"):
        ui.button(
            "Previous",
            on_click=lambda: ui.navigate.to(_build_page_url(pagination.previous_page)),
        ).props("flat" if pagination.has_previous else "flat disable")
        ui.label(f"{pagination.current_page} / {pagination.total_pages}")
        ui.button(
            "Next",
            on_click=lambda: ui.navigate.to(_build_page_url(pagination.next_page)),
        ).props("flat" if pagination.has_next else "flat disable")


def _build_column_defs(page_config: BaseAdminPage) -> list[dict]:
    """Build AG Grid column definitions from page config."""
    column_defs = []
    for col in page_config.get_visible_columns():
        col_def: dict = {
            "headerName": col.header_name,
            "field": col.field_name,
            "sortable": col.sortable,
        }
        if col.width:
            col_def["width"] = col.width
        if col.masked:
            col_def["valueFormatter"] = "value ? '****' : ''"
        column_defs.append(col_def)
    return column_defs


def _build_row_data(dtos: list, masked_fields: set[str]) -> list[dict]:
    """Build row data from DTOs, masking sensitive fields server-side."""
    rows = []
    for dto in dtos:
        row = dto.model_dump()
        for key, value in row.items():
            if key in masked_fields:
                row[key] = "****" if value else ""
            elif hasattr(value, "isoformat"):
                row[key] = value.isoformat()
        rows.append(row)
    return rows


async def render_detail_page(
    page_config: BaseAdminPage,
    service,
    record_id: int,
) -> None:
    """Render a detail view for a single record."""
    try:
        dto = await service.get_data_by_data_id(data_id=record_id)
    except BaseCustomException as e:
        logger.warning("Admin detail load failed: %s", e)
        ui.notify(e.message, type="negative")
        ui.button(
            "Back to list",
            on_click=lambda: ui.navigate.to(f"/admin/{page_config.domain_name}"),
        ).props("flat")
        return
    except Exception:
        logger.exception(
            "Unexpected error loading detail for %s #%s",
            page_config.domain_name,
            record_id,
        )
        ui.notify("Failed to load record. Please try again later.", type="negative")
        ui.button(
            "Back to list",
            on_click=lambda: ui.navigate.to(f"/admin/{page_config.domain_name}"),
        ).props("flat")
        return

    masked_fields = page_config.get_masked_field_names()
    data = dto.model_dump()

    with ui.row().classes("items-center q-mb-md q-gutter-sm"):
        ui.button(
            icon="arrow_back",
            on_click=lambda: ui.navigate.to(f"/admin/{page_config.domain_name}"),
        ).props("flat round")
        ui.label(f"{page_config.display_name} #{record_id}").classes("text-h5")

    with ui.card().classes("w-full"):
        for col in page_config.columns:
            value = data.get(col.field_name, "")
            if col.field_name in masked_fields:
                display_value = "****" if value else ""
            elif hasattr(value, "isoformat"):
                display_value = value.isoformat()
            else:
                display_value = str(value) if value is not None else ""

            with ui.row().classes("items-center q-py-xs"):
                ui.label(col.header_name).classes("text-weight-bold").style(
                    "width: 160px"
                )
                ui.label(display_value)
