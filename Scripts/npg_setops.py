# -*- coding: utf-8 -*-
"""
=====
ndset
=====

Script :   ndset.py

Author :   Dan_Patterson@carleton.ca

Modified : 2020-10-11

Purpose :

This set of functions is largely directed to extending some of numpy set
functions to apply to Nxd shaped arrays as well as structured and recarrays.
The functionality largely depends on using a `view` of the input array so that
each row can be treated as a unique record in the array.

If you are working with arrays and wish to perform functions on certain columns
then you will have to preprocess/preselect.  You can only add so much to a
function before it loses its readability and utility.

ndset::

    _view_as_struct_, is_in, nd_diff, nd_diffxor, nd_intersect,
    nd_union, nd_uniq

Notes
-----
_view_as_struct_(a)
    >>> a = np.array([[  0,   0], [  0, 100], [100, 100]])
    >>> _view_as_struct_(a)
    ... array([[(  0,   0)],
    ...        [(  0, 100)],
    ...        [(100, 100)]], dtype=[('f0', '<i4'), ('f1', '<i4')])

is_in
    >>> a = np.array([[  0,   0], [  0, 100], [100, 100]])
    >>> look_for = np.array([[  0, 100], [100, 100]])
    >>> is_in(a, look_for, reverse=False)
    array([[  0, 100],
    ...    [100, 100]])
    >>> is_in(a, look_for, reverse=True)
    array([[0, 0]])

For the following:
    >>> a = np.array([[  0,   0], [  0, 100], [100, 100]])
    >>> b = np.array([[  0, 100], [100, 100]])
    >>> c = np.array([[ 20, 20], [100, 20], [100, 0], [ 0, 0]])

nd_diff(a, b)
    >>> nd_diff(a, b)
    array([[0, 0]])

nd_diffxor(a, b, uni=False)
    >>> nd_diffxor(a, c, uni=False)
    array([[  0, 100],
           [ 20,  20],
           [100,   0],
           [100,  20],
           [100, 100]])

nd_intersect(a, b, invert=False)
    >>> nd_intersect(a, b, invert=False)
    array([[  0, 100],
           [100, 100]])
    >>> nd_intersect(a, c, invert=False)
    array([[0, 0]])

nd_union(a, b)
    >>> nd_union(a, c)
    array([[  0,   0],
           [  0, 100],
           [ 20,  20],
           [100,   0],
           [100,  20],
           [100, 100]])

nd_uniq(a, counts=False)
    >>> d = np.array([[ 0, 0], [100, 100], [100, 100], [ 0, 0]])
    nd_uniq(d)
    array([[  0,   0],
           [100, 100]])

References
----------
`<https://community.esri.com/blogs/dan_patterson/2016/10/23/numpy-lessons-5-
identical-duplicate-unique-different>`_.

`<https://github.com/numpy/numpy/blob/master/numpy/lib/arraysetops.py>`_.

"""
# pylint: disable=C0103
# pylint: disable=R1710
# pylint: disable=R0914

import sys
import numpy as np


ft = {'bool': lambda x: repr(x.astype(np.int32)),
      'float_kind': '{: 0.3f}'.format}
np.set_printoptions(edgeitems=10, linewidth=80, precision=2, suppress=True,
                    threshold=100, formatter=ft)
np.ma.masked_print_option.set_display('-')  # change to a single -

script = sys.argv[0]  # print this should you need to locate the script


__all__ = ['_view_as_struct_',
           '_check_dtype_',
           '_unique1d_',
           'nd_diff',
           'nd_diffxor',
           'nd_intersect',
           'nd_isin',
           'nd_merge',
           'nd_union',
           'nd_uniq'
           ]


def _view_as_struct_(a, return_all=False):
    """Key function to get uniform 2d arrays to be viewed as structured arrays.
    A bit of trickery, but it works for all set-like functionality

    Parameters
    ----------
    a : array
        Geo array or ndarray to be viewed.

    Returns
    -------
    Array view as structured/recarray, with shape = (N, 1)

    See main documentation under ``Notes``.
    """
    if not isinstance(a, np.ndarray) or a.dtype.kind in ('O', 'V'):
        print("\nA 2D ndarray is required as input.")
        return None
    shp = a.shape
    dt = a.dtype
    a_view = a.view(dt.descr * shp[1])
    if return_all:
        return a_view, shp, dt
    return a_view


def _unique1d_(ar, return_index=False, return_inverse=False,
               return_counts=False):
    """Return unique array elements. From `np.lib.arraysetops`."""
    ar = np.asanyarray(ar).flatten()
    any_indices = return_index or return_inverse
    if any_indices:
        p = ar.argsort(kind='mergesort' if return_index else 'quicksort')
        aux = ar[p]
    else:
        ar.sort()
        aux = ar
    mask = np.empty(aux.shape, dtype=np.bool_)
    mask[:1] = True
    mask[1:] = aux[1:] != aux[:-1]
    ret = (aux[mask],)
    if return_index:
        ret += (p[mask],)
    if return_inverse:
        imask = np.cumsum(mask) - 1
        inv_idx = np.empty(mask.shape, dtype=np.intp)
        inv_idx[p] = imask
        ret += (inv_idx,)
    if return_counts:
        idx = np.concatenate(np.nonzero(mask) + ([mask.size],))
        ret += (np.diff(idx),)
    return ret


def _check_dtype_(a_view, b_view):
    """Check for equivalency in the dtypes.  If they are not equal, flag and
    return True or False.
    """
    err = "\nData types are not equal, function failed.\n1. {}\n2. {}"
    adtype = a_view.dtype.descr
    bdtype = b_view.dtype.descr
    if adtype != bdtype:
        print(err.format(adtype, bdtype))
        return False
    return True


def nd_diff(a, b, invert=True):
    """See nd_intersect.  This just returns the opposite/difference."""
    return nd_intersect(a, b, invert=invert)


def nd_diffxor(a, b, uni=False):
    """Use setxor... it is slower than nd_diff, 36 microseconds vs 18.2
    but this is faster for large sets
    """
    a_view = _view_as_struct_(a, return_all=False)
    b_view = _view_as_struct_(b, return_all=False)
    good = _check_dtype_(a_view, b_view)  # check dtypes
    if not good:
        return None
    ab = np.setxor1d(a_view, b_view, assume_unique=uni)
    return ab.view(a.dtype).reshape(-1, ab.shape[0]).squeeze()


def nd_in1d(a):
    """Check for the presence of array in the other."""
    pass


def nd_intersect(a, b, invert=False):
    """Intersect two, 2D arrays using views and in1d.

    Parameters
    ----------
    a, b : arrays
        Arrays are assumed to have a shape = (N, 2)

    References
    ----------
    `<https://github.com/numpy/numpy/blob/master/numpy/lib/arraysetops.py>`_.

    `<https://stackoverflow.com/questions/9269681/intersection-of-2d-
    numpy-ndarrays>`_.

    `<https://stackoverflow.com/questions/8317022/get-intersecting-rows-
    across-two-2d-numpy-arrays>`_.
    """
    a_view = _view_as_struct_(a, return_all=False)
    b_view = _view_as_struct_(b, return_all=False)
    good = _check_dtype_(a_view, b_view)  # check dtypes
    if not good:
        return None
    if len(a) > len(b):
        idx = np.in1d(a_view, b_view, assume_unique=False, invert=invert)
        return a[idx]
    else:
        idx = np.in1d(b_view, a_view, assume_unique=False, invert=invert)
        return b[idx]


def nd_isin(a, look_for, reverse=False):
    """Check array `a` for the presence of records in array `look_for`.

    Parameters
    ----------
    arr : array
        The array to check for the elements
    look_for : number, list or array
        what to use for the good
    reverse : boolean
        Switch the query look_for to `True` to find those not in `a`
    """
    a_view = _view_as_struct_(a, return_all=False)
    b_view = _view_as_struct_(look_for, return_all=False)
    good = _check_dtype_(a_view, b_view)  # check dtypes
    if not good:
        return None
    inv = False
    if reverse:
        inv = True
    idx = np.in1d(a_view, b_view, assume_unique=False, invert=inv)
    return a[idx]


def nd_merge(a, b):
    """Merge views of 2 ndarrays or recarrays.  Duplicates are not removed, use
    nd_union instead.
    """
    ab = None
    if (a.dtype.kind in ('f', 'i')) and (b.dtype.kind in ('f', 'i')):
        ab = np.concatenate((a, b), axis=0)
    else:
        a_view = _view_as_struct_(a, return_all=False)
        b_view = _view_as_struct_(b, return_all=False)
        good = _check_dtype_(a_view, b_view)  # check dtypes
        if good:
            ab = np.concatenate((a_view, b_view), axis=None)
            ab = ab.view(a.dtype).reshape(-1, ab.shape[0]).squeeze()
    return ab


def nd_union(a, b):
    """Union views of arrays.

    Return the unique, sorted array of values that are in either of the two
    input arrays.
    """
    a_view = _view_as_struct_(a, return_all=False)
    b_view = _view_as_struct_(b, return_all=False)
    good = _check_dtype_(a_view, b_view)  # check dtypes
    if not good:
        return None
    ab = np.union1d(a_view, b_view)
#    ab = np.unique(np.concatenate((a_view, b_view), axis=None))
    return ab.view(a.dtype).reshape(ab.shape[0], -1).squeeze()


def nd_uniq(a, return_index=False,
            return_inverse=False,
            return_counts=False,
            axis=None):
    """Taken from, but modified for Geo arrays.

    Parameters
    ----------
    a : Geo array or ndarray
        For other array_like objects, see `unique` and `_unique1d` in:

    `<https://github.com/numpy/numpy/blob/master/numpy/lib/arraysetops.py>`_.
    """
    def reshape_uniq(uniq, shp, dt, axis):
        n = len(uniq)
        uniq = uniq.view(dt)
        uniq = uniq.reshape(n, *shp[1:])
        uniq = np.moveaxis(uniq, 0, axis)
        return uniq
    # ----
    if hasattr(a, "IFT"):
        a_view, shp, dt = _view_as_struct_(a.XY, return_all=True)
        out = _unique1d_(a_view, return_index, return_inverse, return_counts)
        out = (reshape_uniq(out[0], shp, dt, axis=0),) + out[1:]
        if len(out) == 1:
            return out[0]
        return out
    else:
        return np.unique(a, return_index, return_inverse, return_counts)


# ----------------------------------------------------------------------
# __main__ .... code section
if __name__ == "__main__":
    # print the script source name.
    print("Script... {}".format(script))
