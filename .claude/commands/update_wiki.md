Consolidate the key information from this session into the project wiki.

## Step 1: Identify the Topic

Look at what was discussed or produced in this session — documents worked on, plans implemented, decisions made, analyses completed. Identify the core topic(s) that contain non-trivial, reference-worthy information.

If the topic is ambiguous, ask the user to confirm before proceeding.

Skip trivial updates (typo fixes, minor config changes, routine maintenance). The wiki is a manual, not a journal.

## Step 2: Propose Changes Incrementally

Do NOT write full pages in one shot. Present changes **one paragraph or section at a time**, asking the user to approve or refine each before moving on. Use AskUserQuestion to fine-tune wording, scope, and placement.

For example:
1. Propose the page title, description, and placement (new page vs. update to existing)
2. After confirmation, propose the first section/paragraph
3. Iterate — adjust based on feedback before moving to the next section
4. Continue until all content is drafted

This keeps the user in control and avoids bulk rewrites.

The final content should be:
- **Consolidated**: Distill the session's context into clear, reusable reference material
- **Technical and precise**: Written for a knowledgeable reader, not a narrative of what happened
- **Structured**: Use headings, bullet points, and tables where appropriate
- **Self-contained**: A reader should understand the content without needing session context

Include YAML frontmatter per wiki conventions:
```yaml
---
title: Page Title
description: One-liner summary
tags: []
created: "YYYY-MM-DD"
---
```

## Step 3: Integrate with Existing Wiki

Read the current wiki pages to determine placement:

```bash
ls wiki/*.md
```

Then read relevant existing pages to check for overlap.

Decision logic:
- **If the topic fits within an existing page**: Update that page with the new content (add sections, revise outdated information, expand where needed). Do not duplicate.
- **If the topic overlaps multiple pages**: Break the summary into sections and distribute updates across the relevant pages.
- **If the topic is genuinely new**: Create a new page and add `[[wikilinks]]` from related existing pages.

When updating existing pages, preserve their structure and voice. Add to them — don't rewrite what's already correct.

## Step 4: Handle Tags

Review existing tags: `architecture`, `article`, `report`.

- Use existing tags where they apply
- Only propose a new tag if no combination of existing tags narrows to ≤20 documents AND the new tag would apply to 3+ pages
- Prefer `[[wikilinks]]` over tags for connecting related pages

## Step 5: Update Changelog

Add a brief entry to `wiki/Changelog.md` noting what was updated and why.

## Step 6: Commit

After all wiki files are written, commit and push the wiki submodule:

```bash
git -C wiki add . && git -C wiki commit -m "update: <brief description>" && git -C wiki push
```

Show the user a summary of what was added/changed before pushing.
