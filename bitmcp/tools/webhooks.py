"""Tools: webhook management."""

from typing import Optional

from bitmcp.server import mcp, api_get, api_post, api_delete, get_workspace


@mcp.tool()
def list_webhooks(
    repo_slug: str,
    workspace: Optional[str] = None,
) -> dict:
    """
    List semua webhook pada repository.

    Args:
        repo_slug: Slug repository
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_get(f"/repositories/{ws}/{repo_slug}/hooks")


@mcp.tool()
def create_webhook(
    repo_slug: str,
    url: str,
    description: str,
    events: list,
    active: bool = True,
    workspace: Optional[str] = None,
) -> dict:
    """
    Buat webhook baru pada repository.

    Args:
        repo_slug: Slug repository
        url: URL endpoint yang akan menerima event (harus HTTPS)
        description: Deskripsi webhook
        events: List event yang dimonitor, contoh:
                ['repo:push', 'pullrequest:created', 'pullrequest:fulfilled',
                 'pullrequest:rejected', 'issue:created', 'issue:updated']
        active: Aktifkan webhook (default True)
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_post(
        f"/repositories/{ws}/{repo_slug}/hooks",
        {
            "description": description,
            "url": url,
            "active": active,
            "events": events,
        },
    )


@mcp.tool()
def delete_webhook(
    repo_slug: str,
    webhook_uid: str,
    workspace: Optional[str] = None,
) -> dict:
    """
    Hapus sebuah webhook.

    Args:
        repo_slug: Slug repository
        webhook_uid: UID webhook yang akan dihapus
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_delete(f"/repositories/{ws}/{repo_slug}/hooks/{webhook_uid}")


@mcp.tool()
def list_workspace_webhooks(workspace: Optional[str] = None) -> dict:
    """
    List semua webhook yang terpasang di level workspace.
    Berbeda dari webhook repository, webhook workspace memantau semua event di seluruh repo.

    Args:
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_get(f"/workspaces/{ws}/hooks")
