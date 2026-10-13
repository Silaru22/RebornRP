# Reborn Discord bot

Discord administration bot for the Reborn DayZ project. It manages questionnaires, whitelist
entries, and selected server configuration files backed by Teable/PostgreSQL.

The bot does **not** download, update, remove, or restart DayZ or Workshop mods. Mod lifecycle is
owned by the DayZ server administrator.

## Components

- `src/quents`: questionnaire form, review flow, and Discord nickname update;
- `src/server_tools`: explicit whitelist changes;
- `src/economy`: generation of selected TraderPlus and mutant configuration files;
- `src/teable`: Teable HTTP API access;
- `deploy`: local Windows and self-hosted Teable deployment files;
- `scripts`: one-time migration/bootstrap utilities.

## Safety defaults

- Teable URL, PostgreSQL schema, and table IDs come from `.env` instead of being hard-coded.
- Existing server configuration files are backed up before changes.
- JSON files are written atomically.
- Manual mutant files ending in `_hnd.json` are preserved.
- Git push of generated configuration is disabled by default.
- Economy/configuration and whitelist commands are disabled by default; the questionnaire flow
  can run without writing to the DayZ server directory.
- The bot does not request Discord's privileged Message Content intent.
- The configuration generator refuses paths outside `configs_repo_path`.

## Access control

- Administrative slash commands require the Discord role `Тех. администратор`.
- Role matching ignores letter case and whitespace, so `тех.администратор` is also accepted.
- Questionnaire submission remains available to players; questionnaire review buttons retain the
  existing curator, administrator, technical administrator, and event-manager checks.

## Repository ownership

- This checkout has no Git remote connected to the former employee's GitLab or GitHub account.
- The future `origin` must be a new GitHub repository owned by the organization, not a personal
  repository owned by a contractor or employee.
- Repository administrators, recovery methods, deploy keys, access tokens, and CI secrets must all
  remain under organization-controlled accounts.
- Do not restore the legacy `git@gitlab.com:reborn9951441/reborn_bot.git` remote.
- Keep `config_git_push_enabled=false` until the separate DayZ configuration repository is also
  organization-owned and its exact remote has been reviewed.

See `deploy/README.md` for the migration and startup procedure.

## Future improvements

- remind curators when a questionnaire has waited more than 24 hours;
- add questionnaire FAQ and curator editing tools;
- add CI checks for Python, JSON, and XML;
- add scheduled off-machine backup retention.
