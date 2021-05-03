# git-kit

Useful utilities for Git

## Commands

<!-- start commands -->
| Command | Description |
| ------- | ----------- |
| `archaeology` | Find a commit most closely resembling a ref. |
| `autofixup` | Attempt to figure out a commit to fix up a single changed file into. |
| `branches` | Interactively select a branch. |
| `del-merged` | Delete merged branches. |
| `go-back` | Go back to a previous ref. |
| `ownership` | Figure out total authorship, line-by-line, of the repository. |
| `point-here` | Set the given branch refs to point to the current HEAD. |
| `reltag` | Create an annotated timestamped release tag. |
| `vtag` | Create a version commit and release tag. |
| `what` | What _is_ the current revision anyway? |
<!-- end commands -->

## Installation

* Create a Python 3 virtualenv
* Activate the virtualenv
* Clone the repo
* `pip install -e .`
* `cd ~/bin; ln -s $VIRTUAL_ENV/bin/git-kit`
* `git kit`
