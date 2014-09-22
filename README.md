# Workflow System Benchmarks
This repository contains support code for running benchmarks of multiple
workflow systems, including PTero.  The benchmarks are intended to compare
systems based on performance using constrained resources.  They are designed to
run on the same base VM image with the same number of virtual CPUs and same
amount of RAM.

## Benchmarks
There are 2 primary axes for the benchmarks:

1. The number of steps in a workflow.
2. The number of concurrent workflows being processed.

The tertiary axis of interest is how parallel the workflows are.  This axis is
treated discretely, such that all steps in a workflow are parallel or serial.

Based on these axes, the simplest interesting benchmarks are:

- The wall clock time required for a single parallel workflow to finish as a
  function of the number of steps.
- The wall clock time required for a set of concurrent, parallel workflows with
  a particular number of steps to finish as a function of the number of
  workflows.
- The wall clock time required for a single serial workflow to finish as a
  function of the number of steps.
- The wall clock time required for a set of concurrent, serial workflows with a
  particular number of steps to finish as a function of the number of
  workflows.

The work performed by each step in a workflow should be pluggable.  We should
include at least two implementations of that work:

1. `sleep` - should sleep for a duration determined by its input
2. `spin` - should `NOP` loop for a number of times determined by its input
