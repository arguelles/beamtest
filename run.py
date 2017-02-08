#!/usr/bin/env python2
"""
Runs DDC2 through nios2-terminal
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
        print values
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
        '-o', '--outfile', type=str, default='./data/test/test',
        metavar='FILE', required=False,
        help='''Output location of data (no need to include file extension)'''
    )
    parser.add_argument(
        '--live', action='store_true', default=False,
        help='''Live visualisation'''
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
    """Parse the string from nios2-terminal"""
    return arr_str.rstrip().replace(' ', '').split(',')[:-1]


def check_data(raw_data, nsamples, verbose):
    """Remove the data which only partially captures a full waveform"""
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
        if np.diff(list(n_of_runs))[0] != 1:
            raise AssertionError(
                'Something bad happened!\nn_of_runs = '
                '{0}\nnp.diff(list(n_of_runs))[0] = '
                '{1}'.format(n_of_runs, np.diff(list(n_of_runs))[0])
            )
        n_incomplete_pulse = np.sum(uc_run_counts == np.max(list(n_of_runs)))
        if verbose:
            print 'n_incomplete_pulse', n_incomplete_pulse
        clean_data = raw_data[:-n_incomplete_pulse]
    else:
        clean_data = raw_data

    if verbose:
        print 'clean_data', clean_data
        print 'clean_data.shape', clean_data.shape

    return clean_data


def run(infile, ddc_file, time_lim, live, verbose):
    """Main function to run FPGA and DDC2 chain and collect the data"""
    print '=========='
    print 'Running for {0}s'.format(time_lim)

    process = run_setup(COMMAND.format(ddc_file, infile))

    def signal_handler(sig, frame):
        print 'Caught signal, cleaning up\n'
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    str_data = []
    skip_intro = True
    skip_initial_wv = True
    idx = 0
    try:
        if live:
            from matplotlib import pyplot as plt
            from matplotlib.offsetbox import AnchoredText
            plt.ion()
            fig = plt.figure(figsize=(12, 8))
            ax = fig.add_subplot(111)
            ax.set_xlabel('Time (4ns)')
            ax.set_ylabel('Voltage (A.U.)')
            xmax = 1
            ymin, ymax = (999999, 1)
            live_data = []

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
                    continue
            if skip_initial_wv:
                time = timer()
                # Wait before recording any data to flush previous buffer
                if time - start_t < 2 or '---------------------------' in line:
                    continue
                else:
                    start_t = timer()
                    skip_initial_wv = False
            time = timer()
            if verbose:
                print line,
            if time - start_t > time_lim:
                break
            str_data.append(line)

            if live:
                try: d = map(int, parse(line))
                except: continue
                if len(d) == 0: continue
                if d[0] == 0:
                    if live_data == []: continue
                    ax.set_xlim(0, xmax)
                    # ax.set_ylim(ymin, ymax)
                    ax.set_ylim(9070-1000, 9070+10)
                    ax.xaxis.grid(True, which='major')
                    ax.yaxis.grid(True, which='major')
                    ld = np.vstack(live_data)
                    ax.scatter(ld[:,0], ld[:,1], marker='o', c='crimson')
                    ax.plot(ld[:,0], ld[:,1], linestyle='--', linewidth=1,
                            c='crimson')
                    at = AnchoredText('min = {0}\nmax = {1}'.format(ymin, ymax),
                                      prop=dict(size=14), frameon=True, loc=1)
                    at.patch.set_boxstyle("round,pad=0.,rounding_size=0.5")
                    ax.add_artist(at)
                    plt.pause(0.001)
                    ax.cla()
                    live_data = []
                if d[0] > xmax: xmax = d[0]
                if d[1] < ymin: ymin = d[1]
                if d[1] > ymax: ymax = d[1]
                live_data.append([d[0], d[1]])
    except:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        raise
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)

    n_count = 0
    nsamples = 0
    timestamp = 0
    local_time = 0
    raw_data = []
    for idx in range(len(str_data)):
        if 'Nsamples' in str_data[idx] and nsamples == 0:
            nsamples = int(str_data[idx].split()[2])
            continue
        if 'timestamp' in str_data[idx]:
            timestamp = int(str_data[idx].split()[3][:-1])
            continue
        if 'local time' in str_data[idx]:
            local_time = int(str_data[idx].split()[4][:-1])
            continue
        if nsamples == 0: continue
        if ',' not in str_data[idx]: continue
        if len(str_data[idx].split()) != 5: continue
        try: timing = int(str_data[idx].split()[0][:-1])
        except: continue
        if verbose:
            print timing, n_count
        if timing == 0 and n_count != 0:
            # remove incomplete waveforms
            raw_data = raw_data[:-n_count]
            n_count = 0
        if n_count == 0 and timing != 0:
            n_count = timing
        if timing != n_count:
            raise AssertionError(
                'Something went wrong! timing != n_count! {0} != '
                '{1}\n{2}'.format(timing, n_count, str_data[idx])
            )
        raw_data.append(map(int, parse(str_data[idx])) + [timestamp, local_time])
        if n_count >= nsamples: n_count += 1
        elif n_count == nsamples-1: n_count = 0
        else: n_count += 1
    raw_data = np.array(raw_data)
    data = check_data(raw_data, nsamples, verbose)

    timings, run_counts = np.unique(data[:,0], return_counts=True)

    if len(set(run_counts)) != 1:
        raise AssertionError(
            'Something bad happened!\nrun_counts = {0}\nlen(set(run_counts)) '
            '= {1}'.format(run_counts, len(set(run_counts)))
        )
    run_counts = run_counts[0]

    trns_data = data.reshape(run_counts, len(timings), data.shape[1])
    if verbose:
        print 'trns_data', trns_data
        print 'trns_data.shape', trns_data.shape

    return trns_data


def main():
    args = parse_args()
    data = run(args.infile, args.ddc_file, args.time, args.live, args.verbose)

    print 'Number of waveforms = {0}'.format(data.shape[0])

    of = args.outfile
    idx = 0
    if '_000' not in of:
        of += '_000'
    while os.path.exists(of+'.npy'):
        of = of.replace('_{0:003d}'.format(idx), '_{0:003d}'.format(idx+1))
        idx += 1
    of += '.npy'
    print 'Saving to file', of
    np.save(of, data)

    print '=========='
    print 'DONE'
    print '=========='


main.__doc__ = __doc__


if __name__ == '__main__':
    main()
