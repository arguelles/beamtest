#!/usr/bin/env python2
"""
Plots DDC2 waveforms
"""
import argparse
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from operator import add
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
        '-b', '--baseline', type=int, metavar='INT', required=False,
        help='''Baseline of ADC counts'''
    )
    parser.add_argument(
        '-n', '--nplot', type=int, metavar='INT', required=False,
        help='''Specify number of waveforms to plot'''
    )
    parser.add_argument(
        '-o', '--outfile', type=str, default='images/test.png',
        metavar='FILE', required=False, help='''Output location of plot'''
    )
    args = parser.parse_args()
    return args


def make_wv_plot(data, outfile, nplot):
    """Make the waveform plot"""
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111)

    ax.set_xlabel('Time (ns)')
    # ax.set_ylabel('Voltage (A.U.)')
    ax.set_ylabel('ADC counts')

    ax.set_xlim(600, 1000)
    # ax.set_ylim(0, 400)
    idx = 0
    for d in data:
        if idx == nplot: break
        for e in d:
            if idx == nplot: break

            ax.scatter(e[:,0], e[:,1], marker='o', c='crimson')
            ax.plot(e[:,0], e[:,1], linestyle='--', linewidth=1, c='crimson')
            idx += 1

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
    ntot = reduce(add, [x.shape[0] for x in data])
    print 'Loaded {0} waveforms'.format(ntot)

    for idx in range(len(data)):
        data[idx] = np.array(data[idx], dtype=np.float32)
        for e in data[idx]:
            e[:,0] *=  4 # convert to ns
            e[:,0] = np.flipud(e[:,0]) # flip in x axis
            e[:,1] = -e[:,1] # invert in y
            if args.baseline:
                e[:,1] += args.baseline
            # e[:,1] = e[:,1] / 3200. # convert to V

    if args.nplot is not None: nplot = args.nplot
    else: nplot = ntot
    make_wv_plot(data, args.outfile, nplot)

    print '=========='
    print 'DONE'
    print '=========='


main.__doc__ = __doc__


if __name__ == '__main__':
    main()
