#!/usr/bin/env python2
"""
Plot charge histogram from pandas DataFrame object
"""
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.offsetbox import AnchoredText
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
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
        '-b', '--bins', type=int, default='100', metavar='INT', required=False,
        help='''Number of bins'''
    )
    args = parser.parse_args()
    return args


def run(infile, outfile, bins):
    """Main function to do plotting"""

    store = pd.HDFStore(infile)
    df = store['df']
    store.close()

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111)

    print 'plotting...'
    charges = df['charge'].unique()
    print charges
    assert 0
    binning = np.linspace(np.min(charges), np.max(charges), bins+1)

    ax.set_xlim(np.min(charges), np.max(charges))
    # ax.set_ylim(0, 1000)

    hist, _ = np.histogram(charges, binning)
    hist_0 = np.concatenate([[hist[0]], hist])

    # cut away empty waveforms
    cut_at = 0
    hist_cut = hist[cut_at:]
    binning_cut = binning[cut_at:]
    bin_centres = (binning_cut[:-1] + binning_cut[1:])/2.

    def gauss(x, *p):
        A, mu, sigma = p
        return A*np.exp(-(x-mu)**2/(2.*sigma**2))

    # initial guess
    p0 = [1., 0., 1.]
    print hist_cut
    coeff, var_matrix = curve_fit(gauss, bin_centres, hist_cut, p0=p0)
    hist_fit = gauss(bin_centres, *coeff)
    pe = (coeff[1] / coeff[2])**2

    # internal impedence of DDC2 is 150 ohms
    gain = (coeff[1] * 1e-9) / (pe * 150. * 1.6e-19)

    ax.step(
        binning, hist_0, alpha=1, drawstyle='steps-pre', linewidth=1,
        linestyle='-', color='r'
    )
    ax.plot(bin_centres, hist_fit, label='Fitted with gaussian')

    ax.set_xlabel('Charge (nVs)')
    ax.set_ylabel('N')

    for ymaj in ax.yaxis.get_majorticklocs():
        ax.axhline(y=ymaj, ls=':', color='gray', alpha=0.7, linewidth=1)
    for xmaj in ax.xaxis.get_majorticklocs():
        ax.axvline(x=xmaj, ls=':', color='gray', alpha=0.7, linewidth=1)

    ax.legend()
    at = AnchoredText(r'$A = {0:.3f}$'.format(coeff[0]) + '\n' +
                      r'$\mu = {0:.3f}$'.format(coeff[1]) + '\n' +
                      r'$\sigma = {0:.3f}$'.format(coeff[2]) + '\n' +
                      r'$(\frac{\mu}{\sigma})^2 = PE = ' + r'{0:.1f}$'.format(pe) + '\n' +
                      r'gain = {0:.2e}'.format(gain),
                      prop=dict(size=12), frameon=True, loc=5)
    at.patch.set_boxstyle("round,pad=0.3,rounding_size=0.2")
    ax.add_artist(at)

    fig.savefig(outfile, bbox_inches='tight', dpi=150)


def main():
    args = parse_args()
    run(
        infile = args.infile,
        outfile = args.outfile,
        bins = args.bins
    )

    print '=========='
    print 'DONE'
    print '=========='


main.__doc__ = __doc__


if __name__ == '__main__':
    main()

