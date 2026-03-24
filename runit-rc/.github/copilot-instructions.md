# Copilot Instructions for `runit-rc`

## Build, test, and lint commands

- Build the only compiled artifact (`pause`): `make`
- Clean build output: `make clean`
- Validate the install layout without touching the host root: `tmpdir=$(mktemp -d) && make SHELL=/bin/bash install DESTDIR="$tmpdir" && rm -rf "$tmpdir"`
- Install for real: `sudo make SHELL=/bin/bash install`
- There is no automated test suite in this repository today.
- There is no lint target or linter config checked into this repository today.
- There is no single-test command because the repository does not define per-test execution.

## High-level architecture

- This repository packages the stage scripts and helper binaries used by Venom Linux's runit-based boot flow. `make install` places scripts under `/etc/runit`, helper binaries under `/sbin`, service templates under `/etc/sv`, and symlinks `/var/service` to the active `runsvdir`.
- `1` is the stage-1 entrypoint. It runs `/etc/runit/rc.startup`, creates `/run/runit`, and initializes the `/etc/runit/stopit` sentinel file.
- `rc.startup` handles early boot work: mounting virtual filesystems, loading kernel modules via `modules-load`, starting udev, activating LVM and swap when available, running `fsck`, remounting `/` read-write, mounting the remaining filesystems, and applying host configuration from `/etc/runit/runit.conf` plus `/etc/lsb-release` when present.
- `2` is the long-running supervision stage. It selects a runlevel by scanning kernel command-line arguments for a directory name under `/etc/runit/runsvdir/`, defaults to `default`, runs `/etc/runit/rc.startup.local` if present, then `exec`s `runsvdir -P /var/service`.
- Service definitions live in `services/` and are copied into `/etc/sv` during install. The install target wires `/etc/runit/runsvdir/default` to `getty-tty1` and `/etc/runit/runsvdir/single` to `sulogin`.
- `3` is the shutdown stage. It optionally marks reboot intent from `/run/runit.reboot`, force-stops supervised services, exits them, and then runs `/etc/runit/rc.shutdown`.
- `rc.shutdown` performs the final teardown: local shutdown hook, random-seed save, optional RTC sync, udev stop, TERM/KILL sweep, swapoff, unmounts, remounting `/` read-only, and final `sync`.
- `halt`, `shutdown`, and `ctrlaltdel` are thin control frontends. They coordinate stage changes by touching sentinel files such as `/run/runit.reboot`, `/etc/runit/reboot`, `/etc/runit/stopit`, `/fastboot`, `/forcefsck`, and `/etc/nologin`.

## Key conventions

- Keep runtime scripts POSIX-`/bin/sh` compatible. The installed boot-stage scripts are executed directly by init and use absolute installed paths like `/etc/runit/...`, `/etc/sv/...`, `/var/service`, and `/sbin/runit-init`.
- Prefer putting machine- or site-specific behavior in `rc.startup.local`, `rc.shutdown.local`, or `runit.conf` instead of editing the core startup/shutdown flow.
- `runit.conf` is a sourced shell config, not a custom parser format. Preserve simple shell variable assignments for settings like `HARDWARECLOCK`, `TIMEZONE`, `KEYMAP`, and `FONT`.
- Runlevels are directory-driven. To add a new runlevel, add a directory under `/etc/runit/runsvdir`; stage `2` discovers it from kernel command-line tokens rather than from a separate registry.
- Getty service templates use paired `run` and `finish` scripts. If you add another tty service, also add the matching `finish` script that updates utmp with `utmpset -w`.
- `services/sulogin/run` optionally sources a local `conf` file from the service directory and derives the active console from `/sys/class/tty/console/active`; preserve that pattern if you change the single-user service.
- The current `Makefile` `install` target assumes brace expansion in `chmod $(ISVDIR)/*/{run,finish}`. In practice, use `make SHELL=/bin/bash install` when validating or installing from the repository.
