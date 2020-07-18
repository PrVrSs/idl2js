import logging
from subprocess import check_call

from git import Git, Repo
from github import Github
from more_itertools.more import first, last

from idl2js.fuzzers.hongg.const import HONGG_DIR, HONGG_REPO


class Hongg:

    repo = HONGG_REPO
    dir = HONGG_DIR

    def __init__(self, nightly: bool = True):
        self._git = Git(str(self.dir))
        self._github = Github().get_repo(self.repo)

        self._init_fuzzer_dir(nightly)

    def _init_fuzzer_dir(self, nightly: bool):
        if self.dir.is_dir():
            if self._git.rev_parse('--is-inside-work-tree'):
                return

            self.dir.rmdir()

        self.clone()

    def clone(self):
        logging.info(f'https://github.com/{self.repo}.git')
        Repo.clone_from(f'https://github.com/{self.repo}.git', str(self.dir))

    @property
    def local_last_commit(self):
        return self._git.log('--pretty=format:"%H"', n=1)

    @property
    def local_last_tag(self):
        return last(self._git.tag().splitlines(), default='')

    @property
    def remote_last_commit(self):
        return first(self._github.get_commits()).sha

    @property
    def remote_last_tag(self):
        return self._github.get_latest_release().tag_name

    def build_fuzzer(self):
        return check_call(['make', '-C', str(self.dir)])

    def compile_extension(self):
        return check_call(['python', 'compile.py', 'build_ext', '--inplace'])


g = Hongg()

print(g.compile_extension())
