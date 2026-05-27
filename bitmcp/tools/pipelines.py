"""Tools: Pipelines / CI-CD."""

from typing import Optional

from bitmcp.server import mcp, api_get, api_post, get_workspace


@mcp.tool()
def list_pipelines(
    repo_slug: str,
    workspace: Optional[str] = None,
    page: int = 1,
) -> dict:
    """
    List pipeline runs dalam repository.

    Args:
        repo_slug: Slug repository
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
        page: Nomor halaman
    """
    ws = get_workspace(workspace)
    return api_get(
        f"/repositories/{ws}/{repo_slug}/pipelines",
        params={"page": page, "pagelen": 10, "sort": "-created_on"},
    )


@mcp.tool()
def get_pipeline(
    repo_slug: str,
    pipeline_uuid: str,
    workspace: Optional[str] = None,
) -> dict:
    """
    Detail sebuah pipeline run.

    Args:
        repo_slug: Slug repository
        pipeline_uuid: UUID pipeline (contoh: '{uuid}')
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_get(f"/repositories/{ws}/{repo_slug}/pipelines/{pipeline_uuid}")


@mcp.tool()
def trigger_pipeline(
    repo_slug: str,
    branch: str = "main",
    workspace: Optional[str] = None,
) -> dict:
    """
    Trigger pipeline baru pada sebuah branch.

    Args:
        repo_slug: Slug repository
        branch: Branch yang akan di-run pipeline-nya (default: 'main')
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_post(
        f"/repositories/{ws}/{repo_slug}/pipelines",
        {"target": {"type": "pipeline_ref_target", "ref_type": "branch", "ref_name": branch}},
    )


@mcp.tool()
def stop_pipeline(
    repo_slug: str,
    pipeline_uuid: str,
    workspace: Optional[str] = None,
) -> dict:
    """
    Stop sebuah pipeline yang sedang berjalan.

    Args:
        repo_slug: Slug repository
        pipeline_uuid: UUID pipeline yang akan dihentikan
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_post(
        f"/repositories/{ws}/{repo_slug}/pipelines/{pipeline_uuid}/stopPipeline"
    )


@mcp.tool()
def list_pipeline_steps(
    repo_slug: str,
    pipeline_uuid: str,
    workspace: Optional[str] = None,
) -> dict:
    """
    List semua step dalam sebuah pipeline run.

    Args:
        repo_slug: Slug repository
        pipeline_uuid: UUID pipeline
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_get(f"/repositories/{ws}/{repo_slug}/pipelines/{pipeline_uuid}/steps")


@mcp.tool()
def get_pipeline_step_log(
    repo_slug: str,
    pipeline_uuid: str,
    step_uuid: str,
    workspace: Optional[str] = None,
) -> str:
    """
    Ambil log output dari sebuah pipeline step.

    Args:
        repo_slug: Slug repository
        pipeline_uuid: UUID pipeline
        step_uuid: UUID step
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    import httpx
    from bitmcp.server import get_auth, BITBUCKET_API

    ws = get_workspace(workspace)
    auth = get_auth()
    url = f"{BITBUCKET_API}/repositories/{ws}/{repo_slug}/pipelines/{pipeline_uuid}/steps/{step_uuid}/log"
    response = httpx.get(url, auth=auth, timeout=60)
    response.raise_for_status()
    return response.text


@mcp.tool()
def list_pipeline_variables(
    repo_slug: str,
    workspace: Optional[str] = None,
) -> dict:
    """
    List pipeline variables (tanpa menampilkan nilai secret).

    Args:
        repo_slug: Slug repository
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_get(f"/repositories/{ws}/{repo_slug}/pipelines_config/variables")


@mcp.tool()
def create_pipeline_variable(
    repo_slug: str,
    key: str,
    value: str,
    secured: bool = False,
    workspace: Optional[str] = None,
) -> dict:
    """
    Buat pipeline variable baru pada repository.

    Args:
        repo_slug: Slug repository
        key: Nama variable (contoh: 'DATABASE_URL', 'API_KEY')
        value: Nilai variable
        secured: Sembunyikan nilai sebagai secret — nilainya tidak bisa dibaca kembali (default False)
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_post(
        f"/repositories/{ws}/{repo_slug}/pipelines_config/variables",
        {"key": key, "value": value, "secured": secured},
    )
