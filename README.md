# bitmcp

> An in-house MCP server for Bitbucket Cloud — built for teams who want full control,
> full auditability, and zero third-party trust.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Protocol](https://img.shields.io/badge/Protocol-MCP-orange)
![Bitbucket](https://img.shields.io/badge/Bitbucket-Cloud-0052CC?logo=bitbucket)

Connect **GitHub Copilot** or **Claude Desktop** directly to your Bitbucket workspace.
Browse repositories, review pull requests, monitor pipelines, and leave comments —
all from your AI assistant, in the language of your choice.

---

## What makes this different

|  | This server | Generic MCP tools |
|---|---|---|
| **Credential storage** | `~/.config/bitmcp/` at `600` permissions | Varies |
| **Token exposure** | Never logged or returned in output | Not guaranteed |
| **Destructive operations** | None — no delete or destroy tools | Often included |
| **Traffic routing** | Direct to `api.bitbucket.org` | May use proxies |
| **PR comment language** | English, Indonesian, Sundanese, Javanese, Minang | English only |
| **Codebase** | 100% Python, fully auditable by your team | Black box |

---

## Getting started

### 1 — Install

```bash
git clone <repo-url>
cd bitmcp

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -e .
```

### 2 — Get a Bitbucket API token

1. Go to [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click **Create API token**, give it a name such as `"MCP Server"`
3. Copy the generated token — you will not be able to see it again

### 3 — Run first-time setup

Ask your AI assistant to run:

```
setup_bitbucket(
    workspace="your-workspace-slug",
    username="your@email.com",
    api_token="your-token"
)
```

Credentials are written immediately to `~/.config/bitmcp/config.json`
with `600` permissions (owner read/write only).

> **Environment variable override** — useful for CI/CD or shared machines:
> ```bash
> export BITBUCKET_API_TOKEN="..."
> export BITBUCKET_USERNAME="..."
> export BITBUCKET_WORKSPACE="..."   # optional default workspace
> ```
> Environment variables take priority over the config file when both are set.

---

## Connect to your AI assistant

### GitHub Copilot — VS Code

Create or update `.vscode/mcp.json` in your workspace:

```json
{
  "servers": {
    "bitbucket": {
      "type": "stdio",
      "command": "/absolute/path/to/.venv/bin/bitmcp"
    }
  }
}
```

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "bitbucket": {
      "command": "/absolute/path/to/.venv/bin/bitmcp"
    }
  }
}
```

---

## Available tools — 66 total

There are **no destructive operations** in this server.
Nothing can delete a repository, remove a branch, drop a tag, or erase a comment.

<details>
<summary><strong>Configuration (2)</strong></summary>

| Tool | What it does |
|---|---|
| `setup_bitbucket` | Save workspace credentials to local config |
| `get_config_status` | Check which credentials are currently active |

</details>

<details>
<summary><strong>User & Account (3)</strong></summary>

| Tool | What it does |
|---|---|
| `get_current_user` | Get the authenticated user's profile |
| `get_user_profile` | Get a user's public profile by account ID |
| `get_user_permissions` | Check the current user's access level on a repository |

</details>

<details>
<summary><strong>Workspace & Projects (9)</strong></summary>

| Tool | What it does |
|---|---|
| `list_workspaces` | List all accessible workspaces |
| `get_workspace_details` | Get workspace metadata |
| `list_workspace_members` | List all members and their roles |
| `list_workspace_permissions` | List permission levels across the workspace |
| `list_projects` | List projects within a workspace |
| `get_project` | Get project details by project key |
| `create_project` | Create a new project |
| `get_default_reviewers` | Get the default reviewer list for a repository |
| `search_code` | Search code across all repositories in the workspace |

</details>

<details>
<summary><strong>Repositories (6)</strong></summary>

| Tool | What it does |
|---|---|
| `list_repositories` | List repositories in the workspace |
| `get_repository` | Get detailed repository information |
| `create_repository` | Create a new repository |
| `update_repository` | Update repository name, description, or visibility |
| `fork_repository` | Fork a repository |
| `list_repository_forks` | List all forks of a repository |

</details>

<details>
<summary><strong>Branches & Tags (5)</strong></summary>

| Tool | What it does |
|---|---|
| `list_branches` | List all branches |
| `create_branch` | Create a new branch from a source branch |
| `list_tags` | List all tags |
| `create_tag` | Create a new tag pointing to a commit |
| `get_branching_model` | Get the repository's branching model configuration |

</details>

<details>
<summary><strong>Commits & Files (7)</strong></summary>

| Tool | What it does |
|---|---|
| `list_commits` | List commits, optionally filtered by branch |
| `get_commit` | Get details of a specific commit |
| `get_commit_diff` | Get the raw diff for a commit or range |
| `get_commit_diffstat` | Get a summary of changed files for a commit |
| `get_file_contents` | Read a file from any branch or commit |
| `list_commit_statuses` | List CI/CD build statuses attached to a commit |
| `list_commit_comments` | List comments on a commit |

</details>

<details>
<summary><strong>Pull Requests (20)</strong></summary>

Tools marked with ✦ support [multilingual comments](#multilingual-pr-comments).

| Tool | What it does |
|---|---|
| `list_pull_requests` | List PRs, filterable by state (OPEN, MERGED, DECLINED) |
| `get_pull_request` | Get PR details |
| `create_pull_request` | Open a new PR |
| `update_pull_request` | Edit PR title, description, or destination branch |
| `get_pull_request_diff` | Get the raw code diff |
| `get_pull_request_diffstat` | Get a summary of files changed |
| `get_pull_request_commits` | List commits included in the PR |
| `get_pull_request_comments` | Read all comments on a PR |
| `get_pull_request_activity` | View the PR activity timeline |
| `get_pull_request_merge_status` | Check if a PR can be merged (conflict detection) |
| `add_pull_request_comment` ✦ | Add a general comment |
| `add_inline_comment` ✦ | Add an inline comment on a specific line of code |
| `reply_to_comment` ✦ | Reply to an existing comment thread |
| `approve_pull_request` | Approve a PR |
| `unapprove_pull_request` | Remove your approval |
| `request_changes_pull_request` | Request changes on a PR |
| `merge_pull_request` | Merge a PR (merge commit, squash, or fast-forward) |
| `decline_pull_request` | Decline/close a PR |
| `add_reviewer` | Add a reviewer to a PR |
| `remove_reviewer` | Remove a reviewer from a PR |

</details>

<details>
<summary><strong>Pipelines / CI-CD (8)</strong></summary>

| Tool | What it does |
|---|---|
| `list_pipelines` | List pipeline runs |
| `get_pipeline` | Get pipeline run details |
| `trigger_pipeline` | Trigger a new pipeline on a branch |
| `stop_pipeline` | Stop a currently running pipeline |
| `list_pipeline_steps` | List all steps in a pipeline run |
| `get_pipeline_step_log` | Get the log output of a pipeline step |
| `list_pipeline_variables` | List pipeline variables (secret values are masked) |
| `create_pipeline_variable` | Add a new pipeline variable |

</details>

<details>
<summary><strong>Issues (6)</strong></summary>

| Tool | What it does |
|---|---|
| `list_issues` | List issues, filterable by status |
| `get_issue` | Get issue details |
| `create_issue` | Open a new issue |
| `update_issue` | Update issue title, status, or priority |
| `list_issue_comments` | List comments on an issue |
| `add_issue_comment` | Add a comment to an issue |

</details>

---

## Multilingual PR comments

`add_pull_request_comment`, `add_inline_comment`, and `reply_to_comment` each accept
a `language` parameter. The AI assistant writes the comment content in the selected
language, and a language label is automatically appended at the bottom of the comment.

| `language` | Written in |
|---|---|
| `indonesia` | Bahasa Indonesia *(default)* |
| `english` | English |
| `sunda` | Bahasa Sunda |
| `jawa` | Bahasa Jawa |
| `minang` | Bahasa Minang (Minangkabau) |

**Example prompt:**

> *"Leave a comment on PR #42 in backend-api in Bahasa Sunda saying the code looks good"*

The comment posted to Bitbucket will look like this:

```
Kode ieu sae pisan, teu aya masalah nanaon 👍

---
*Bahasa Sunda*
```

---

## Usage examples

```
# First-time setup
setup_bitbucket(workspace="my-company", username="you@company.com", api_token="xxxx")

# Verify who is logged in
get_current_user()

# Explore the workspace
list_workspace_members()
list_repositories()
search_code(query="TODO")

# Open and review a pull request
list_pull_requests(repo_slug="backend-api")
get_pull_request_diff(repo_slug="backend-api", pr_id=42)
get_pull_request_comments(repo_slug="backend-api", pr_id=42)
get_pull_request_merge_status(repo_slug="backend-api", pr_id=42)

# Leave an inline comment in Bahasa Jawa on a specific line
add_inline_comment(
    repo_slug="backend-api",
    pr_id=42,
    content="Iki kudu dikasih error handling, mas",
    file_path="app/services/payment.py",
    line=57,
    language="jawa"
)

# Approve and squash-merge
approve_pull_request(repo_slug="backend-api", pr_id=42)
merge_pull_request(repo_slug="backend-api", pr_id=42, merge_strategy="squash")

# Monitor CI/CD pipelines
list_pipelines(repo_slug="backend-api")
get_pipeline_step_log(
    repo_slug="backend-api",
    pipeline_uuid="{pipeline-uuid}",
    step_uuid="{step-uuid}"
)
```

---

## Security

- **Credential file** is stored at `~/.config/bitmcp/config.json` with `600`
  permissions — readable and writable only by the file owner.
- **API tokens** are never returned in tool output, never written to logs, and never
  echoed back after setup.
- **All traffic** goes directly to `https://api.bitbucket.org/2.0`.
  There are no intermediate proxies or third-party servers involved.
- **No destructive operations** — this server intentionally excludes any tool that
  can delete or permanently modify data (no delete repo, no delete branch, no delete tag).
- **Fully auditable** — the entire codebase is plain Python with no obfuscation.
  Your team can read and verify every line before use.
