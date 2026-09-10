---
name: linear
description: Manage issues, projects & team workflows in Linear. Use when the user wants to read, create or updates tickets in Linear.
metadata:
  short-description: Manage Linear issues in Codex
---

# Linear

## Overview

This skill provides a structured workflow for managing issues, projects &
team workflows in Linear. Default to the Linear MCP server for normal read and
write operations. If the user explicitly asks to run the `linear-import` CLI,
or the task is the PRD-kickoff CSV import step, use the CLI workflow below
instead of pausing for MCP setup.

## Prerequisites
- For MCP workflows: Linear MCP server must be connected and accessible via
  OAuth.
- For CLI import workflows: the repo must contain the CSV to import and a
  `LINEAR_API_KEY` value in `.env`.
- Confirm access to the relevant Linear workspace, teams, and projects.

## New Issue Assignment Invariant

Every newly created Linear issue must have an assignee. Assign it to Javier by
default. Use another assignee only when Javier explicitly names that person for
the new issue.

Resolve Javier's exact Linear member record before creation. If it cannot be
resolved unambiguously, stop and ask instead of creating an unassigned issue.
After creation, re-fetch the issue and verify the assignee. Do not change the
assignee of an existing issue unless Javier explicitly requests that update.

## New Issue Label Invariant

Every newly created Linear issue must have at least one label. Use the smallest
relevant set of labels already available in the destination project. Create and
apply a missing label only after Javier explicitly approves that label.

Resolve the destination project's available labels before creation. If no
existing approved label applies and Javier has not approved a new label, stop
and ask instead of creating an unlabeled issue. After creation, re-fetch the
issue and verify its labels. Do not change labels on an existing issue unless
Javier explicitly requests that update.

## Required Workflow

**Follow these steps in order. Do not skip steps.**

### Step 0: Choose MCP vs CLI import

- If the user explicitly asks for `linear-import`, or the request is the
  post-approval PRD kickoff CSV import, use the CLI import flow in Step 0A.
- Otherwise, use the MCP path in Step 0B.

### Step 0A: CLI import flow for PRD kickoff or explicit CSV import

1. Confirm the CSV has already been generated and stop until the user gives
   explicit approval to create Linear issues.
2. Run `linear-import` only after that approval.
3. Read `LINEAR_API_KEY` from the repo `.env` file and use that key rather
   than any other Linear-related env var.
4. Select:
   - `Linear (CSV export)` as the service,
   - the user-approved CSV file (for PRD kickoff, `docs/prd/linear_issues.csv`),
   - the user-approved existing team/project,
   - self-assignment to Javier unless he explicitly requested another assignee,
   - at least one existing destination-project label for every imported issue,
     or a new label Javier explicitly approved before import.
5. If sandbox networking blocks the CLI, rerun it with the required network
   approval.
6. If the CLI does not print created issue IDs, query Linear afterward to map
   imported titles to their new issue identifiers before continuing PRD sync.

### Step 0B: Set up Linear MCP (if not already configured)

If any MCP call fails because Linear MCP is not connected, pause and set it up:

1. Add the Linear MCP:
   - `codex mcp add linear --url https://mcp.linear.app/mcp`
2. Enable remote MCP client:
   - Set `[features] rmcp_client = true` in `config.toml` **or** run `codex --enable rmcp_client`
3. Log in with OAuth:
   - `codex mcp login linear`

After successful login, the user will have to restart codex. You should finish
your answer and tell them so when they try again they can continue with Step 1.

**Windows/WSL note:** If you see connection errors on Windows, try configuring the Linear MCP to run via WSL:
```json
{"mcpServers": {"linear": {"command": "wsl", "args": ["npx", "-y", "mcp-remote", "https://mcp.linear.app/sse", "--transport", "sse-only"]}}}
```

### Step 1
Clarify the user's goal and scope (e.g., issue triage, sprint planning, documentation audit, workload balance). Confirm team/project, priority, cycle, and due dates as needed. For new issues, use Javier as assignee without asking again unless he requested someone else, and select at least one existing destination-project label. Ask only when no valid label applies or a new label needs approval.

### Step 2
Select the appropriate workflow (see Practical Workflows below) and identify the Linear MCP tools you will need. Confirm required identifiers (issue ID, project ID, team key) before calling tools.

### Step 3
Execute Linear MCP tool calls in logical batches:
- Read first (list/get/search) to build context.
- Create or update next (issues, projects, labels, comments) with all required fields.
- Include the resolved assignee in every new issue creation and re-fetch each
  created issue to verify it is not unassigned.
- Include at least one existing or explicitly approved destination-project label
  in every new issue creation and re-fetch each issue to verify it is not
  unlabeled.
- For bulk operations, explain the grouping logic before applying changes.

### Step 4
Summarize results, call out remaining gaps or blockers, and propose next actions (additional issues, label changes, assignments, or follow-up comments).

## Available Tools

Issue Management: `list_issues`, `get_issue`, `create_issue`, `update_issue`, `list_my_issues`, `list_issue_statuses`, `list_issue_labels`, `create_issue_label`

Project & Team: `list_projects`, `get_project`, `create_project`, `update_project`, `list_teams`, `get_team`, `list_users`

Documentation & Collaboration: `list_documents`, `get_document`, `search_documentation`, `list_comments`, `create_comment`, `list_cycles`

## Practical Workflows

- Sprint Planning: Review open issues for a target team, pick top items by priority, and create a new cycle (e.g., "Q1 Performance Sprint") with assignments.
- Bug Triage: List critical/high-priority bugs, rank by user impact, and move the top items to "In Progress."
- Documentation Audit: Search documentation (e.g., API auth), then open labeled "documentation" issues for gaps or outdated sections with detailed fixes.
- Team Workload Balance: Group active issues by assignee, flag anyone with high load, and suggest or apply redistributions.
- Release Planning: Create a project (e.g., "v2.0 Release") with milestones (feature freeze, beta, docs, launch) and generate issues with estimates.
- Cross-Project Dependencies: Find all "blocked" issues, identify blockers, and create linked issues if missing.
- Automated Status Updates: Find your issues with stale updates and add status comments based on current state/blockers.
- Smart Labeling: Analyze unlabeled issues and suggest or apply existing labels. Create a missing label only after Javier explicitly approves it.
- Sprint Retrospectives: Generate a report for the last completed cycle, note completed vs. pushed work, and open discussion issues for patterns.

## Tips for Maximum Productivity

- Batch operations for related changes; consider smart templates for recurring issue structures.
- Use natural queries when possible ("Show me what John is working on this week").
- Leverage context: reference prior issues in new requests.
- Break large updates into smaller batches to avoid rate limits; cache or reuse filters when listing frequently.

## Troubleshooting

- Authentication: Clear browser cookies, re-run OAuth, verify workspace permissions, ensure API access is enabled.
- Tool Calling Errors: Confirm the model supports multiple tool calls, provide all required fields, and split complex requests.
- Missing Data: Refresh token, verify workspace access, check for archived projects, and confirm correct team selection.
- Performance: Remember Linear API rate limits; batch bulk operations, use specific filters, or cache frequent queries.
