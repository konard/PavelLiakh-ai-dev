import datetime
import threading
from concurrent.futures import Future
from pathlib import Path
from typing import Optional

from nicegui import ui, events, run
from nicegui.elements.table import Table

from src.config import config
from src.ioc import log, sku_storage, sku_service

table: Table = None
UPLOAD_FOLDER = config.get_folder("uploads")  # Using existing uploads folder from config
file_container: ui.column = None
processing_future: Optional[Future] = None


def get_file_list() -> list[Path]:
    """Get sorted list of files in upload folder"""
    return sorted(UPLOAD_FOLDER.glob("*"), key=lambda f: f.stat().st_mtime, reverse=True)


def delete_file(file_path: Path) -> None:
    """Delete file from disk"""
    try:
        file_path.unlink()
        ui.notify(f"Deleted: {file_path.name}", type="positive")
        update_files_list()
    except Exception as e:
        ui.notify(f"Error deleting {file_path.name}: {str(e)}", type="negative")


def update_files_list() -> None:
    """Update the file list display"""
    global file_container

    file_container.clear()
    files = get_file_list()

    if not files:
        with file_container:
            ui.label("No files uploaded yet").classes("text-gray-500")
        return

    for file_path in files:
        with file_container:
            with ui.card().classes("w-full p-4"):
                with ui.row().classes("items-center justify-between w-full"):
                    ui.label(file_path.name)
                    ui.button(icon="delete", on_click=lambda fp=file_path: delete_file(fp)).props(
                        "flat dense"
                    )


def _render_skus_table() -> None:
    """Handle file upload and refresh file list"""
    global table
    if table:
        table.rows.clear()
        skus = []
        for sku in skus:
            row_data = sku.__dict__
            table.add_row(row_data)


def data_tab() -> None:
    """Render the data tab with file upload and management"""
    global table, file_container

    with ui.column().classes("items-center w-full gap-4"):
        ui.label("Data Management").classes("text-2xl font-bold")

        with ui.card().classes("w-full p-4"):
            upload = (
                ui.upload(
                    label="Upload CSV File",
                    on_upload=lambda e: handle_file_upload(e),
                    auto_upload=True,
                )
                .props("accept=.csv")
                .classes("w-full")
            )

        with ui.card().classes("w-full p-4"):
            ui.label("Uploaded Files").classes("text-xl font-bold mb-4")
            file_container = ui.column().classes("w-full gap-2")
            update_files_list()

        with ui.row().classes("gap-4"):
            ui.button("Refresh List", icon="refresh", on_click=lambda: update_files_list()).classes(
                "w-48"
            )

            ui.button(
                "Upload All", icon="upload", on_click=lambda: ui.notify(process_all_files())
            ).classes("w-48")

        # SKU table section
        ui.label("SKU Data").classes("text-xl font-bold")
        table = ui.table(
            title="SKUs",
            pagination=10,
            columns=[
                {"name": "sku", "label": "SKU", "field": "number", "required": True},
                {"name": "category", "label": "category", "field": "category", "required": False},
            ],
            rows=[],
        )
        _render_skus_table()


def handle_file_upload(e: events.UploadEventArguments) -> None:
    """Handle file upload including saving and processing"""
    global file_container
    try:
        name = e.name
        content = e.content.read()
        random_prefix = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        target_filename = UPLOAD_FOLDER / f"{random_prefix}_{name}"

        with open(target_filename, "wb") as f:
            f.write(content)
            log.info(f"Saved uploaded file: {target_filename}")

        # Process file in a background thread
        threading.Thread(target=lambda: process_file(target_filename), daemon=True).start()

        # Update UI
        ui.notify(f"Uploaded and processing: {name}", type="positive")
        update_files_list()

    except Exception as ex:
        log.error(f"Error handling upload: {str(ex)}")
        ui.notify(f"Upload failed: {str(ex)}", type="negative")


def process_all_files() -> str:
    """Process all files in upload folder in background thread"""
    global processing_future

    if processing_future and not processing_future.done():
        return "File processing in progress"

    def process_files_task():
        sku_service.process_all_files()
        ui.notify("SKUs file processed", type="positive")
        update_files_list()

    processing_future = Future()
    thread = threading.Thread(
        target=lambda: (process_files_task(), processing_future.set_result(True)), daemon=True
    )
    thread.start()

    return "Processing started"


def process_file(target_filename: Path) -> None:
    """Process a specific file"""
    try:
        result = sku_service.process_file(str(target_filename.resolve()))
        ui.notify(f"Processed {target_filename.name}: {len(result)} SKUs found.", type="positive")
    except Exception as e:
        ui.notify(f"Error processing {target_filename.name}: {str(e)}", type="negative")
