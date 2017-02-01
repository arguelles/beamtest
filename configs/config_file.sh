# /bin/sh
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
echo "TRIG_MODE 1"

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

# Read the pressure (kPa) from the PT sensor
# echo "READ_PRESSURE"

# Read the temperature register (ADC code) from
# the PT sensor. Note that the ADC code is 
# retrieved because the MPL115A1's temperature
# sensor is not calibrated.
# echo "READ_TEMP_REG"

############### ADC Commands #######################

# Low latency disable 
# 0: enable (ADS4149 default)
# 1: disabled (allows test pat, gain, offset corr)
# echo "ADC_DIS_LOW_LATENCY 0"

# Test bit pattern (ADS4149 default=0, use requires ADC_DIS_LOW_LATENCY=1)
# 0: normal operation
# 1: all 0
# 2: all 1
# 3: checker board
# 4: digital ramp
# 5: custom pattern
# echo "ADC_TEST_PAT 0"

# Custom pattern (any 14 bit number is OK, requires ADC_DIS_LOW_LATENCY=1)
# echo "ADC_CUSTOM_PAT 0"

# Enable user-controlled LVDS swing (ADS4149 default=0)
# 0: no LVDS swing control
# 3: allow LVDS swing control 
# echo "ADC_EN_LVDS_SWING 3"

# LVDS swing (ADS4149 default=0)
#  0: +/-350mV with external 100Ohm termination
# 27: +/-410mV with external 100Ohm termination
# 50: +/-465mV with external 100Ohm termination
# 14: +/-570mV with external 100Ohm termination
# 62: +/-200mV with external 100Ohm termination
# 15: +/-125mV with external 100Ohm termination
# echo "ADC_LVDS_SWING 0"

# High performance mode
# 0: do not use high performance mode
# 3: use high performance mode (best for >230MSPS)
echo "ADC_HI_PERF_MODE 3"

# High performance mode 2
# 0: Default mode
# 1: Best reconstruction of high frequency content
# echo "ADC_HI_PERF_MODE_2 0"

# Disable gain (disables internal gain control) 
# 0: Default Mode. Gain mode enabled
# 1: Disable Gain Mode
# echo "ADC_DISABLE_GAIN 0"

# Gain mode (requires ADC_DIS_LOW_LATENCY=1)
#  0: 0.0dB gain (ADS4149 default)
#  1: 0.5dB gain
#  2: 1.0dB gain
#  3: 1.5dB gain
#  4: 2.0dB gain
#  5: 2.5dB gain
#  6: 3.0dB gain
#  7: 3.5dB gain
#  8: 4.0dB gain
#  9: 4.5dB gain
# 10: 5.0dB gain
# 11: 5.5dB gain
# 12: 6.0dB gain
# echo "ADC_GAIN 0"

# LVDS CLKOUT strength
# 0: 100 Ohm external termination (ADS4149 default)
# 1:  50 Ohm external termination
# echo "ADC_LVDS_CLKOUT_STRENGTH 0"

# LVDS DATA strength
# 0: 100 Ohm external termination (ADS4149 default)
# 1:  50 Ohm external termination
# echo "ADC_LVDS_DATA_STRENGTH 0"

# Enable CLKOUT Setup/Hold time adjustment
# 0: Setup/Hold time adjustment for CLKOUT rising edge enabled (ADS4149 default)
# 1: Setup/Hold time adjustment for CLKOUT rising edge disabled
# echo "ADC_EN_CLKOUT_RISE 0" 

# CLKOUT rise POSN: CLKOUT rise control
# 0 (00): (ADS4149 default- timings are as specified in datasheet)
# 1 (01): Setup reduces by 500ps, hold increases by 500ps
# 2 (10): Data transition is aligned with rising edge
# 3 (11): Setup reduces by 200ps, hold increases by 200ps
# echo "ADC_CLKOUT_RISE_POSN 0"

# Enable CLKOUT FALL
# 0: Setup/Hold time adjustment for CLKOUT falling edge enabled (ADS4149 default)
# 1: Setup/Hold time adjustment for CLKOUT falling edge disabled
# echo "ADC_EN_CLKOUT_FALL 0" 

# CLKOUT fall control 
# 00: (ADS4149 default- timings are as specified in datasheet)
# 01: Setup reduced by 400ps, hold increases by 400ps
# 10: Data transition is aligned with rising edge
# 11: Setup reduces by 200ps, hold increases by 200ps
# echo "ADC_CLKOUT_FALL_POSN 0"

# Standby mode (ADC and output buffers powered down 5-25us wakeup time)
# 0: Normal operation (ADS4149 default)
# 1: Standby mode
# echo "ADC_STBY 0"

# Global power down (Put ADC functions to sleep, 100-500us wakeup time)
# 0: Normal operation
# 1: Total power down
# echo "ADC_PDN_GLOBAL 0"

# Power down output buffer
# 0: Normal operation (ADS4149 default)
# 1: Output buffers power down
# echo "ADC_PDN_OBUF 0"

# Enable offset correction (requires ADC_DIS_LOW_LATENCY=1)
# 0: offset correction disabled (ADS4149 default)
# 1: offset correction enabled
# echo "ADC_EN_OFFSET_CORR 1"

# Offset Pedestal 
# 31  (011111):  31LSB
# 30  (011110):  30LSB
# 29  (011101):  29LSB
# ...
#  0  (000000):   0LSB (ADS4149 default)
# ...
# 63: (111111):  -1LSB
# 62: (111110):  -2LSB
# ...
# 32: (100000): -32LSB
# echo "ADC_OFFSET_PEDESTAL 0"

# Freeze offset correction
# 0: Estimation of offset correction is not frozen (ADS4149 default)
# 1: Estimation of offset correction is frozen
# echo "ADC_FREEZE_OFFSET_CORR 0"

# Offset corr time constant
#  0 (0000):    1MSamples  (ADS4149 default)
#  1 (0001):    2MSamples
#  2 (0010):    4MSamples
#  3 (0011):    8MSamples
#  4 (0100):   16MSamples
#  5 (0101):   32MSamples
#  6 (0110):   64MSamples
#  7 (0111):  128MSamples
#  8 (1000):  256MSamples
#  9 (1001):  512MSamples
# 10 (1010): 1   GSamples
# 11 (1011): 2   GSamples 
# echo "ADC_OFFSET_CORR_TIME_CONSTANT 0"

# Low speed mode - good for slower than 80MSPS
# 0, 1, 2: Low speed mode disabled (ADS4149 default)
# 3:       Low speed mode enabled (use for <80MSPS)
# echo "ADC_LOW_SPEED 0"

############### ADC FIFO (AF) Commands ########################

# Clear out the AFs (FIFO clearing function)
# echo "AF_CLEAR"

# Set PRE_CONFIG (determines the number of samples stored before TOT)
# 0:  64 samples of pre-trigger data
# 1:  16 samples of pre-trigger data
# 2:  32 samples of pre-trigger data
# 3:  64 samples of pre-trigger data
# 4: 128 samples of pre-trigger data
echo "AF_SET_PRE_CONFIG 0"

# SET POST_CONFIG (determines the number of samples stored after TOT, requires AF_SET_CNST_RUN=1)
# 0: 256 samples after signal does not meet trigger condition 
# 1:  16 samples after signal does not meet trigger condition 
# 2:  32 samples after signal does not meet trigger condition 
# 3:  64 samples after signal does not meet trigger condition 
# 4: 128 samples after signal does not meet trigger condition 
# 5: 256 samples after signal does not meet trigger condition 
# echo "AF_SET_POST_CONFIG 1"

# Set the test run length (length of records from key1 presses or "metered mode" operation) 
# 0: Collect 256 samples 
# 1 to 2000: Collect 4x's the data argument 
# echo "AF_SET_TEST_CONFIG 0"

# Set the length of fixed length records (requires AF_SET_CNST_RUN=1)
# 0: Collect 256 samples 
# >0: collect pretrigger length + 4x data argument, up to 8000 samples total
echo "AF_SET_CNST_CONFIG 1800"

############### Trigger and Pipeline (TAP) Commands #######################

# Disable the trigger (disable trigger prior to setting up trigger parameters)
echo "TAP_SET_TRIG_EN 0"

# Disable the "greater than" trigger
#echo "TAP_SET_GT 0"
# Enable the "greater than" trigger
# echo "TAP_SET_GT 1"

# Disable the "equal to" trigger
# echo "TAP_SET_ET 0"
# Enable the "equal to" trigger
# echo "TAP_SET_ET 1"

# Disable the "less than" trigger
# echo "TAP_SET_LT 0"
# Enable the "less than" trigger
 echo "TAP_SET_LT 1"

# Set the relative trigger threshold (number of LSBs above or below baseline)
echo "TAP_SET_THR 0"

# Detects baseline for relative trigger threshold
# Takes average of a test run (256 samples by default) and adjusts
# all thresholds by that amount
echo "BASELINE_ADJUST"

# Prints what the current baseline is
echo "TAP_GET_BASELINE"

# Enable the threshold-based trigger
 echo "TAP_SET_TRIG_EN 1"

# Do a test run (sw equivalent of a SoCKit key1 press)
# echo "TAP_TEST_RUN 1"

############### HVS Commands #######################

# Set the HVS enable bit
# 0: Disable HV output
# 1: Enable HV output
echo "HVS_ENABLE 0"

# Set the HVS DAC code (controls HV output level. Range 0-65535 = roughly 0-2000V)
echo "HVS_DAC_CODE 31000"

# Read the HVS ADC code (monitors HV output level.  Range 0-65535. Code = ~26.2 x HV)
echo "HVS_ADC_READ"

# End a command sequence with this so that the NIOS-2 can go back to polling for ADC data.
echo "END"
