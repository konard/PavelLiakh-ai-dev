from src.app.service.user_file_service import DEFAULT_FILE, BIG_FILE
from src.app.service.entities import (
    ROLE_RNP,
    ConversationMessage,
    ROLE_ADMIN,
    NOT_AUTHORIZED_RESPONSE,
    ERROR_RESPONSE,
    UserFile,
    UserContext,
    User,
)
from src.infrastructure.telegram.file_downloader import download_file
from src.config import config
from src.infrastructure.telegram.telegram_api import reply_to_telegram
from src.ioc import conversation_service, users_service, error_service, user_file_service
from src.app.register.data_analyst import analyze_task

from src.ioc import log
from src.ioc import user_file_service
from src.infrastructure.file_helper import download_file_from_url


async def check_authorization(update, message: ConversationMessage) -> bool:
    """Check if user has the required role"""
    user = users_service.get_or_create_user_by_message(message)
    is_authorized = (ROLE_ADMIN in user.roles) or (ROLE_RNP in user.roles)
    if not is_authorized:
        message.response = NOT_AUTHORIZED_RESPONSE
        conversation_service.save(message)
        await reply_to_telegram(update, NOT_AUTHORIZED_RESPONSE)
    return is_authorized


async def update(update, context):
    """Handle /update command"""
    message = conversation_service.build(update, config.manager_bot_link)
    log.info(f"Received /update command from user {message.telegram_user_id}")

    if not await check_authorization(update, message):
        return

    try:
        # Get filename from command arguments
        if not context.args or len(context.args) < 1:
            response = "Please specify a filename to update. Usage: /update filename"
            message.response = response
            await reply_to_telegram(update, response)
            return

        filename = " ".join(context.args)

        # Re-download and update the file
        user = users_service.get_or_create_user_by_message(message)
        updated_file = user_file_service.update_file_from_url(
            user_id=user.telegram_id, filename=filename
        )

        if updated_file:
            response = f"File '{filename}' updated successfully"
        else:
            response = f"File '{filename}' not found or failed to update"

        message.response = response
        conversation_service.save(message)
        await reply_to_telegram(update, response)
    except Exception as e:
        error_service.log_error(user_id=message.telegram_user_id, message="/update", error=e)
        message.response = ERROR_RESPONSE
        await reply_to_telegram(update, ERROR_RESPONSE)


async def add(update, context):
    """Handle /add command"""
    message = conversation_service.build(update, config.manager_bot_link)
    log.info(f"Received /add command from user {message.telegram_user_id}")

    if not await check_authorization(update, message):
        return

    try:
        # Get URL from command arguments
        if not context.args or len(context.args) < 1:
            response = "Please provide a file URL. Usage: /add <file_url>"
            message.response = response
            await reply_to_telegram(update, response)
            return

        file_url = " ".join(context.args)
        file = download_file_from_url(file_url)

        # Add file to user
        user = users_service.get_or_create_user_by_message(message)
        original_filename = file_url.split("/")[-1]  # Get filename from URL
        user_with_file = user_file_service.add_file_to_user(
            user_id=user.telegram_id,
            file=file,
        )

        if user_with_file:
            response = f"File '{original_filename}' added successfully with URL: {file_url}"
        else:
            response = "Failed to add file. Please check the URL and try again."

        message.response = response
        conversation_service.save(message)
        await reply_to_telegram(update, response)
    except Exception as e:
        error_service.log_error(user_id=message.telegram_user_id, message="/add", error=e)
        message.response = ERROR_RESPONSE
        await reply_to_telegram(update, ERROR_RESPONSE)


async def delete(update, context):
    """Handle /delete command"""
    message = conversation_service.build(update, config.manager_bot_link)
    log.info(f"Received /delete command from user {message.telegram_user_id}")

    if not await check_authorization(update, message):
        return

    try:
        # Get filename from command arguments
        if not context.args or len(context.args) < 1:
            response = "Please specify a filename to delete. Usage: /delete filename"
            message.response = response
            await reply_to_telegram(update, response)
            return

        filename = " ".join(context.args)
        user = users_service.get_or_create_user_by_message(message)
        deleted = user_file_service.remove_file(user.telegram_id, filename)

        if deleted:
            response = f"File '{filename}' deleted successfully"
        else:
            response = f"File '{filename}' not found"

        message.response = response
        conversation_service.save(message)
        await reply_to_telegram(update, response)
    except Exception as e:
        error_service.log_error(user_id=message.telegram_user_id, message="/delete", error=e)
        message.response = ERROR_RESPONSE
        await reply_to_telegram(update, ERROR_RESPONSE)


async def select(update, context):
    """Handle /select command to set current file"""
    message = conversation_service.build(update, config.manager_bot_link)
    log.info(f"Received /select command from user {message.telegram_user_id}")

    if not await check_authorization(update, message):
        return

    try:
        # Get filename from command arguments
        if not context.args or len(context.args) < 1:
            response = "Please specify a filename to select. Usage: /select filename"
            message.response = response
            await reply_to_telegram(update, response)
            return

        filename = " ".join(context.args)
        user = users_service.get_or_create_user_by_message(message)

        # Verify file exists
        files = user_file_service.get_user_files(user.telegram_id)
        has_file = any(f.original_filename == filename for f in files)
        embed_file = filename in [DEFAULT_FILE, BIG_FILE]
        if not has_file and not embed_file:
            response = f"File '{filename}' not found in your files"
            message.response = response
            await reply_to_telegram(update, response)
            return

        # Update current file in context
        if user.context is None:
            user.context = UserContext()
        user.context.current_file = filename
        users_service.storage.save_user(user)

        response = f"Selected file '{filename}' as current file"
        message.response = response
        conversation_service.save(message)
        await reply_to_telegram(update, response)
    except Exception as e:
        error_service.log_error(user_id=message.telegram_user_id, message="/select", error=e)
        message.response = ERROR_RESPONSE
        await reply_to_telegram(update, ERROR_RESPONSE)


async def start(update, context):
    """Handle /start command"""
    message = conversation_service.build(update, config.manager_bot_link)
    log.info(f"Received /start command from user {message.telegram_user_id}")

    if not await check_authorization(update, message):
        return

    try:
        response = """Available commands:
/files - List your uploaded files
/add <url> - Add a file by URL
/delete <filename> - Delete a file
/select <filename> - Select a file for analysis

To upload a file, simply send any .csv file without any text message."""

        message.response = response
        conversation_service.save(message)
        await reply_to_telegram(update, response)
    except Exception as e:
        error_service.log_error(user_id=message.telegram_user_id, message="/start", error=e)
        message.response = ERROR_RESPONSE
        await reply_to_telegram(update, ERROR_RESPONSE)


async def files(update, context):
    """Handle /files command"""
    message = conversation_service.build(update, config.manager_bot_link)
    log.info(f"Received /files command from user {message.telegram_user_id}")

    if not await check_authorization(update, message):
        return

    try:
        user = users_service.get_or_create_user_by_message(message)
        files = user_file_service.get_user_files(user.telegram_id)

        file_list = [DEFAULT_FILE, BIG_FILE]
        if files:
            file_list.extend(file.original_filename for file in files)

        response = "Your files:\n" + "\n".join(
            f"{i + 1}. {file}" for i, file in enumerate(file_list)
        )
        response += "\nCurrent: " + user_file_service.get_current_filename(user)

        message.response = response
        conversation_service.save(message)
        await reply_to_telegram(update, response)
    except Exception as e:
        error_service.log_error(user_id=message.telegram_user_id, message="/files", error=e)
        message.response = ERROR_RESPONSE
        await reply_to_telegram(update, ERROR_RESPONSE)


async def echo(update, context):
    """Handle text messages"""
    message = conversation_service.build(update, config.manager_bot_link)
    log.info(f"Received message from user {message.telegram_user_id}: {message.text}")

    if not await check_authorization(update, message):
        return

    try:
        user = users_service.get_or_create_user_by_message(message)
        rnp_response = analyze_task(message.text, user)
        rnp_response = f"{rnp_response.explanations_and_details}"

        message.response = rnp_response
        conversation_service.save(message)
        await reply_to_telegram(update, message.response)
    except Exception as e:
        error_service.log_error(user_id=message.telegram_user_id, message=message.text, error=e)
        message.response = ERROR_RESPONSE
        await reply_to_telegram(update, ERROR_RESPONSE)


async def document(update, context):
    """Handle document uploads"""
    message = conversation_service.build(update, config.manager_bot_link)
    log.info(f"Received document from user {message.telegram_user_id}")

    if not await check_authorization(update, message):
        return

    log.info(f"Received file message with document: {update.message.document}")
    if update.message.document.mime_type != "text/csv":
        log.warning(f"Received non-CSV file with mime_type: {update.message.document.mime_type}")
        response = "Only CSV files are supported"
        message.response = response
        await reply_to_telegram(update, response)
        return

    try:
        doc = update.message.document
        log.info(f"Processing file upload: {doc.file_name} (size: {doc.file_size} bytes)")
        user = users_service.get_or_create_user_by_message(message)
        log.info(f"User {user.telegram_id} uploading file")

        log.info(f"Starting file download for file_id: {doc.file_id}")
        downloaded_file = download_file(doc.file_id, config.rnp_bot_token)
        if not downloaded_file:
            log.error(f"Failed to download file '{doc.file_name}'")
            response = f"Failed to download file '{doc.file_name}'"
            message.response = response
            await reply_to_telegram(update, response)
            return
        log.info(f"File downloaded successfully: {downloaded_file.original_filename}")

        saved_file = user_file_service.add_file_to_user(
            user_id=user.telegram_id,
            file=UserFile(
                original_filename=doc.file_name,
                original_url=downloaded_file.original_url,
                size=downloaded_file.size,
                path=downloaded_file.path,
            ),
        )

        if saved_file:
            log.info(f"File '{doc.file_name}' added successfully to user {user.telegram_id}")
            response = f"File '{doc.file_name}' added successfully"
        else:
            log.error(f"Failed to add file '{doc.file_name}' for user {user.telegram_id}")
            response = "Failed to add file"

        message.response = response
        conversation_service.save(message)
        await reply_to_telegram(update, response)
        return

    except Exception as e:
        error_service.log_error(user_id=message.telegram_user_id, message=message.text, error=e)
        message.response = ERROR_RESPONSE
