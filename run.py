#!/usr/bin/env python2
"""
Plot waveforms through nios2-terminal
"""
import os, sys
import signal
import subprocess
import numpy as np
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
        '-t', '--time', type=int, metavar='INT', default=5,
        help='''Number of seconds to run DDC2'''
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true', default=False,
        help='''Verbose'''
    )
    args = parser.parse_args()
    return args


def run_setup(command):
    """Run the setup to start taking data"""
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


def parse(arr_str):
    return arr_str.rstrip().replace(' ', '').split(',')[:-1]


def clean_data(raw_data, verbose):
    if verbose:
        print 'raw_data', raw_data
        print 'raw_data.shape', raw_data.shape
    uc_timings, uc_run_counts = np.unique(raw_data[:,0], return_counts=True)
    if verbose:
        print 'uc_timings', uc_timings
        print 'uc_run_counts', uc_run_counts

    n_of_runs = set(uc_run_counts)
    if len(n_of_runs) != 1 and len(n_of_runs) != 2:
        raise AssertionError(
            'Something bad happened!\nn_of_runs = {0}\nlen(n_of_runs) = '
            '{1}'.format(n_of_runs, len(n_of_runs))
        )

    if len(n_of_runs) == 2:
        n_incomplete_pulse = np.sum(uc_run_counts == np.max(list(n_of_runs)))
        print 'n_incomplete_pulse', n_incomplete_pulse
        clean_data = raw_data[:-n_incomplete_pulse]
    else:
        clean_data = raw_data

    if verbose:
        print 'clean_data', clean_data
        print 'clean_data.shape', clean_data.shape

    return clean_data


def main():
    args = parse_args()
    print '=========='
    print 'Running for {0}s'.format(args.time)

    process = run_setup(COMMAND.format(args.ddc_file, args.infile))

    def signal_handler(sig, frame):
        print 'Caught signal, cleaning up\n'
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    raw_data = []
    skip_intro = True
    idx = 0
    try:
        for line in iter(process.stdout.readline, b''):
            if skip_intro:
                try:
                    int(line.split(',')[0])
                except:
                    print line,
                    if 'INVALID' in line:
                        raise AssertionError('Reset the DDC2 and run again')
                    idx += 1
                    continue
                else:
                    if idx < 10:
                        raise AssertionError('Reset the DDC2 and run again')
                    start_t = timer()
                    skip_intro = False
            time = timer()
            if args.verbose:
                # print 'time = {0}'.format(time - start_t)
                print line,
            if time - start_t > args.time:
                break
            raw_data.append(map(int, parse(line)))
    except:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        raise
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)

    raw_data = np.array(raw_data)
    data = clean_data(raw_data, args.verbose)

    timings, run_counts = np.unique(data[:,0], return_counts=True)

    if len(set(run_counts)) != 1:
        raise AssertionError(
            'Something bad happened!\nrun_counts = {0}\nlen(set(run_counts)) '
            '= {1}'.format(run_counts, len(set(run_counts)))
        )
    run_counts = run_counts[0]

    trns_data = data.reshape(run_counts, len(timings), data.shape[1])
    if args.verbose:
        print 'trns_data', trns_data
        print 'trns_data.shape', trns_data.shape

    print '=========='
    print 'DONE'
    print '=========='


main.__doc__ = __doc__


if __name__ == '__main__':
    main()
