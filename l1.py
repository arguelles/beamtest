#!/usr/bin/env python2
"""
Level 1 processing for DDC2 level0 data.
"""
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import gzip
from io import StringIO
import numpy as np
import os
import pandas as pd
import scipy.interpolate as interpolate


def parse_args():
    """Get command line arguments"""
    parser = ArgumentParser(
        description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-i', '--input_folder', type=str, metavar='FOLDER', required=True,
        help='''Path to folder containing level0 data'''
    )
    parser.add_argument(
        '-o', '--outfile', type=str, default='./data/test/l1.npy',
        metavar='FILE', required=False,
        help='''Output location of level1 data'''
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true', default=False,
        help='''Verbose'''
    )
    args = parser.parse_args()
    return args

def run(input_folder, outfile, verbose):
    """Main function to perform level1 processing"""

    l0_data = []
    for filename in os.listdir(input_folder):
        if '.txt.gz' not in filename:
            print 'Skipping file {0}'.format(filename)
            continue
        with gzip.open(input_folder+'/'+filename, 'rb') as f:
            l0_data_raw = f.read()
        l0_data += l0_data_raw.split('---------------------------------------------------------------------------------------------------')
    if verbose: print 'Number of waveforms = {0}'.format(len(l0_data))

    baseline = int(l0_data[0].split('\n')[0].rstrip().split(' ')[-1])
    del l0_data[0]
    if verbose: print 'Baseline = {0}'.format(baseline)

    l1_df = []
    for wf_str in l0_data:
        wf_arr = wf_str.split('\n')
        if 'timestamp' not in wf_arr[5]:
            raise AssertionError('timestamp not found')
        if 'Nsamples' not in wf_arr[8]:
            raise AssertionError('NSamples not found')
        timestamp = int(wf_arr[5].split('=')[1].strip().split(',')[0])
        Nsamples = int(wf_arr[8].rstrip().split(' ')[-1])
        if verbose: print 'timestamp = {0}'.format(timestamp)
        if verbose: print 'Nsamples = {0}'.format(Nsamples)

        index = range(Nsamples)
        columns = ['isamp', 'adc', 'time']
        wv_data = np.loadtxt(
            StringIO(u'{0}'.format(reduce(lambda x,y: x+'\n'+y, wf_arr[11:]))),
            dtype=int,
            delimiter=',',
            usecols=(0, 1, 2)
        )
        if len(wv_data) != Nsamples:
            if verbose: print 'skipping incomplete waveform'
            continue
        # convert to ns
        wv_data[:,0] *= 4
        # renormalise to baseline
        wv_data[:,1] = wv_data[:,1] - baseline

        df = pd.DataFrame(wv_data, columns=columns)
        df = df.assign(index = len(l1_df))

        df = df.assign(voltage = df['adc'] * -0.220)
        # Internal clock of DDC2 is at 250 MHz (4ns)
        df = df.assign(timestamp = df['time'] + (4 * timestamp))

        wv_spline = interpolate.splrep(df['isamp'], df['voltage'], s=0)
        wv_area = interpolate.splint(0, np.max(df['isamp']), wv_spline)
        # convert to nVs
        charge = wv_area / 1e3
        df = df.assign(charge = charge)

        df = df.reindex(index)
        l1_df.append(df)
    # l1_df = pd.concat(l1_df, axis=1, keys=range(len(l1_df)))
    print 'Number of waveforms = {0}'.format(len(l1_df))
    l1_df = pd.concat(l1_df)

    store = pd.HDFStore(outfile)
    store['df'] = l1_df
    store.close()


def main():
    args = parse_args()
    run(
        input_folder = args.input_folder,
        outfile = args.outfile,
        verbose = args.verbose
    )

    print '=========='
    print 'DONE'
    print '=========='


main.__doc__ = __doc__


if __name__ == '__main__':
    main()
