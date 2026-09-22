#!/usr/bin/env python3

#
# python3 e2e_test.py ../build/src/tio --verbose
#
#

import sys

from _test_runner import run_tests
from test_expect import EXPECT_TESTS
from test_hook import HOOK_TESTS


def main():
    run_tests(HOOK_TESTS + EXPECT_TESTS)


if __name__ == "__main__":
    main()
