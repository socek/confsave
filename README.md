# Configuration Saver

## 1. About

Wrapper on a git client to allow storing your configuration files in git repository. In that way, you will have a log
of your changes and have a backup of you confiugration files.

## 2. Install

Simples way is to use pip:

```
$ pip install confsave
```

Or from source (with root privileges or under virtualenv):

```
$ python setup.py install
```

## 3. How to use

First of all, you need to know, that you should know how to use git. This project is very young so if something will
break, you should be able to fix the problem yourself.
Another nessesery thing is to have some place to store your configuration, for example a shell account on some server.

To use confsave is yo use the `cs` command.

```
usage: cs [-h] [--add ADD] [--list] [--status] [--commit [COMMIT]]
          [--repo SET_REPO]

ConfSave cmd

optional arguments:
  -h, --help            show this help message and exit
  --add ADD, -a ADD     add endpoint
  --list, -l            list untracked files
  --status, -s          show status of tracked files
  --commit [COMMIT], -c [COMMIT]
                        commit changes to the repo
  --repo SET_REPO, -r SET_REPO
                        set remote repo to push to
```

First you should add some file to the repo, for example .xinitrc

```
$ cs -a ~/.xinitrc
```

This will move the .xinitrc file to the ~/.confsave directory and create a local link for it.
Before you are ready to make a commit, you should create a remote git repo on some server. I recommend to use git for
the git:

```
remote $ mkdir config.git
remote $ cd config
remote $ git init --bare
```
After that, you should have a git link looking like this:

```
user@remote.net:config.git
```

Of corse it depends on how you will create your git repo. This is just and example.
After that you should set remote repo for your confsave:

```
cs -r user@remote.net:config.git
```

When your remote repo is set, you can commit your changes. --commit command will commit and push the changes.

```
cs -c
```

Also you can check the status of tracked files by -s, and list of untracked files by -l switch.

## 4. Safety instructions
- Do not add any files with passwords or keys
- Use only SSH or HTTPS transmission protocols.

## 5. FAQ
- Is it safe?
- If you use SSH or HTTPS to send your configuration files it should be safe.

- Should I know git before using this tool?
- Yes, you should. ConfSave is pretty young project so if anything strange happend, you should be able to fix the
    problem by yourself.

## 5. Running tests

$ pytest confsave --cov confsave --cov-report html
