"""Tools: issue tracking."""

from typing import Optional

from bitmcp.server import mcp, api_get, api_post, api_put, get_workspace


@mcp.tool()
def list_issues(
    repo_slug: str,
    status: Optional[str] = None,
    workspace: Optional[str] = None,
    page: int = 1,
) -> dict:
    """
    List issues dalam repository.

    Args:
        repo_slug: Slug repository
        status: Filter status — new, open, resolved, on hold, invalid, duplicate, wontfix, closed (opsional)
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
        page: Nomor halaman
    """
    ws = get_workspace(workspace)
    params: dict = {"page": page, "pagelen": 20}
    if status:
        params["q"] = f'status="{status}"'
    return api_get(f"/repositories/{ws}/{repo_slug}/issues", params=params)


@mcp.tool()
def get_issue(
    repo_slug: str,
    issue_id: int,
    workspace: Optional[str] = None,
) -> dict:
    """
    Detail sebuah issue.

    Args:
        repo_slug: Slug repository
        issue_id: ID issue
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_get(f"/repositories/{ws}/{repo_slug}/issues/{issue_id}")


@mcp.tool()
def create_issue(
    repo_slug: str,
    title: str,
    content: Optional[str] = None,
    kind: str = "bug",
    priority: str = "major",
    workspace: Optional[str] = None,
) -> dict:
    """
    Buat issue baru.

    Args:
        repo_slug: Slug repository
        title: Judul issue
        content: Deskripsi issue (mendukung Markdown)
        kind: Tipe — bug, enhancement, proposal, task (default: bug)
        priority: Prioritas — trivial, minor, major, critical, blocker (default: major)
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    payload: dict = {"title": title, "kind": kind, "priority": priority}
    if content:
        payload["content"] = {"raw": content}
    return api_post(f"/repositories/{ws}/{repo_slug}/issues", payload)


@mcp.tool()
def update_issue(
    repo_slug: str,
    issue_id: int,
    title: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    content: Optional[str] = None,
    workspace: Optional[str] = None,
) -> dict:
    """
    Update sebuah issue.

    Args:
        repo_slug: Slug repository
        issue_id: ID issue
        title: Judul baru (opsional)
        status: Status baru — new, open, resolved, on hold, invalid, duplicate, wontfix, closed (opsional)
        priority: Prioritas baru (opsional)
        content: Deskripsi baru (opsional)
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    payload: dict = {}
    if title is not None:
        payload["title"] = title
    if status is not None:
        payload["status"] = status
    if priority is not None:
        payload["priority"] = priority
    if content is not None:
        payload["content"] = {"raw": content}
    return api_put(f"/repositories/{ws}/{repo_slug}/issues/{issue_id}", payload)


@mcp.tool()
def list_issue_comments(
    repo_slug: str,
    issue_id: int,
    workspace: Optional[str] = None,
    page: int = 1,
) -> dict:
    """
    List komentar pada sebuah issue.

    Args:
        repo_slug: Slug repository
        issue_id: ID issue
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
        page: Nomor halaman
    """
    ws = get_workspace(workspace)
    return api_get(
        f"/repositories/{ws}/{repo_slug}/issues/{issue_id}/comments",
        params={"page": page, "pagelen": 50},
    )


@mcp.tool()
def add_issue_comment(
    repo_slug: str,
    issue_id: int,
    content: str,
    workspace: Optional[str] = None,
) -> dict:
    """
    Tambahkan komentar pada sebuah issue.

    Args:
        repo_slug: Slug repository
        issue_id: ID issue
        content: Isi komentar (mendukung Markdown)
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_post(
        f"/repositories/{ws}/{repo_slug}/issues/{issue_id}/comments",
        {"content": {"raw": content}},
    )
