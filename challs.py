#! /usr/bin/env python3

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import yaml

from app.lib.challs import load
from app.lib.differ import diff_all


def print_diff(result):
    for function, info in result.items():
        if info['delta'][1] == info['delta'][3]:
            continue
        hunks = info['hunks']
        for hunk in hunks:
            if hunk[0] == 0:
                continue
            if hunk[0] == 1:
                print(re.sub('^', '+', hunk[1].rstrip(), flags=re.MULTILINE))
            if hunk[0] == -1:
                print(re.sub('^', '-', hunk[1].rstrip(), flags=re.MULTILINE))

def strip(path):
    command = ['strip', '--strip-debug', path]
    return subprocess.run(command, check=True)


def validate(challenge, tmpdir, compile=False, disassemble=False):
    for challenge in challenges:
        print('Validating ' + challenge.name + '...')

        # Make sure we have everything neeed to build...
        if not os.path.isfile(challenge.source):
            print('  Missing source code!')
            continue
        if not os.path.isfile(challenge.starter):
            print('  Missing starter code!')
        if not os.path.isfile(challenge.builder):
            print('  Missing build script!')
            continue
        if not os. access(challenge.builder, os.X_OK):
            print('  Build script is not executable!')
            continue

        # Try to build this thing!
        impl = challenge.impl(tmpdir)
        shutil.copyfile(challenge.source, impl.source)
        result = challenge.build(impl)

        if result.returncode != 0:
            print('  Compilation failed!')
            print(result.stdout)
            continue

        # Make sure we have everything neeed to test...
        if not os.path.isfile(challenge.tester):
            print('  Missing test script!')
            continue
        if not os. access(challenge.tester, os.X_OK):
            print('  Test script is not executable!')
            continue

        # Run some tests!
        test = challenge.test(impl, verbose=True)
        if test['pass'] != test['total']:
            print('  New binary failed tests (%d%%)!' % (100 * test['pass'] / test['total']))
            continue

        if compile:
            shutil.copyfile(impl.binary, challenge.binary)
            strip(challenge.binary)
        else:
            test = challenge.test(impl, verbose=True)
            if test['pass'] != test['total']:
                print('  Old binary failed tests (%d%%)!' % (100 * test['pass'] / test['total']))

        # Disassemble some things...
        newasm = challenge.disassemble(impl, srcmap=False, warn=True)
        if disassemble:
            with open(challenge.disasm, 'w') as file:
                yaml.dump(newasm, file)
        # else:
        #     with open(challenge.disasm) as file:
        #         newasm = yaml.safe_load(file)

        #     result, delta = diff_all(binasm, oldasm)
        #     if delta[1] != delta[3]:
        #         print('  New binary does not disassemble to target!')
        #         print_diff(result)

        with open(challenge.disasm) as file:
            oldasm = yaml.safe_load(file)
        binasm = challenge.disassemble(challenge, srcmap=False, warn=True)

        result, delta = diff_all(binasm, oldasm)
        if delta[1] != delta[3]:
            print('  Old binary does not disassemble to target!')
            print_diff(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--compile',     action='store_true', help='regenerate binary.out files')
    parser.add_argument('-d', '--disassemble', action='store_true', help='regenerate disasm.yml files')
    parser.add_argument('-l', '--language',    action='append',     help='only check these languages')

    parser.add_argument('config',            help='path to config.json')
    parser.add_argument('name',   nargs='*', help='only check these challenges')
    args = parser.parse_args()

    challenges = load(args.config)

    if args.language:
        challenges = [c for c in challenges if c.language in args.language]

    for name in args.name:
        for challenge in challenges:
            if challenge.name == name:
                break
        else:
            print('Not running ' + name + '!')

    if args.name:
        challenges = [c for c in challenges if c.name in args.name]

    def literal_presenter(dumper, data):
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    yaml.add_representer(str, literal_presenter)

    with tempfile.TemporaryDirectory(prefix='deco') as tmpdir:
        validate(challenges, tmpdir, compile=args.compile, disassemble=args.disassemble)
