#!/usr/bin/python
# also supports python3
#
# version 2.0 of this script
#
# is_regression.py - statistical test for performance throughput regression
# based on python scipy.stats.ttest_ind() function
#
# we input two sets of samples: 
#  the baseline sample set -- used as an indication of previously achieved level of performance
#  the current sample set -- used as an indication of the system currently being tested for performance regression
#
# command line inputs:
#  sample_type -- 'throughput' or 'response-time'
#  confidence_threshold -- min probability that two sample sets have a different mean 
#                           (e.g. 95 means that results differ with 95% probability)
#  max_pct_dev -- maximum percent deviation of either sample set, 100.0 x std.dev/mean 
#  regression_threshold -- do not return error status unless regression exceeds this percentage
#  base_sample -- file containing baseline performance throughput samples, 1 per line
#  current_sample -- file containing current performance throughput samples, 1 per line
#
# recommendation: make max_pct_dev 1/2 of regression threshold, so that you can detect small regressions.
#
# return status codes and their meanings are described below in the code.
#  
# we declare a performance regression if base_set mean is worse than current_set mean and a T-test determines
# that the probability that the two sample sets have a different mean is greater than confidence_threshold
#
# the base sample set mean is "worse" than the current sample set mean if and only if:
#   the sample_type is 'throughput'    and the base mean > current mean
#   the sample type is 'response-time' and the base mean < current mean
#
# References: The Art of Computer Systems Perf. Analysis, Raj Jain
# see documentation for python scipy.stats.ttest_ind() function
#
# DEPENDENCIES:
# numpy and scipy RPMs
# for python3, there are python3-{numpy,scipy} RPMs
#

import os
import sys
from sys import argv, exit
import math
import numpy
import scipy
from scipy.stats import ttest_ind
from numpy import array

# process status codes returned to shell
# do not change, regression test and applications use these!

NOTOK=-1                      # fatal error status
PASS = 0                      # declare no regression
FAIL = 10                     # declare regression
VARIANCE_TOO_HIGH=11          # uncertain, sample set variance too high
NOT_ENOUGH_SAMPLES=12         # uncertain, not enough samples to know variance
NO_CONFIDENCE=13              # uncertain, sample sets are too close together

verbose = (os.getenv('VERBOSE') != None)

def usage(msg):
  print('\nERROR: ' + msg)
  print('usage: is_regression.py sample_type confidence_threshold max_pct_dev regression_threshold base_samples_file test_samples_file')
  print('sample_type is either "throughput" or "response-time"')
  print('confidence_threshold is probability that sample means differ expressed as a percentage')
  print('max_pct_dev is maximum percent deviation allowed for either sample set')
  print('regression_threshold -- do not return error status unless regression exceeds this percentage')
  print('samples files are text files with one floating-point sample value per line')
  print('')
  print('prefix command with VERBOSE=1 to obtain more detail on computation')
  sys.exit(NOTOK)

def read_samples_from_file( sample_filepath ):
  with open(sample_filepath, "r") as sample_file:
      samples = [ float(r.strip()) for r in sample_file.readlines() ]
  if verbose:
    print('%d samples read from file %s'%(len(samples), sample_filepath))
    print(samples)
  return array(samples)

def print_sample_stats(samples_name, samples_array):
    s = samples_array
    print('sample stats for %s:\n  count = %d\n  min = %f\n  max = %f\n  mean = %f\n  sd = %f\n  pct.dev. = %5.2f %%'%\
            (samples_name, len(s), s.min(), s.max(), s.mean(), s.std(ddof=1), 100.0*s.std(ddof=1)/s.mean()))

if len(argv) < 7:
  usage('not enough command line arguments')

sample_type = argv[1]
confidence_threshold = float(argv[2])
max_pct_dev = float(argv[3])
regression_threshold = float(argv[4])

# read in and acknowledge command line arguments

print('decision parameters:\n  sample type = %s\n  confidence threshold = %6.2f %%\n  max. pct. deviation = %6.2f %%\n  regression threshold = %6.2f %% '%(sample_type, confidence_threshold, max_pct_dev, regression_threshold))

if sample_type != 'throughput' and sample_type != 'response-time':
  usage('invalid sample type (first parameter)')

baseline_sample_array = read_samples_from_file(argv[5])
print_sample_stats('baseline', baseline_sample_array)

current_sample_array = read_samples_from_file(argv[6])
print_sample_stats('current', current_sample_array)

# reject invalid inputs

if len(current_sample_array) < 3:
  print('ERROR: not enough current samples')
  exit(NOT_ENOUGH_SAMPLES)

if len(baseline_sample_array) < 3:
  print('ERROR: not enough baseline samples')
  exit(NOT_ENOUGH_SAMPLES)

# flunk the test if standard deviation is too high for either sample test

baseline_pct_dev = 100.0 * baseline_sample_array.std(ddof=1) / baseline_sample_array.mean()
current_pct_dev = 100.0 * current_sample_array.std(ddof=1) / current_sample_array.mean()

if baseline_pct_dev > max_pct_dev:
  print('WARNING: pct. deviation of %5.2f is too high for baseline samples'%baseline_pct_dev)
if current_pct_dev > max_pct_dev:
  print('WARNING: pct. deviation of %5.2f is too high for current samples'%current_pct_dev)

pct_change = 100.0*(current_sample_array.mean() - baseline_sample_array.mean())/baseline_sample_array.mean()
if sample_type == 'response-time':
  pct_change *= -1.0
print('current mean improvement over baseline is %5.2f percent'%pct_change)

change_likely = abs(pct_change) - max(baseline_pct_dev,current_pct_dev)
if change_likely > 0.0:
  print('magnitude of change is at least %5.2f%%'%change_likely)
else:
  print('magnitude of change is less than standard deviation of samples')

# FAIL the test if sample sets are accurate enough and 
# current sample set is statistically worse than baseline sample set

(t, same_mean_probability) = ttest_ind(baseline_sample_array, current_sample_array)
print('t-test t-statistic = %f probability = %f'%(t,same_mean_probability))
print('t-test says that mean of two sample sets differs with probability %6.2f%%'%\
        ((1.0-same_mean_probability)*100.0))

pb_threshold = (100.0 - confidence_threshold)/100.0
rg_threshold = (regression_threshold / 100.0) + 1.0

print('probability that sample sets have same mean = %6.4f'%same_mean_probability)
if verbose: print('probability threshold = %6.4f'%pb_threshold)
if same_mean_probability < pb_threshold:
   current_sample_mean = current_sample_array.mean()

   # the two samples do not have the same mean
   # fail if current sample is worse than baseline sample as defined above

   if (sample_type == 'throughput'):
     adjusted_baseline_mean = baseline_sample_array.mean() / rg_threshold
     if verbose: print('current sample mean = %f , adjusted baseline mean = %f'%\
                         (current_sample_mean, adjusted_baseline_mean))
     if adjusted_baseline_mean > current_sample_mean:
       print('declaring a performance regression test FAILURE because of lower throughput')
       exit(FAIL)
   elif (sample_type == 'response-time'):
     adjusted_baseline_mean = baseline_sample_array.mean() * rg_threshold
     if verbose: print('current sample mean = %f , adjusted baseline mean = %f'%\
                         (current_sample_mean, adjusted_baseline_mean))
     if adjusted_baseline_mean < current_sample_mean:
       print('declaring a performance regression test FAILURE because of higher response time')
       exit(FAIL)
   else: 
     usage('sample_type must either be "throughput" or "response-time"')
   if current_sample_mean > baseline_sample_array.mean():
     print('current sample set is statistically better than baseline sample set')
else:
  print('sample sets are statistically indistinguishable for specified confidence level')
  if baseline_pct_dev > max_pct_dev or current_pct_dev > max_pct_dev:
    exit(VARIANCE_TOO_HIGH)
  else:
    exit(NO_CONFIDENCE)
exit(PASS)  # no regression found
