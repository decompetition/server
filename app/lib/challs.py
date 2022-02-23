#! /usr/bin/env python3

import collections
import json
import os
import re

from . import minidis
from . import sandbox

Language = collections.namedtuple('Language', ['slug', 'name', 'extension'])
LANGUAGES = {
    'c':     Language('c',     'C',     '.c'),
    'cpp':   Language('cpp',   'C++',   '.cpp'),
    'nim':   Language('nim',   'Nim',   '.nim'),
    'go':    Language('go',    'Go',    '.go'),
    'rust':  Language('rust',  'Rust',  '.rs'),
    'swift': Language('swift', 'Swift', '.swift'),
}

class ChallengeImpl:
    def __init__(self, info, folder):
        self.info    = info
        self.folder  = folder
        self.source  = os.path.join(folder, 'source'  + info.extension)
        self.binary  = os.path.join(folder, 'binary.out')


class ChallengeInfo:
    def __init__(self, name, root, data, defaults={}):
        self.name      = name
        self.value     = data['value']
        self.language  = data['language']
        self.extension = LANGUAGES[self.language].extension

        def replace(match):
            text = match.group()
            if text == '%n': return name
            if text == '%r': return root
            if text == '%f': return self.folder
            if text == '%l': return self.language
            if text == '%x': return self.extension
            raise Exception('Unknown escape: ' + text)

        def lookup(key):
            val = data.get(key)
            if val is not None:
                return val
            val = defaults[key]
            if isinstance(val, str):
                val = re.sub('%.', replace, val)
            return val

        self.folder    = os.path.join(root, lookup('folder'))
        self.container = lookup('container')
        self.functions = lookup('functions')
        self.options   = lookup('options')

        self.binary  = os.path.join(root, lookup('binary'))
        self.builder = os.path.join(root, lookup('builder'))
        self.disasm  = os.path.join(root, lookup('disasm'))
        self.source  = os.path.join(root, lookup('source'))
        self.starter = os.path.join(root, lookup('starter'))
        self.tester  = os.path.join(root, lookup('tester'))

    def build(self, impl):
        return sandbox.build(self, impl)

    def disassemble(self, impl, srcmap=True, warn=False):
        return minidis.disassemble(impl.binary, self.language, self.functions, srcmap=srcmap, warn=warn)

    def impl(self, folder):
        return ChallengeImpl(self, folder)

    def test(self, impl, verbose=False):
        return sandbox.test(self, impl, verbose=verbose)


def load(path):
    root = os.path.abspath(os.path.dirname(path))
    with open(path) as file:
        config = json.load(file)

    challenges = []
    defaults   = config.get('defaults', {})
    for name, data in config['binaries'].items():
        challenges.append(ChallengeInfo(name, root, data, defaults))
    return challenges


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='path to config.json')
    args = parser.parse_args()

    challenges = load(args.config)
    for challenge in challenges:
        print('Name:', challenge.name)
        print('  Container: ', challenge.container)
        print('  Functions: ', ' '.join(challenge.functions))
        print('  Builder:   ', challenge.builder)
        print('  Options:   ', ' '.join(challenge.options))
        print()
        print('  Source:    ', challenge.source)
        print('  Binary:    ', challenge.binary)
        print('  Disasm:    ', challenge.disasm)
        print('  Starter:   ', challenge.starter)
        print('  Tester:    ', challenge.tester)
        print()
