#!/usr/bin/env python2
"""
Plot waveforms from pandas DataFrame object
"""
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import scipy.interpolate as interpolate
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
    parser.add_argument(
        '-n', '--nplot', type=int, required=False, default=None,
        metavar='INT', help='''Specify number of waveforms to plot'''
    )
    parser.add_argument(
        '--ymax', type=int, required=False, default=1000,
        metavar='INT', help='''Y axis maximum value'''
    )
    parser.add_argument(
        '--interpolate', action='store_true', default=False,
        help='''Plot the interpolated waveforms'''
    )
    args = parser.parse_args()
    return args


def run(infile, outfile, interp, nplot, ymax):
    """Main function to do plotting"""

    store = pd.HDFStore(infile)
    df = store['df']
    store.close()

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111)

    ax.set_xlim(0, np.max(df['isamp']))
    ax.set_ylim(-ymax/10, ymax)

    print 'plotting...'
    if not interp:
        if nplot is None:
            df.plot(x='isamp', y='voltage', ax=ax)
        else:
            wv_idx = df['index'].unique()
            for i, idx in enumerate(wv_idx):
                if i == nplot:
                    break
                wv_df = df[df['index'] == idx]
                wv_df.plot(x='isamp', y='voltage', ax=ax)
    else:
        wv_idx = df['index'].unique()
        for i, idx in enumerate(wv_idx):
            if nplot is not None:
                if i == nplot:
                    break
            wv_df = df[df['index'] == idx]
            spl = interpolate.splrep(wv_df['isamp'], wv_df['voltage'], s=0)
            x = np.linspace(0, np.max(wv_df['isamp']), 200)
            y = interpolate.splev(x, spl)
            ax.scatter(x, y, marker='o', c='blue')
            ax.plot(x, y, linestyle='-', linewidth=1, c='blue')

    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('Voltage (mV)')

    legend = ax.legend()
    if legend is not None:
        legend.remove()

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
        interp = args.interpolate,
        nplot = args.nplot,
        ymax = args.ymax
    )

    print '=========='
    print 'DONE'
    print '=========='


main.__doc__ = __doc__


if __name__ == '__main__':
    main()
