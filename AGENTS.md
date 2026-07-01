> For Mintlify product knowledge (components, configuration, writing standards),
> install the Mintlify skill: `npx skills add https://mintlify.com/docs`

# Documentation project instructions

## About this project

- This is the documentation site for **Railmail**, an email marketing platform, built on [Mintlify](https://mintlify.com)
- Pages are MDX files with YAML frontmatter
- Configuration lives in `docs.json`
- The **API Reference** is generated automatically from the OpenAPI spec at `api-reference/openapi.json`, which is a copy of the backend's `docs/openapi/public-v1.json`. When the backend spec changes, re-copy it — do not hand-edit endpoint pages.
- Overview pages under `api-reference/` (`introduction`, `authentication`, `errors`, `rate-limits`) are hand-written and should stay in sync with the spec's `info.description`.
- Validate changes locally with `mint validate`, `mint openapi-check api-reference/openapi.json`, and `mint broken-links`.
- Use the Mintlify MCP server, `https://mcp.mintlify.com`, to edit content and settings via MCP
- Use the Mintlify docs MCP server, `https://www.mintlify.com/docs/mcp`, to query information about using Mintlify via MCP

## Terminology

- Use "project" — an API key is scoped to exactly one project.
- Use "subscriber" for an end user on a mailing list, "topic" for a subscription list, "consent" for per-topic opt-in.
- Use "API key" (format `rm_(live|test)_...`), and "scope" for the permissions a key carries.

## Style preferences

{/* Add any project-specific style rules below */}

- Use active voice and second person ("you")
- Keep sentences concise — one idea per sentence
- Use sentence case for headings
- Bold for UI elements: Click **Settings**
- Code formatting for file names, commands, paths, and code references

## Content boundaries

{/* Define what should and shouldn't be documented */}
{/* Example: Don't document internal admin features */}
