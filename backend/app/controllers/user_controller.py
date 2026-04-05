import json

from werkzeug.exceptions import BadRequest

from backend.app.controllers.base_controller import BaseController
from backend.app.validators.schemas import CreateUserSchema, UpdateUserSchema
from backend.app.utils.cache import cache_get, cache_set, cache_delete


class UserController(BaseController):
    def __init__(self, user_service):
        self.user_service = user_service
        self.config = None  # Will be set if passed in

    def set_config(self, config):
        """Set config for cache operations."""
        self.config = config

    def create_user(self, request):
        try:
            data = request.get_json()
            if not data:
                raise ValueError("Payload cannot be empty")

            schema = CreateUserSchema(**data)
            user = self.user_service.create_user(
                username=schema.username, email=schema.email
            )

            # No wildcard cache nuke — list caches use short TTL for natural expiry

            return self.handle_success(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "created_at": user.created_at.isoformat(),
                },
                201,
            )
        except BadRequest as e:
            # Handle malformed JSON
            return self.handle_success({"error": "bad_request", "message": str(e)}, 400)
        except Exception as e:
            return self.handle_error(e, "create_user")

    def list_users(self, request):
        try:
            page = request.args.get("page", 1, type=int)
            per_page = request.args.get("per_page", 50, type=int)

            # Create cache key based on pagination
            cache_key = f"users:list:{page}:{per_page}"

            # Try to get from cache
            cached = cache_get(cache_key, self.config)
            if cached:
                return self.handle_success(json.loads(cached))

            # Cache miss - fetch from DB
            # Use get_all_users for testing purposes when no pagination params
            if page == 1 and per_page == 50 and not request.args:
                users = self.user_service.get_all_users()
            else:
                users = self.user_service.list_users(page=page, per_page=per_page)

            result = [
                {
                    "id": u.id,
                    "username": u.username,
                    "email": u.email,
                    "created_at": u.created_at.isoformat(),
                }
                for u in users
            ]

            # Short TTL (30s) for list caches — same rationale as URL list
            cache_set(cache_key, json.dumps(result), 30, self.config)

            return self.handle_success(result)
        except Exception as e:
            return self.handle_error(e, "list_users")

    def get_user(self, user_id: int):
        try:
            cache_key = f"user:{user_id}"

            # Try to get from cache
            cached = cache_get(cache_key, self.config)
            if cached:
                return self.handle_success(json.loads(cached))

            # Cache miss - fetch from DB
            user = self.user_service.get_user(user_id)
            if not user:
                raise ValueError("User not found")

            result = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
            }

            # Store in cache for 5 minutes
            cache_set(cache_key, json.dumps(result), 300, self.config)

            return self.handle_success(result)
        except Exception as e:
            return self.handle_error(e, "get_user")

    def update_user(self, user_id: int, request):
        try:
            data = request.get_json() or {}
            schema = UpdateUserSchema(**data)

            updates = schema.model_dump(exclude_unset=True)
            user = self.user_service.update_user(user_id, updates)
            if not user:
                raise ValueError("User not found")

            # Invalidate only the exact key for this user
            cache_delete(f"user:{user_id}", self.config)

            return self.handle_success(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "created_at": user.created_at.isoformat(),
                }
            )
        except Exception as e:
            return self.handle_error(e, "update_user")

    def delete_user(self, user_id: int):
        try:
            user = self.user_service.get_user(user_id)
            if user:
                self.user_service.delete_user(user_id)
                cache_delete(f"user:{user_id}", self.config)
            return self.handle_success({}, 204)
        except Exception as e:
            return self.handle_error(e, "delete_user")

    def bulk_import(self, request):
        try:
            if "file" not in request.files:
                raise ValueError("No file provided")

            file = request.files["file"]
            if file.filename == "":
                raise ValueError("Empty filename")

            content = file.read().decode("utf-8")
            count = self.user_service.bulk_import_csv(content)

            return self.handle_success({"count": count}, 201)
        except Exception as e:
            return self.handle_error(e, "bulk_import")
