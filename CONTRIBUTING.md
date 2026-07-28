# Contributing

Thanks for your interest in improving RiverWare-AI-Tools. Issues and pull
requests are welcome.

## Adding or changing a skill

Skills live in `skills/`, one folder per skill:

```
skills/<skill-name>/
  SKILL.md          The skill definition (required)
  <helper>.py       Parser / generator scripts the skill runs
```

### SKILL.md checklist

- [ ] Frontmatter `name` matches the folder name.
- [ ] Frontmatter `description` is written as **trigger conditions** —
      what the skill does *and* when an agent should use it
      ("Use when asked to ...").
- [ ] Body under ~500 lines; heavy lifting delegated to bundled scripts.
- [ ] No absolute paths, no machine- or user-specific references —
      everything relative to the repository root.
- [ ] Never instructs reading a `.mdl` file raw (they exceed context
      limits); all file access goes through a parser script.
- [ ] Scripts print ASCII-safe output and run on Windows/macOS/Linux
      with Python 3.10+.
- [ ] A **Worked example** section points at a committed output in
      `examples/` showing the target shape and depth.

### Worked examples

Every skill ships with at least one committed output in `examples/`
produced with the skill and polished into finished documentation. If you
change what a skill produces, regenerate and re-polish its example.

### Clone-user bridge

If you add a skill, also add a thin bridge at
`.claude/skills/<skill-name>/SKILL.md` (copy the frontmatter, body is one
pointer line to `skills/<skill-name>/SKILL.md`) so users who clone the
repo get the skill without installing the plugin.

## Commit style

Conventional Commits: `type(scope): imperative subject` with types
`feat` `fix` `docs` `style` `refactor` `perf` `test` `chore` `ci` `build`.
