#!/usr/bin/env python2
"""
Records the raw input from the DDC2 through the Quartus 2 nios2eds terminal and
saves the data to disk.
"""
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from copy import deepcopy
import gzip
from multiprocessing import Process
import numpy as np
import os, sys
import signal
import subprocess
from timeit import default_timer as timer


COMMAND = 'nios2-download -g {0} && {1} | nios2-terminal'


def parse_args():
    """Get command line arguments"""
    parser = ArgumentParser(
        description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-i', '--settings', type=str, metavar='FILE', required=True,
        help='''DDC2 settings file'''
    )
    parser.add_argument(
        '-d', '--ddc_dfile', type=str, metavar='FILE',
        default='ddc2_nios2_sw.elf', help='''DDC2 download file'''
    )
    parser.add_argument(
        '-t', '--time', type=int, metavar='INT', default=5,
        help='''Number of seconds to run DDC2'''
    )
    parser.add_argument(
        '-o', '--outdir', type=str, default='./data/test/',
        metavar='FOLDER', required=False,
        help='''Output location of folder to contain data'''
    )
    parser.add_argument(
        '--chunk', type=int, default=1e5, metavar='INT', required=False,
        help='''Number of lines to save before splitting into a new file'''
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


def run(settings, ddc_dfile, time_lim, outdir, chunk, verbose):
    """Main function to run FPGA and DDC2 chain and collect the data"""
    print '=========='
    print 'Running for {0}s'.format(time_lim)

    process = run_setup(COMMAND.format(ddc_dfile, settings))

    def signal_handler(sig, frame):
        print 'Caught signal, cleaning up\n'
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    stream = ''
    baseline = 0
    skip_intro = True
    skip_initial_wv = True
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
                    if 'TAP_GET_BASELINE' in line:
                        stream += 'BASELINE = ' + line.split(' ')[-1][1:-2]
                        stream += '\n' + '\n'
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

            stream += line

            if idx % chunk == 0:
                s_copy = deepcopy(stream)
                def save_to_disk():
                    of = outdir+'/level0_{0:06d}.txt.gz'.format(int(idx/chunk))
                    with gzip.GzipFile(of, 'wb') as outfile:
                        outfile.write(s_copy)
                p = Process(target = save_to_disk)
                p.start()
                stream = ''
            idx += 1
    except:
        print 'Error, cleaning up\n'
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        print 'Dumping data to dump_{0:06d}.txt'.format(int(idx/chunk))
        of = './dump_{0:06d}.txt'.format(int(idx/chunk))
        with open(of, 'wb') as outfile:
            outfile.write(stream)
        raise
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)

    outfile = outdir+'/level0_{0:06d}.txt.gz'.format(int(idx/chunk))
    with gzip.GzipFile(outfile, 'wb') as outfile:
        outfile.write(stream)
    stream = ''


def main():
    args = parse_args()
    run(
        settings = args.settings,
        ddc_dfile = args.ddc_dfile,
        time_lim = args.time,
        outdir = args.outdir,
        chunk = args.chunk,
        verbose = args.verbose
    )

    print '=========='
    print 'DONE'
    print '=========='


main.__doc__ = __doc__


if __name__ == '__main__':
    main()
