#!/usr/bin/env python2
"""
Plot charge histogram from pandas DataFrame object
"""
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
mpl.rcParams['mathtext.fontset'] = 'custom'
mpl.rcParams['mathtext.rm'] = 'Bitstream Vera Sans'
mpl.rcParams['mathtext.it'] = 'Bitstream Vera Sans:italic'
mpl.rcParams['mathtext.bf'] = 'Bitstream Vera Sans:bold'


def parse_args():
    """Get command line arguments"""
    parser = ArgumentParser(
        description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-i', '--infile', type=str, metavar='FILE', required=True,
        help='''Path to data object'''
    )
    parser.add_argument(
        '-o', '--outfile', type=str, default='./images/test.png',
        metavar='FILE', required=False,
        help='''Output path of figure'''
    )
    args = parser.parse_args()
    return args


def run(infile, outfile):
    """Main function to do plotting"""

    store = pd.HDFStore(infile)
    df = store['df']
    store.close()

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111)

    print 'plotting...'
    charges = df['charge'].unique()
    binning = np.linspace(np.min(charges), np.max(charges), 101)

    ax.set_xlim(np.min(charges), np.max(charges))
    # ax.set_ylim(0, 1000)

    hist, _ = np.histogram(charges, binning)
    hist_0 = np.concatenate([[hist[0]], hist])
    ax.step(
        binning, hist_0, alpha=1, drawstyle='steps-pre', linewidth=1,
        linestyle='-', color='r'
    )

    ax.set_xlabel('Charge (nVs)')
    ax.set_ylabel('N')

    for ymaj in ax.yaxis.get_majorticklocs():
        ax.axhline(y=ymaj, ls=':', color='gray', alpha=0.7, linewidth=1)
    for xmaj in ax.xaxis.get_majorticklocs():
        ax.axvline(x=xmaj, ls=':', color='gray', alpha=0.7, linewidth=1)

    fig.savefig(outfile, bbox_inches='tight', dpi=150)


def main():
    args = parse_args()
    run(
        infile = args.infile,
        outfile = args.outfile,
    )

    print '=========='
    print 'DONE'
    print '=========='


main.__doc__ = __doc__


if __name__ == '__main__':
    main()

