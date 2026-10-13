# Reborn local deployment

The deployment deliberately separates responsibilities:

- DayZ and Workshop mods remain under the server administrator's control.
- The Discord bot may update only the explicitly configured whitelist and server configuration files.
- Teable, PostgreSQL, and Redis run in a resource-limited WSL2 Ubuntu environment.
- Nothing in this repository downloads, updates, or restarts DayZ mods.

## Ownership boundary

The replacement environment must not depend on accounts or infrastructure controlled by the former
employee. The organization must own and be able to recover:

- the GitHub organization and both repositories (bot source and, if used, DayZ configurations);
- the Discord application and bot token;
- the Teable administrator account, database, backups, domain, and DNS;
- all SSH/deploy keys, access tokens, CI secrets, and recovery email addresses.

Do not add a Git remote until its URL and organization ownership have been verified. Never reuse the
legacy GitLab remote, old deploy keys, or old personal access tokens.

## Resource limits

For the current eight-core host, limit WSL2 to:

- 2 virtual CPUs;
- 6 GB RAM;
- a virtual disk stored on the non-DayZ NVMe drive.

Run `deploy/windows/enable-wsl.ps1` from an elevated PowerShell session, restart Windows, and only
then install Ubuntu. The feature script never restarts Windows itself. Store the distribution on a
non-system drive and apply the CPU and RAM limits before starting Teable.

Do not expose PostgreSQL or Redis to the LAN or Internet. Only publish the Teable HTTP port during
the initial migration. Add HTTPS before allowing access from outside the local network.

## Teable bootstrap

1. Install Ubuntu under WSL2 on a non-system NVMe drive.
2. Install Docker Engine and the Compose plugin inside Ubuntu.
3. Copy `deploy/teable` to the VM.
4. Copy `.env.example` to `.env` and replace every placeholder secret and `PUBLIC_ORIGIN`.
5. Start with `docker compose up -d`.
6. Create the first administrator in Teable.
7. Import `Reborn Base.tea` from the Teable UI.
8. Verify all six tables, 6,277 records, formulas, links, and views.
9. Run `scripts/create_questionnaire_table.py` with the imported base ID and a fresh API token.
10. Put the returned `teable_users_table_id` into the bot `.env`.
11. Run `backup.sh` before upgrading Teable or changing the imported schema.

The exported base does not contain the questionnaire table expected by the bot. Create or migrate
that table before enabling the questionnaire commands.

## Bot bootstrap

1. Create a new Discord application owned by the organization.
2. Create a fresh `.env` from the repository `.env.example`.
3. Configure the new Discord token, guild ID, local Teable URL/token, imported schema ID, table IDs,
   DayZ config path, backup path, and whitelist path.
4. Keep `config_git_push_enabled=false` until backups are tested and the configuration repository is
   owned by the organization with fresh credentials.
5. Recreate `.venv`, install dependencies, and run `deploy/windows/run-bot.ps1` manually.
6. Test every Discord command in a test guild.
7. Only then run `deploy/windows/install-bot-task.ps1` from an elevated PowerShell session.
