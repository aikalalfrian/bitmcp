"""Tools: pull request lifecycle."""

from typing import Literal, Optional

from bitmcp.server import mcp, api_get, api_post, api_put, api_delete, get_workspace

# ---------------------------------------------------------------------------
# Tipe pilihan bahasa untuk komentar pull request
# ---------------------------------------------------------------------------

BahasaKomentar = Literal["english", "indonesia", "sunda", "jawa", "minang"]

_NAMA_BAHASA: dict[str, str] = {
    "english": "English",
    "indonesia": "Bahasa Indonesia",
    "sunda": "Bahasa Sunda",
    "jawa": "Bahasa Jawa",
    "minang": "Bahasa Minang (Minangkabau)",
}


@mcp.tool()
def list_pull_requests(
    repo_slug: str,
    state: str = "OPEN",
    workspace: Optional[str] = None,
    page: int = 1,
) -> dict:
    """
    List pull request dalam repository.

    Args:
        repo_slug: Slug repository
        state: Status PR — OPEN, MERGED, DECLINED, SUPERSEDED (default: OPEN)
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
        page: Nomor halaman
    """
    ws = get_workspace(workspace)
    return api_get(
        f"/repositories/{ws}/{repo_slug}/pullrequests",
        params={"state": state, "page": page, "pagelen": 20},
    )


@mcp.tool()
def get_pull_request(
    repo_slug: str,
    pr_id: int,
    workspace: Optional[str] = None,
) -> dict:
    """
    Detail sebuah pull request.

    Args:
        repo_slug: Slug repository
        pr_id: ID pull request
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_get(f"/repositories/{ws}/{repo_slug}/pullrequests/{pr_id}")


@mcp.tool()
def create_pull_request(
    repo_slug: str,
    title: str,
    source_branch: str,
    destination_branch: str = "main",
    description: Optional[str] = None,
    close_source_branch: bool = False,
    reviewers: Optional[list] = None,
    workspace: Optional[str] = None,
) -> dict:
    """
    Buat pull request baru.

    Args:
        repo_slug: Slug repository
        title: Judul pull request
        source_branch: Branch asal (contoh: 'feature/login')
        destination_branch: Branch tujuan (default: 'main')
        description: Deskripsi PR (mendukung Markdown)
        close_source_branch: Hapus source branch setelah merge (default False)
        reviewers: List account_id reviewer (opsional), contoh: ['uuid1', 'uuid2']
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    payload: dict = {
        "title": title,
        "source": {"branch": {"name": source_branch}},
        "destination": {"branch": {"name": destination_branch}},
        "close_source_branch": close_source_branch,
    }
    if description:
        payload["description"] = description
    if reviewers:
        payload["reviewers"] = [{"account_id": r} for r in reviewers]
    return api_post(f"/repositories/{ws}/{repo_slug}/pullrequests", payload)


@mcp.tool()
def update_pull_request(
    repo_slug: str,
    pr_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    destination_branch: Optional[str] = None,
    workspace: Optional[str] = None,
) -> dict:
    """
    Update judul, deskripsi, atau destination branch sebuah PR.

    Args:
        repo_slug: Slug repository
        pr_id: ID pull request
        title: Judul baru (opsional)
        description: Deskripsi baru (opsional)
        destination_branch: Branch tujuan baru (opsional)
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    payload: dict = {}
    if title is not None:
        payload["title"] = title
    if description is not None:
        payload["description"] = description
    if destination_branch is not None:
        payload["destination"] = {"branch": {"name": destination_branch}}
    return api_put(f"/repositories/{ws}/{repo_slug}/pullrequests/{pr_id}", payload)


@mcp.tool()
def approve_pull_request(
    repo_slug: str,
    pr_id: int,
    workspace: Optional[str] = None,
) -> dict:
    """
    Approve sebuah pull request.

    Args:
        repo_slug: Slug repository
        pr_id: ID pull request
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_post(f"/repositories/{ws}/{repo_slug}/pullrequests/{pr_id}/approve")


@mcp.tool()
def unapprove_pull_request(
    repo_slug: str,
    pr_id: int,
    workspace: Optional[str] = None,
) -> dict:
    """
    Batalkan approval sebuah pull request.

    Args:
        repo_slug: Slug repository
        pr_id: ID pull request
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_delete(f"/repositories/{ws}/{repo_slug}/pullrequests/{pr_id}/approve")


@mcp.tool()
def request_changes_pull_request(
    repo_slug: str,
    pr_id: int,
    workspace: Optional[str] = None,
) -> dict:
    """
    Tandai PR memerlukan perubahan (request changes).

    Args:
        repo_slug: Slug repository
        pr_id: ID pull request
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_post(
        f"/repositories/{ws}/{repo_slug}/pullrequests/{pr_id}/request-changes"
    )


@mcp.tool()
def merge_pull_request(
    repo_slug: str,
    pr_id: int,
    merge_strategy: str = "merge_commit",
    message: Optional[str] = None,
    close_source_branch: bool = True,
    workspace: Optional[str] = None,
) -> dict:
    """
    Merge sebuah pull request.

    Args:
        repo_slug: Slug repository
        pr_id: ID pull request
        merge_strategy: Strategi merge — merge_commit, squash, fast_forward (default: merge_commit)
        message: Pesan commit merge opsional
        close_source_branch: Hapus source branch setelah merge (default True)
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    payload: dict = {
        "type": "pullrequest",
        "merge_strategy": merge_strategy,
        "close_source_branch": close_source_branch,
    }
    if message:
        payload["message"] = message
    return api_post(f"/repositories/{ws}/{repo_slug}/pullrequests/{pr_id}/merge", payload)


@mcp.tool()
def decline_pull_request(
    repo_slug: str,
    pr_id: int,
    workspace: Optional[str] = None,
) -> dict:
    """
    Tolak (decline) sebuah pull request.

    Args:
        repo_slug: Slug repository
        pr_id: ID pull request
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_post(f"/repositories/{ws}/{repo_slug}/pullrequests/{pr_id}/decline")


@mcp.tool()
def add_pull_request_comment(
    repo_slug: str,
    pr_id: int,
    content: str,
    language: BahasaKomentar = "indonesia",
    workspace: Optional[str] = None,
) -> dict:
    """
    Tambahkan komentar ke pull request.

    PENTING — Pilihan bahasa:
      Tulis isi `content` sepenuhnya dalam bahasa yang dipilih di parameter `language`:
      - "english"   → tulis dalam English
      - "indonesia" → tulis dalam Bahasa Indonesia (default)
      - "sunda"     → tulis dalam Bahasa Sunda
      - "jawa"      → tulis dalam Bahasa Jawa (Ngoko atau Krama sesuai konteks)
      - "minang"    → tulis dalam Bahasa Minang (Minangkabau)

    Args:
        repo_slug: Slug repository
        pr_id: ID pull request
        content: Isi komentar dalam bahasa yang dipilih (mendukung Markdown)
        language: Pilihan bahasa komentar (default: indonesia)
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    lang_label = _NAMA_BAHASA.get(language, language)
    tagged_content = f"{content}\n\n---\n*{lang_label}*"
    return api_post(
        f"/repositories/{ws}/{repo_slug}/pullrequests/{pr_id}/comments",
        {"content": {"raw": tagged_content}},
    )


@mcp.tool()
def get_pull_request_comments(
    repo_slug: str,
    pr_id: int,
    workspace: Optional[str] = None,
    page: int = 1,
) -> dict:
    """
    Ambil semua komentar di sebuah pull request.

    Args:
        repo_slug: Slug repository
        pr_id: ID pull request
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
        page: Nomor halaman
    """
    ws = get_workspace(workspace)
    return api_get(
        f"/repositories/{ws}/{repo_slug}/pullrequests/{pr_id}/comments",
        params={"page": page, "pagelen": 50},
    )


@mcp.tool()
def get_pull_request_diff(
    repo_slug: str,
    pr_id: int,
    workspace: Optional[str] = None,
) -> str:
    """
    Tampilkan raw diff sebuah pull request.

    Args:
        repo_slug: Slug repository
        pr_id: ID pull request
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    import httpx
    from bitmcp.server import get_auth, BITBUCKET_API

    ws = get_workspace(workspace)
    auth = get_auth()
    url = f"{BITBUCKET_API}/repositories/{ws}/{repo_slug}/pullrequests/{pr_id}/diff"
    response = httpx.get(url, auth=auth, timeout=30)
    response.raise_for_status()
    return response.text


@mcp.tool()
def get_pull_request_merge_status(
    repo_slug: str,
    pr_id: int,
    workspace: Optional[str] = None,
) -> dict:
    """
    Cek apakah sebuah PR bisa di-merge (conflict check).

    Args:
        repo_slug: Slug repository
        pr_id: ID pull request
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_get(f"/repositories/{ws}/{repo_slug}/pullrequests/{pr_id}/mergecheck")


@mcp.tool()
def get_pull_request_activity(
    repo_slug: str,
    pr_id: int,
    workspace: Optional[str] = None,
    page: int = 1,
) -> dict:
    """
    Tampilkan timeline aktivitas sebuah pull request.

    Args:
        repo_slug: Slug repository
        pr_id: ID pull request
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
        page: Nomor halaman
    """
    ws = get_workspace(workspace)
    return api_get(
        f"/repositories/{ws}/{repo_slug}/pullrequests/{pr_id}/activity",
        params={"page": page, "pagelen": 50},
    )


@mcp.tool()
def get_pull_request_commits(
    repo_slug: str,
    pr_id: int,
    workspace: Optional[str] = None,
    page: int = 1,
) -> dict:
    """
    List semua commit yang termasuk dalam sebuah pull request.

    Args:
        repo_slug: Slug repository
        pr_id: ID pull request
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
        page: Nomor halaman
    """
    ws = get_workspace(workspace)
    return api_get(
        f"/repositories/{ws}/{repo_slug}/pullrequests/{pr_id}/commits",
        params={"page": page, "pagelen": 30},
    )


@mcp.tool()
def get_pull_request_diffstat(
    repo_slug: str,
    pr_id: int,
    workspace: Optional[str] = None,
) -> dict:
    """
    Tampilkan ringkasan file yang berubah di sebuah pull request (diffstat).
    Lebih cepat dari get_pull_request_diff karena hanya menampilkan nama file.

    Args:
        repo_slug: Slug repository
        pr_id: ID pull request
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_get(f"/repositories/{ws}/{repo_slug}/pullrequests/{pr_id}/diffstat")


@mcp.tool()
def add_inline_comment(
    repo_slug: str,
    pr_id: int,
    content: str,
    file_path: str,
    line: int,
    language: BahasaKomentar = "indonesia",
    workspace: Optional[str] = None,
) -> dict:
    """
    Tambahkan komentar inline langsung pada baris kode di sebuah pull request.

    PENTING — Pilihan bahasa:
      Tulis isi `content` sepenuhnya dalam bahasa yang dipilih di parameter `language`:
      - "english"   → tulis dalam English
      - "indonesia" → tulis dalam Bahasa Indonesia (default)
      - "sunda"     → tulis dalam Bahasa Sunda
      - "jawa"      → tulis dalam Bahasa Jawa (Ngoko atau Krama sesuai konteks)
      - "minang"    → tulis dalam Bahasa Minang (Minangkabau)

    Args:
        repo_slug: Slug repository
        pr_id: ID pull request
        content: Isi komentar dalam bahasa yang dipilih (mendukung Markdown)
        file_path: Path file yang dikomentari (contoh: 'app/models/user.rb')
        line: Nomor baris yang dikomentari
        language: Pilihan bahasa komentar (default: indonesia)
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    lang_label = _NAMA_BAHASA.get(language, language)
    tagged_content = f"{content}\n\n---\n*{lang_label}*"
    return api_post(
        f"/repositories/{ws}/{repo_slug}/pullrequests/{pr_id}/comments",
        {
            "content": {"raw": tagged_content},
            "inline": {"path": file_path, "to": line},
        },
    )


@mcp.tool()
def reply_to_comment(
    repo_slug: str,
    pr_id: int,
    parent_comment_id: int,
    content: str,
    language: BahasaKomentar = "indonesia",
    workspace: Optional[str] = None,
) -> dict:
    """
    Balas sebuah komentar di pull request (threaded reply).

    PENTING — Pilihan bahasa:
      Tulis isi `content` sepenuhnya dalam bahasa yang dipilih di parameter `language`:
      - "english"   → tulis dalam English
      - "indonesia" → tulis dalam Bahasa Indonesia (default)
      - "sunda"     → tulis dalam Bahasa Sunda
      - "jawa"      → tulis dalam Bahasa Jawa (Ngoko atau Krama sesuai konteks)
      - "minang"    → tulis dalam Bahasa Minang (Minangkabau)

    Args:
        repo_slug: Slug repository
        pr_id: ID pull request
        parent_comment_id: ID komentar yang akan dibalas
        content: Isi balasan dalam bahasa yang dipilih (mendukung Markdown)
        language: Pilihan bahasa balasan (default: indonesia)
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    lang_label = _NAMA_BAHASA.get(language, language)
    tagged_content = f"{content}\n\n---\n*{lang_label}*"
    return api_post(
        f"/repositories/{ws}/{repo_slug}/pullrequests/{pr_id}/comments",
        {
            "content": {"raw": tagged_content},
            "parent": {"id": parent_comment_id},
        },
    )


@mcp.tool()
def add_reviewer(
    repo_slug: str,
    pr_id: int,
    reviewer_account_id: str,
    workspace: Optional[str] = None,
) -> dict:
    """
    Tambahkan reviewer ke sebuah pull request.
    Menggunakan mekanisme update PR dengan menambahkan reviewer baru ke daftar yang ada.

    Args:
        repo_slug: Slug repository
        pr_id: ID pull request
        reviewer_account_id: Account ID (UUID) reviewer yang akan ditambahkan
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    # Ambil PR saat ini untuk mendapatkan daftar reviewer existing
    current_pr = api_get(f"/repositories/{ws}/{repo_slug}/pullrequests/{pr_id}")
    existing = [r["account_id"] for r in current_pr.get("reviewers", []) if "account_id" in r]
    if reviewer_account_id not in existing:
        existing.append(reviewer_account_id)
    return api_put(
        f"/repositories/{ws}/{repo_slug}/pullrequests/{pr_id}",
        {"reviewers": [{"account_id": rid} for rid in existing]},
    )


@mcp.tool()
def remove_reviewer(
    repo_slug: str,
    pr_id: int,
    reviewer_account_id: str,
    workspace: Optional[str] = None,
) -> dict:
    """
    Hapus reviewer dari sebuah pull request.

    Args:
        repo_slug: Slug repository
        pr_id: ID pull request
        reviewer_account_id: Account ID (UUID) reviewer yang akan dihapus
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    current_pr = api_get(f"/repositories/{ws}/{repo_slug}/pullrequests/{pr_id}")
    remaining = [
        r["account_id"]
        for r in current_pr.get("reviewers", [])
        if r.get("account_id") != reviewer_account_id
    ]
    return api_put(
        f"/repositories/{ws}/{repo_slug}/pullrequests/{pr_id}",
        {"reviewers": [{"account_id": rid} for rid in remaining]},
    )
