#!/usr/bin/env python
"""
Plot waveforms through nios2-terminal
"""
import os, sys
import signal
import subprocess
from timeit import default_timer as timer
import argparse
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


COMMAND = 'nios2-download -g {0} && {1} | nios2-terminal'


class FullPaths(argparse.Action):
    """Append user- and relative-paths"""
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))


def is_valid_file(filepath):
    """Checks if a path is an actual file"""
    if not os.path.exists(filepath):
        msg = 'The file {0} does not exist!'.format(filepath)
        raise ValueError(msg)
    else:
        return filepath


def parse_args():
    """Get command line arguments"""
    parser = ArgumentParser(
        description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-i', '--infile', type=is_valid_file, action=FullPaths,
        metavar='FILE', required=True, help='''Settings file'''
    )
    parser.add_argument(
        '-d', '--ddc_file', type=is_valid_file, action=FullPaths,
        metavar='FILE', default='ddc2_nios2_sw.elf',
        help='''DDC2 download file'''
    )
    parser.add_argument(
        '-t', '--time', type=int, metavar='INT', default=10,
        help='''Number of seconds to run DDC2'''
    )
    args = parser.parse_args()
    return args


def run_setup(command):
    """Run the setup to start taking data"""
    print '=========='
    print 'Executing command:', command
    print '=========='
    cmd = command.split()
    p1 = subprocess.Popen([cmd[0], cmd[1], cmd[2]])
    p1.wait()
    p2 = subprocess.Popen(cmd[4], stdout=subprocess.PIPE)
    p2.wait()
    p3 = subprocess.Popen(
        cmd[6], stdin=p2.stdout, stdout=subprocess.PIPE, bufsize=1,
        preexec_fn=os.setsid
    )
    return p3


def main():
    args = parse_args()
    print '=========='
    print 'Running for {0}s'.format(args.time)
    print '=========='

    process = run_setup(COMMAND.format(args.ddc_file, args.infile))

    def signal_handler(sig, frame):
        print '=========='
        print 'Caught signal, cleaning up\n'
        print '=========='
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    start_t = timer()
    for line in iter(process.stdout.readline, b''):
        time = timer()
        if time - start_t > args.time:
            break
        print line,
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    print '=========='
    print 'DONE'
    print '=========='


main.__doc__ = __doc__


if __name__ == '__main__':
    main()
