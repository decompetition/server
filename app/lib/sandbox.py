import os
import subprocess

def build(chal, impl, options=[], **kwargs):
    source = '/mnt/' + os.path.basename(impl.source)
    binary = '/mnt/' + os.path.basename(impl.binary)
    return run(chal.container,
        command = ['/run-me', source, binary] + options,
        volumes = [
            os.path.abspath(chal.builder) + ':/run-me:ro',
            os.path.abspath(impl.folder)  + ':/mnt'
        ],
        **kwargs
    )

def run(container, command, user='root', volumes=[], timeout=10):
    volumes = sum(map(lambda v: ['--volume', v], volumes), [])
    options = [
        '--network', 'none',
        '--user',     user,
        '--rm',
        '--',
        container,
    ]

    return subprocess.run(['docker', 'run'] + volumes + options + command,
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT,
        universal_newlines = True,
        timeout = timeout
    )

def test(chal, impl, verbose=False, **kwargs):
    binary = '/mnt/' + os.path.basename(impl.binary)
    scores = {'pass': 0, 'fail': 0, 'error': 0, 'total': 0}
    flags  = ['-v'] if verbose else []
    try:
        result = run(chal.container,
            user    = 'nobody',
            command = ['/run-me', *flags, binary],
            volumes = [
                os.path.abspath(chal.tester) + ':/run-me:ro',
                os.path.abspath(impl.binary) + ':' + binary + ':ro'
            ],
            **kwargs
        )
    except subprocess.TimeoutExpired:
        scores['error'] = 1
        scores['total'] = 1
        return scores

    for line in result.stdout.splitlines():
        if verbose and not line.startswith('PASS'):
            print(line)

        if line.startswith('PASS'):
            scores['pass'] += 1
        elif line.startswith('FAIL'):
            scores['fail'] += 1
        elif line.startswith('ERROR'):
            scores['error'] += 1
        else:
            continue
        scores['total'] += 1
    return scores
