# 17 Tool Authorisation

## Goal

Show how tool authorisation middleware controls which tools a user or role can run.

## What changed from Lab 16

Lab 16 focused on input validation (the message).

This lab focuses on authorisation (the tool and the user's role).

## Authorisation checks

```python
class ToolAuthorisationMiddleware:
    def check_tool_allowed(self, tool_name) -> str | None:
        # Blocks admin-only tools for non-admin roles.
        # Blocks tools not in the global authorised_tools list.

    def check_role_permission(self, tool_name) -> str | None:
        # Blocks tools not in the role's permission set.
```

## Authorisation model

Three layers:

1. **authorised_tools**: global allowlist. Every user must have a tool here to run it.
2. **admin_tools**: restricted to `role == "admin"`. Non-admins are blocked.
3. **role_permissions**: per-role allowlist. A tool must be in the role's list.

## Why this matters

Agents with many tools need access control.

Without authorisation middleware:

- Any tool can be invoked regardless of user role.
- Admin operations are exposed.
- You cannot limit tools per user tier.

With authorisation middleware:

- Tool access is gated by user context.
- Admin tools are protected.
- Role-based permissions are enforced at the middleware layer.

## Files in this lab

```txt
src/17_tool_authorisation/
├── README.md
├── main.py
└── expected_output.txt
```

## Run

```bash
uv run python -m src.17_tool_authorisation.main
```

## Expected behaviour

This lab is deterministic and does not call the model.

The important behaviour is:

- Admin tool `delete_all_notes` is blocked for learner role.
- Learner tool `add_note` is allowed.
- Unknown tool `update_config` is blocked.
- Role permission check blocks learner from admin tools.
- Same check allows admin to run admin tools.
- Auth log tracks every decision.

## Learning point

Tool authorisation middleware ensures users can only run tools they are permitted to use. It checks the tool against an authorised list, admin restrictions, and role-based permissions.