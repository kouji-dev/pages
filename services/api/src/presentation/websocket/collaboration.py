"""WebSocket handlers for real-time collaboration."""

import json
from uuid import UUID

import socketio  # type: ignore[import-untyped,import-not-found]
import structlog

from src.application.services.collaboration_service import CollaborationService
from src.domain.repositories import (
    PageRepository,
    UserRepository,
)

logger = structlog.get_logger()

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",  # Configure appropriately for production
    logger=False,
    engineio_logger=False,
)


class CollaborationWebSocketHandler:
    """WebSocket handler for real-time collaboration."""

    def __init__(
        self,
        collaboration_service: CollaborationService,
        page_repository: PageRepository,
        user_repository: UserRepository,
    ) -> None:
        """Initialize WebSocket handler with dependencies.

        Args:
            collaboration_service: Collaboration service
            page_repository: Page repository
            user_repository: User repository
        """
        self._collaboration_service = collaboration_service
        self._page_repository = page_repository
        self._user_repository = user_repository

        # Register event handlers
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register Socket.IO event handlers."""

        @sio.event
        async def connect(sid: str, environ: dict, auth: dict | None) -> None:
            """Handle client connection.

            Args:
                sid: Socket session ID
                environ: WSGI environment
                auth: Authentication data
            """
            logger.info("Client connecting", socket_id=sid)
            # In production, verify JWT token from auth
            await sio.emit("connected", {"socket_id": sid}, room=sid)

        @sio.event
        async def disconnect(sid: str) -> None:
            """Handle client disconnection.

            Args:
                sid: Socket session ID
            """
            logger.info("Client disconnecting", socket_id=sid)
            await self._collaboration_service.disconnect_socket(sid)

        @sio.event
        async def join_page(sid: str, data: dict) -> None:
            """Handle joining a page room.

            Args:
                sid: Socket session ID
                data: Event data with page_id and user_id
            """
            try:
                page_id = UUID(data.get("page_id"))
                user_id = UUID(data.get("user_id"))

                logger.info("User joining page", page_id=str(page_id), user_id=str(user_id))

                # Join room for this page
                room = f"page:{page_id}"
                await sio.enter_room(sid, room)

                # Create/update presence
                await self._collaboration_service.join_page(
                    page_id=page_id,
                    user_id=user_id,
                    socket_id=sid,
                )

                # Notify others in the room
                await sio.emit(
                    "user_joined",
                    {
                        "user_id": str(user_id),
                        "page_id": str(page_id),
                    },
                    room=room,
                    skip_sid=sid,
                )

                # Send current presences to the new user
                presences = await self._collaboration_service.get_page_presences(page_id)
                await sio.emit(
                    "presences",
                    {
                        "presences": [
                            {
                                "user_id": str(p.user_id),
                                "cursor_position": p.cursor_position,
                                "selection": p.selection,
                            }
                            for p in presences
                        ]
                    },
                    room=sid,
                )

            except Exception as e:
                logger.error("Error joining page", error=str(e), socket_id=sid)
                await sio.emit("error", {"message": str(e)}, room=sid)

        @sio.event
        async def leave_page(sid: str, data: dict) -> None:
            """Handle leaving a page room.

            Args:
                sid: Socket session ID
                data: Event data with page_id and user_id
            """
            try:
                page_id = UUID(data.get("page_id"))
                user_id = UUID(data.get("user_id"))

                logger.info("User leaving page", page_id=str(page_id), user_id=str(user_id))

                # Leave room
                room = f"page:{page_id}"
                await sio.leave_room(sid, room)

                # Remove presence
                await self._collaboration_service.leave_page(page_id, user_id)

                # Notify others in the room
                await sio.emit(
                    "user_left",
                    {
                        "user_id": str(user_id),
                        "page_id": str(page_id),
                    },
                    room=room,
                    skip_sid=sid,
                )

            except Exception as e:
                logger.error("Error leaving page", error=str(e), socket_id=sid)

        @sio.event
        async def cursor_update(sid: str, data: dict) -> None:
            """Handle cursor position update.

            Args:
                sid: Socket session ID
                data: Event data with page_id, user_id, and cursor_position
            """
            try:
                page_id = UUID(data.get("page_id"))
                user_id = UUID(data.get("user_id"))
                cursor_position = data.get("cursor_position")

                # Update presence
                await self._collaboration_service.update_cursor(
                    page_id=page_id,
                    user_id=user_id,
                    cursor_position=json.dumps(cursor_position) if cursor_position else None,
                )

                # Broadcast to others in the room
                room = f"page:{page_id}"
                await sio.emit(
                    "cursor_updated",
                    {
                        "user_id": str(user_id),
                        "cursor_position": cursor_position,
                    },
                    room=room,
                    skip_sid=sid,
                )

            except Exception as e:
                logger.error("Error updating cursor", error=str(e), socket_id=sid)

        @sio.event
        async def selection_update(sid: str, data: dict) -> None:
            """Handle selection update.

            Args:
                sid: Socket session ID
                data: Event data with page_id, user_id, and selection
            """
            try:
                page_id = UUID(data.get("page_id"))
                user_id = UUID(data.get("user_id"))
                selection = data.get("selection")

                # Update presence
                await self._collaboration_service.update_selection(
                    page_id=page_id,
                    user_id=user_id,
                    selection=json.dumps(selection) if selection else None,
                )

                # Broadcast to others in the room
                room = f"page:{page_id}"
                await sio.emit(
                    "selection_updated",
                    {
                        "user_id": str(user_id),
                        "selection": selection,
                    },
                    room=room,
                    skip_sid=sid,
                )

            except Exception as e:
                logger.error("Error updating selection", error=str(e), socket_id=sid)

        @sio.event
        async def content_update(sid: str, data: dict) -> None:
            """Handle content update (document synchronization).

            Args:
                sid: Socket session ID
                data: Event data with page_id, user_id, and content changes
            """
            try:
                page_id = UUID(data.get("page_id"))
                user_id = UUID(data.get("user_id"))
                changes = data.get("changes")

                logger.info(
                    "Content update received",
                    page_id=str(page_id),
                    user_id=str(user_id),
                    socket_id=sid,
                )

                # Broadcast to others in the room (operational transform would happen here)
                room = f"page:{page_id}"
                await sio.emit(
                    "content_updated",
                    {
                        "user_id": str(user_id),
                        "changes": changes,
                    },
                    room=room,
                    skip_sid=sid,
                )

            except Exception as e:
                logger.error("Error updating content", error=str(e), socket_id=sid)


def create_collaboration_app(
    collaboration_service: CollaborationService,
    page_repository: PageRepository,
    user_repository: UserRepository,
) -> socketio.ASGIApp:
    """Create Socket.IO ASGI app for collaboration.

    Args:
        collaboration_service: Collaboration service
        page_repository: Page repository
        user_repository: User repository

    Returns:
        Socket.IO ASGI app
    """
    CollaborationWebSocketHandler(collaboration_service, page_repository, user_repository)

    # Create ASGI app
    app = socketio.ASGIApp(sio)

    return app
