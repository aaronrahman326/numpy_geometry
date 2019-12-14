# -*- coding: utf-8 -*-
r"""\

npg_helpers
-----------

Script :
    npg_helpers.py

Author :
    Dan_Patterson@carleton.ca

Modified :
    2019-12-12

Purpose
-------
Helper functions for npgeom.

Notes
-----
None

References
----------
None
"""
# pylint: disable=C0103  # invalid-name
# pylint: disable=R0914  # Too many local variables
# pylint: disable=R1710  # inconsistent-return-statements
# pylint: disable=W0105  # string statement has no effect

import sys
# from textwrap import dedent

import numpy as np


def compare_2d(arr, look_for, unique=True, invert=False, return_idx=False):
    """Look for duplicates in two 2D arrays.

    ** can use to find duplicates between 2 arrays ie compare_arrays **

    Parameters
    ----------
    arr : array, 2D
        The main array, preferably the larger of the two.
    look_for : array, 2D
        The array to compare with.

    Returns
    -------
    The intersection or difference in both arrays, depending on ``invert``.
    The indices of where the objects were found

    >>> a = np.array([[ 5.,  5.], [ 6.,  6.], [10., 10.], [12., 12.]])
    >>> b = np.array([[ 6.,  6.], [12., 12.]])

    >>> compare_2d(a, b, invert=False)
    ... array([[ 6.,  6.],
    ...        [12., 12.]])

    >>> compare_2d(a, b, invert=True)
    ... array([[ 5.,  5.],
    ...        [10., 10.]])
    """
    result = (arr[:, None] == look_for).all(-1).any(-1)
    if sum(result) == 0:
        return None
    if invert:
        result = ~result
    idx = np.where(result)[0]
    out = arr[result]
    if unique:
        out = np.unique(out, axis=0)
    if return_idx:
        return out, idx
    return out


def keep_points(arr, look_for, **kwargs):
    """Keep points in ``arr`` that match those in ``look_for``.

    See ``compare_2d``
    """
    return compare_2d(arr, look_for, invert=False, return_idx=False)


def remove_points(arr, look_for, **kwargs):
    """Remove points from ``arr`` that match those in ``look_for``."""
    return compare_2d(arr, look_for, invert=True, return_idx=False)


script = sys.argv[0]  # print this should you need to locate the script
# ===========================================================================
# ---- main section
if __name__ == "__main__":
    """optional location for parameters"""
    in_fc = r"C:\Git_Dan\npgeom\npgeom.gdb\Polygons"
    in_fc = r"C:\Git_Dan\npgeom\npgeom.gdb\Polygons2"
