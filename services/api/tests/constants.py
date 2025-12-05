"""Constants for test URLs and endpoints.

This module provides constants for API endpoints to avoid hardcoding URLs
throughout the test suite. This makes it easier to maintain and update
endpoints if they change.
"""

# Base API path
API_V1_BASE = "/api/v1"

# Auth endpoints
AUTH_LOGIN = f"{API_V1_BASE}/auth/login"
AUTH_REGISTER = f"{API_V1_BASE}/auth/register"
AUTH_REFRESH = f"{API_V1_BASE}/auth/refresh"
AUTH_PASSWORD_RESET_REQUEST = f"{API_V1_BASE}/auth/password/reset-request"
AUTH_PASSWORD_RESET = f"{API_V1_BASE}/auth/password/reset"

# User endpoints
USERS_BASE = f"{API_V1_BASE}/users"
USERS_LIST = f"{USERS_BASE}/"  # Trailing slash required for FastAPI router.get("/")
USERS_ME = f"{USERS_BASE}/me"
USERS_ME_PROFILE = f"{USERS_BASE}/me"
USERS_ME_EMAIL = f"{USERS_BASE}/me/email"
USERS_ME_PASSWORD = f"{USERS_BASE}/me/password"
USERS_ME_AVATAR = f"{USERS_BASE}/me/avatar"
USERS_ME_PREFERENCES = f"{USERS_BASE}/me/preferences"
USERS_ME_DEACTIVATE = f"{USERS_BASE}/me/deactivate"
USERS_REACTIVATE = f"{USERS_BASE}/{{user_id}}/reactivate"

# Organization endpoints
ORGANIZATIONS_BASE = f"{API_V1_BASE}/organizations"
ORGANIZATIONS_LIST = f"{ORGANIZATIONS_BASE}/"
ORGANIZATIONS_DETAIL = f"{ORGANIZATIONS_BASE}/{{organization_id}}"
ORGANIZATIONS_MEMBERS = f"{ORGANIZATIONS_BASE}/{{organization_id}}/members"
ORGANIZATIONS_MEMBER_DETAIL = f"{ORGANIZATIONS_BASE}/{{organization_id}}/members/{{user_id}}"
ORGANIZATIONS_INVITE = f"{ORGANIZATIONS_BASE}/{{organization_id}}/members/invite"
ORGANIZATIONS_INVITATIONS = f"{ORGANIZATIONS_BASE}/{{organization_id}}/invitations"
ORGANIZATIONS_SETTINGS = f"{ORGANIZATIONS_BASE}/{{organization_id}}/settings"
ORGANIZATIONS_INVITATION_ACCEPT = f"{ORGANIZATIONS_BASE}/invitations/{{token}}/accept"
ORGANIZATIONS_INVITATION_CANCEL = f"{ORGANIZATIONS_BASE}/invitations/{{invitation_id}}"
