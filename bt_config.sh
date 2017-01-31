#!/bin/sh
#
# Tyler Anderson Wed Nov  5 10:12:38 EST 2014
# Simple example script for controlling DDC2

############### Top Level Commands ##################
# Runtime mode
# 0: Normal (outputs header, footer, local time word, data) 
# 1: Metered (auto-triggered, collects enough test runs for 100ksamples, good for realtime performance metrics)
# 2: Sparse (good for redirecting data to file)
echo "RUNTIME_MODE 2"

# Trigger mode
# 0: Normal (retriggerable on threshold crossing)
# 1: Single. In constant record mode, record is armed by SoCKit KEY2 press.
echo "TRIG_MODE 0"

# Set the record-length mode bit
# 0: TOT mode. Collect record length that depends on TOT
# 1: Constant record length mode. Collect a number of samples based on AF_SET_CNST_CONFIG
echo "AF_SET_CNST_RUN 1"

# Get the logic version number (auto-incremented with each firmware compile)
echo "GET_LOGIC_VERSION_NUMBER"

############### DAC Commands #######################

# Set the offset DAC code. (0 to 65536-1) 32768 is mid-range.
echo "DAC_CODE 40000"

############### PT SENSE Commands ################

############### ADC Commands #######################

# High performance mode
# 0: do not use high performance mode
# 3: use high performance mode (best for >230MSPS)
echo "ADC_HI_PERF_MODE 3"

############### ADC FIFO (AF) Commands ########################

# Set PRE_CONFIG (determines the number of samples stored before TOT)
# 0:  64 samples of pre-trigger data
# 1:  16 samples of pre-trigger data
# 2:  32 samples of pre-trigger data
# 3:  64 samples of pre-trigger data
# 4: 128 samples of pre-trigger data
echo "AF_SET_PRE_CONFIG 1"

# Set the length of fixed length records (requires AF_SET_CNST_RUN=1)
# 0: Collect 256 samples 
# >0: collect pretrigger length + 4x data argument, up to 8000 samples total
echo "AF_SET_CNST_CONFIG 0"

############### Trigger and Pipeline (TAP) Commands #######################

# Disable the trigger (disable trigger prior to setting up trigger parameters)
echo "TAP_SET_TRIG_EN 0"

# Disable the "less than" trigger
# echo "TAP_SET_LT 0"
# Enable the "less than" trigger
# echo "TAP_SET_LT 1"

echo "TAP_SET_GT 1"

# Set the relative trigger threshold (number of LSBs above or below baseline)
echo "TAP_SET_THR 999"

# Detects baseline for relative trigger threshold
# Takes average of a test run (256 samples by default) and adjusts
# all thresholds by that amount
echo "BASELINE_ADJUST"

# Prints what the current baseline is
echo "TAP_GET_BASELINE"

# Enable the threshold-based trigger
echo "TAP_SET_TRIG_EN 1"

# Length of Test run
echo "AF_SET_TEST_CONFIG 300"

############### HVS Commands #######################

# Set the HVS enable bit
# 0: Disable HV output
# 1: Enable HV output
echo "HVS_ENABLE 0"

# Set the HVS DAC code (controls HV output level. Range 0-65535 = roughly 0-2000V)
# echo "HVS_DAC_CODE 31000"

# Read the HVS ADC code (monitors HV output level.  Range 0-65535. Code = ~26.2 x HV)
# echo "HVS_ADC_READ"

# End a command sequence with this so that the NIOS-2 can go back to polling for ADC data.
echo "END"
