MAX_RUN_TIME = 30 # seconds
MAX_STREAM_LINES = 7
STREAM_REFRESH_IMTERVAL = 5 # seconds

HOST_MOUNT_DIR = '/tmp/shared'
DIND_MOUNT_DIR = '/bot/mount'
PERSISTENT_MOUNT_DIR = '/persistent'
PERSISTENT_VOLUME_PREFIX = 'globibot-dind-user-persistent'

USER_STORAGE_VOLUME_NAME = lambda key: f'{PERSISTENT_VOLUME_PREFIX}_{key}'

CONTAINER_LOG_OPTS = dict(
    stream = True,
    follow = True,
    stdout = True,
    stderr = True
)

CONTAINER_OPTS = lambda mount_dir, user_volume_name: dict(
    detach              = True,
    working_dir         = '/app',
    volumes             = {
        mount_dir:        { 'bind': mount_dir,            'mode': 'ro' },
        user_volume_name: { 'bind': PERSISTENT_MOUNT_DIR, 'mode': 'rw' },
    },
    tmpfs               = { '/tmp': 'size=256M,exec,mode=777' },
    # throttle
    pids_limit          = 64,
    mem_limit           = '256m',
    mem_swappiness      = 0,
    cpu_count           = 1,
    cpuset_cpus         = '0',
    # network_disabled    = True,
    storage_opt         = { 'size': '10G' },
    # Doesn't work 4Head
    device_write_bps    = [{ 'Path': '/dev/sda', 'Rate': 4096 * 1000 }],
    device_read_bps     = [{ 'Path': '/dev/sda', 'Rate': 128 * 1000 * 1000 }],
)

# TODO: figure out a way to limit its size while still remaining persistent
VOLUME_DRIVER_OPTS = dict(
    # type   = 'tmpfs',
    # device = 'tmpfs',
    # o      = 'size=128m',
)
