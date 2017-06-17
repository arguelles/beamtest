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
import time


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
        '--no-invert', action='store_true', default=False,
        required=False, help='''Don't invert the waveform'''
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true', default=False,
        help='''Verbose'''
    )
    args = parser.parse_args()
    return args


def mk_time(timestamp_list):
    """Convert date/time into a single number representation"""
    a, b = timestamp_list
    year = int(a.split('-')[0])
    month = int(a.split('-')[1])
    day = int(a.split('-')[2])
    hour = int(b.split(':')[0])
    mins = int(b.split(':')[1])
    sec = int(np.floor(float(b.split(':')[2])))
    decimal = float('0.'+str(b.split('.')[-1]))

    return time.mktime((year, month, day, hour, mins, sec, 0, 0, 0)) + decimal


def run(input_folder, outfile, no_invert, verbose):
    """Main function to perform level1 processing"""

    l0_data = ''
    for filename in sorted(os.listdir(input_folder)):
        if '.txt.gz' not in filename:
            if 'dump_' in filename and '.txt' in filename:
                continue
            print 'Skipping file {0}'.format(filename)
            continue
        with gzip.open(input_folder+'/'+filename, 'rb') as f:
            l0_data_raw = f.read()
        l0_data += l0_data_raw
    for filename in sorted(os.listdir(input_folder)):
        if 'dump_' in filename and '.txt' in filename:
            with open(input_folder+'/'+filename, 'r') as f:
                l0_data_raw = f.read()
            l0_data += l0_data_raw
    l0_data = l0_data.split('---------------------------------------------------------------------------------------------------')
    if verbose: print 'Number of waveforms = {0}'.format(len(l0_data))

    baseline = int(l0_data[0].split('\n')[0].rstrip().split(' ')[-1])
    if verbose: print 'Baseline = {0}'.format(baseline)
    l0_data[0] = l0_data[0][l0_data[0].index('\n')+1:]

    initial_st_ts = l0_data[0].split('\n')[0].rstrip().split(' ')[-2:]
    initial_mk_ts = mk_time(initial_st_ts)
    if verbose: print 'Initial mktime = {0}'.format(initial_mk_ts)
    l0_data[0] = l0_data[0][l0_data[0].index('\n')+1:]

    l1_df = []
    initial_fpga_ts = None
    for wf_str in l0_data:
        wf_arr = wf_str.split('\n')
        if 'start timestamp' not in wf_arr[5]:
            raise AssertionError('timestamp not found')
        if 'local time' not in wf_arr[6]:
            raise AssertionError('local time not found')
        if 'Nsamples' not in wf_arr[8]:
            raise AssertionError('NSamples not found')
        fpga_ts = int(wf_arr[5].split('=')[1].strip().split(',')[0])
        local_time = int(wf_arr[6].split('=')[1].strip().split(',')[0])
        Nsamples = int(wf_arr[8].rstrip().split(' ')[-1])
        if verbose: print 'timestamp = {0}'.format(fpga_ts)
        if verbose: print 'local_time = {0}'.format(local_time)
        if verbose: print 'Nsamples = {0}'.format(Nsamples)

        if initial_fpga_ts is None:
            initial_fpga_ts = fpga_ts
            if verbose: print 'Initial FPGA timestamp {0}'.format(initial_fpga_ts)

        index = range(Nsamples)
        columns = ['isamp', 'adc', 'timestamp']
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
        if not no_invert:
            # invert in y axis
            wv_data[:,1] = -wv_data[:,1]
            # renormalise to baseline
            wv_data[:,1] = wv_data[:,1] + baseline
        else:
            # renormalise to baseline
            wv_data[:,1] = wv_data[:,1] - baseline

        df = pd.DataFrame(wv_data, columns=columns)
        df = df.assign(index = len(l1_df))

        # LSB = 0.220 mV/ADC count
        df = df.assign(voltage = df['adc'] * 0.220)
        # Internal clock of DDC2 is at 250 MHz (4ns)
        timestamp = initial_mk_ts + 4 * (fpga_ts - initial_fpga_ts +
                                         df['timestamp'] - local_time)
        df['timestamp'] = timestamp

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
        invert = args.invert,
        verbose = args.verbose
    )

    print '=========='
    print 'DONE'
    print '=========='


main.__doc__ = __doc__


if __name__ == '__main__':
    main()
