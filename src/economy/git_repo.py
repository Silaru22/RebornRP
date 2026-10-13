import os

from git import Repo


class GitRepo:
    def __init__(self, repo_path: str, ssh_key_path: str) -> None:
        """
        :param repo_path: путь до локальной копии репозитория №2
        :param ssh_key_path: путь до SSH-ключа (если используется SSH-доступ)
        """
        self.repo_path = repo_path
        self.ssh_key_path = ssh_key_path

        self.repo = Repo(repo_path)
        if self.repo.is_dirty(untracked_files=True):
            msg = 'Configuration repository has uncommitted changes'
            raise RuntimeError(msg)

        self.env = os.environ.copy()
        if ssh_key_path:
            self.env['GIT_SSH_COMMAND'] = f'ssh -i "{ssh_key_path}" -o IdentitiesOnly=yes'

    def add_changes(self, paths: list[str] | None = None) -> bool:
        """
        Добавляет файлы в индекс (git add).
        """
        if paths:
            self.repo.git.add(*paths)
        else:
            self.repo.git.add(A=True)
        return True

    def commit_changes(self, message: str) -> bool:
        if not self.repo.is_dirty(untracked_files=True):
            return False
        self.repo.index.commit(message)
        return True

    def push_changes(self, remote_name: str = 'origin', branch_name: str = 'main') -> bool:
        remote = self.repo.remote(remote_name)
        branch = branch_name or self.repo.active_branch.name
        remote.push(refspec=f'{branch}:{branch}', env=self.env)
        return True
