#!/usr/bin/env python2
"""
Plots DDC2 waveforms
"""
import argparse
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
mpl.rcParams['mathtext.fontset'] = 'custom'
mpl.rcParams['mathtext.rm'] = 'Bitstream Vera Sans'
mpl.rcParams['mathtext.it'] = 'Bitstream Vera Sans:italic'
mpl.rcParams['mathtext.bf'] = 'Bitstream Vera Sans:bold'

from run import run, is_valid_file


def parse_args():
    """Get command line arguments"""
    parser = ArgumentParser(
        description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'infiles', type=is_valid_file, nargs='+', metavar='FILES',
        help='''Numpy files'''
    )
    parser.add_argument(
        '-o', '--outfile', type=str, default='images/test.png',
        metavar='FILE', required=False, help='''Output location of plot'''
    )
    args = parser.parse_args()
    return args


def make_wv_plot(data, outfile):
    """Make the waveform plot"""
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111)

    ax.set_xlabel('Time (4ns)')
    ax.set_ylabel('Voltage (A.U.)')

    for d in data:
        ax.scatter(d[:,0], d[:,1], marker='o', c='crimson')
        ax.plot(d[:,0], d[:,1], linestyle='--', linewidth=1, c='crimson')

    for ymaj in ax.yaxis.get_majorticklocs():
        ax.axhline(y=ymaj, ls=':', color='gray', alpha=0.7, linewidth=1)
    for xmaj in ax.xaxis.get_majorticklocs():
        ax.axvline(x=xmaj, ls=':', color='gray', alpha=0.7, linewidth=1)

    fig.savefig(outfile, bbox_inches='tight', dpi=150)


def main():
    args = parse_args()

    data = []
    for f in args.infiles:
        data.append(np.load(f))
    data = np.vstack(data)

    make_wv_plot(data, args.outfile)

    print '=========='
    print 'DONE'
    print '=========='


main.__doc__ = __doc__


if __name__ == '__main__':
    main()
