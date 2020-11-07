import gc

import numpy

from dexp.processing.backends.backend import Backend
from dexp.processing.backends.numpy_backend import NumpyBackend


def lipschitz_continuity_correction(backend: Backend,
                                    image,
                                    num_iterations: int = 2,
                                    correction_percentile: float = 0.1,
                                    lipschitz: float = 0.1,
                                    max_proportion_corrected: float = 1,
                                    decimation: int = 8,
                                    internal_dtype=numpy.float16
                                    ):
    """
    'Lipshitz continuity correction'

    'Broken' pixels on detectors typically blink or are very dim or very bright, in any case they are 'out of context'.
    In many cases they will locally break Lipshitz continuity implied by diffraction limited imaging. Here is a simple
    greedy scheme that starts with the  ost infringing voxels and incrementally filters them using local median filtering.


    Parameters
    ----------

    backend : backend to use (numpy, cupy, ...)
    image : image to correct
    num_iterations : number of iterations
    correction_percentile : percentile of pixels to correct per iteration
    lipschitz : lipschitz continuity constant
    max_proportion_corrected : max proportion of pixels to correct overall
    decimation : decimation for speeding up percentile computation
    internal_dtype : internal dtype

    Returns
    -------
    Lipschitz corrected image

    """
    xp = backend.get_xp_module()

    if type(backend) is NumpyBackend:
        internal_dtype = numpy.float32

    original_dtype = image.dtype
    image = backend.to_backend(image, dtype=internal_dtype, force_copy=True)

    total_number_of_corrections = 0

    for i in range(num_iterations):
        print(f"Iteration {i}")
        # TODO: it is slow to recompute the median filter at each iteration,
        # could be done only once but that's less accurate..
        median, error = _compute_error(backend, image, decimation, lipschitz, internal_dtype)
        gc.collect()
        threshold = xp.percentile(
            error.ravel()[::decimation], q=100 * (1 - correction_percentile)
        )

        mask = error > threshold

        num_corrections = xp.sum(mask)
        print(f"Number of corrections: {num_corrections}")

        if num_corrections == 0:
            break

        proportion = (
                             num_corrections + total_number_of_corrections
                     ) / image.size
        print(
            f"Proportion of corrected pixels: {int(proportion * 100)}% (up to now), versus maximum: {int(max_proportion_corrected * 100)}%) "
        )

        if proportion > max_proportion_corrected:
            break

        image[mask] = median[mask]

        total_number_of_corrections += num_corrections

        gc.collect()

    array = image.astype(original_dtype, copy=False)

    return array


def _compute_error(backend: Backend, array, decimation: int, lipschitz: float, dtype=numpy.float16):
    sp = backend.get_sp_module()
    xp = backend.get_xp_module()
    array = backend.to_backend(array, dtype=dtype)
    # we compute the error map:
    median = sp.ndimage.filters.median_filter(array, size=3)
    error = median.copy()
    error -= array
    xp.abs(error, out=error)
    xp.maximum(error, lipschitz, out=error)
    error -= lipschitz
    return median, error
