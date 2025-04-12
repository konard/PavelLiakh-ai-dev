from src.app.service.entities import ROLE_CODEWRITER, ROLE_RNP
from src.infrastructure.db.json_storage import MongoStorage
from src.app.service.entities import ConversationMessage, User, ROLE_ASSISTANT, ERROR_RESPONSE

roles = [ROLE_ASSISTANT, ROLE_RNP, ROLE_CODEWRITER]


class UsersService:
    def __init__(self, storage: MongoStorage, log, error_service):
        self.storage = storage
        self.log = log
        self.error_service = error_service

    def get_or_create_user_by_message(self, message: ConversationMessage) -> User:
        user_id = message.telegram_user_id
        user_name = message.telegram_user_name
        user_link = message.telegram_user_link

        """Get existing user or create new one from message data"""
        if user_id:
            user = self.storage.find_user_by_telegram_id(user_id)
        else:
            user = None

        if user_link and not user:
            user_link = self.get_pure_telegram_link(user_link)
            user = self.storage.find_user_by_telegram_link(user_link)

        if not user:
            # Create new user from message data
            user = User(
                telegram_id=user_id or "",
                telegram_name=user_name or "",
                telegram_link=(self.get_pure_telegram_link(user_link) if user_link else ""),
                roles=[],
            )
            self.storage.save_user(user)
            return user

        # Update existing user's profile info if needed
        needs_update = False

        if user_id and not user.telegram_id:
            user.telegram_id = user_id
            needs_update = True

        if user_name and user.telegram_name != user_name:
            user.telegram_name = user_name
            needs_update = True

        if user_link and user.telegram_link != user_link:
            user_link = self.get_pure_telegram_link(user_link)
            user.telegram_link = user_link
            needs_update = True

        if needs_update:
            self.storage.save_user(user)

        return user

    def get_all_users(self) -> list[User]:
        """Get all users from storage"""
        return self.storage.get_all_users()

    async def grant_user_access(self, telegram_id_or_link: str, role: str) -> str:
        """Grant user access by adding role"""
        if role not in roles:
            return "Invalid role. Available: " + ", ".join(roles)

        valid_identifier, reason = self.is_valid_identifier_for_registration(telegram_id_or_link)
        if not valid_identifier:
            return reason

        try:
            self.log.info(
                "Grant user with telegram ID or link: %s, grant %s", telegram_id_or_link, role
            )
            user = self.get_or_create_user(telegram_id_or_link)

            if role in user.roles:
                return "User already authorized to " + role

            user.roles.append(role)
            self.storage.save_user(user)
            self.log.info("User %s granted successfully to %s", telegram_id_or_link, role)

            return f"User {self.get_display_name(user)} authorized successfully to {role}"

        except Exception as e:
            self.error_service.log_error(
                user_id="system",
                message=f"Authorization attempt: {telegram_id_or_link}",
                error=e,
            )
            return ERROR_RESPONSE

    async def revoke_user_access(self, telegram_id_or_link: str, role: str) -> str:
        """Revoke user access by removing role"""
        if not telegram_id_or_link:
            return "Telegram ID or link cannot be empty"

        if role not in roles:
            return "Invalid role. Available: " + ", ".join(roles)

        valid_identifier, reason = self.is_valid_identifier_for_registration(telegram_id_or_link)
        if not valid_identifier:
            return reason

        user = self.get_or_create_user(telegram_id_or_link)

        try:
            if role not in user.roles:
                return "User already doesn't have access to " + role

            user.roles.remove(role)
            self.storage.save_user(user)
            self.log.info("User %s access revoked successfully from %s", telegram_id_or_link, role)
            return f"User {self.get_display_name(user)} access revoked successfully for {role}"

        except Exception as e:
            self.error_service.log_error(
                user_id="system",
                message=f"Revocation attempt: {telegram_id_or_link}",
                error=e,
            )
            return ERROR_RESPONSE

    def is_valid_identifier_for_registration(self, telegram_id_or_link: str) -> [bool, str]:
        """Check if user can be registered with given identifier"""
        if not telegram_id_or_link:
            return False, "Telegram ID or link cannot be empty"

        if self.is_link(telegram_id_or_link):
            return True, ""

        if telegram_id_or_link.isdigit():
            return True, ""

        return (
            False,
            "Invalid telegram ID or link. Telegram link must start with @ or t.me/. Telegram ID must be a number.",
        )

    def get_display_name(self, user: User) -> str:
        """Get user-friendly name for printing"""
        display_name = ""
        if user.telegram_name:
            display_name = user.telegram_name

        if display_name:
            if user.telegram_link:
                display_name += f"(@{user.telegram_link})"
        else:
            if user.telegram_link:
                display_name = f"@{user.telegram_link}"
            else:
                display_name = user.telegram_id

        return display_name

    def get_or_create_user(self, id_or_link: str):
        """Get existing user or create new one from message data"""
        is_link = self.is_link(id_or_link)

        if is_link:
            pure_link = self.get_pure_telegram_link(id_or_link)
            user = self.storage.find_user_by_telegram_link(pure_link)
            if user:
                self.log.info("User found by telegram link: %s", pure_link)
                return user

            self.log.info("Creating user with telegram link: %s", pure_link)
            user = User(telegram_link=pure_link)
            self.storage.save_user(user)
            return user

        user = self.storage.find_user_by_telegram_id(id_or_link)
        if user:
            self.log.info("User found by telegram ID: %s", id_or_link)
            return user

        self.log.info("Creating user with telegram ID: %s", id_or_link)
        user = User(telegram_id=id_or_link)
        self.storage.save_user(user)
        return user

    def get_pure_telegram_link(self, telegram_link: str) -> str:
        """Get telegram link without @ or t.me/"""
        return telegram_link.replace("@", "").replace("https://t.me/", "").replace("t.me/", "")

    def is_link(self, telegram_link: str) -> bool:
        """Check if string is a telegram link"""
        return "t.me" in telegram_link or "@" in telegram_link
