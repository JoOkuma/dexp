import numpy

from dexp.processing.backends.backend import Backend
from dexp.processing.backends.numpy_backend import NumpyBackend


def gaussian_kernel_2d(backend: Backend,
                       size: int = 5,
                       sigma: float = 1.0,
                       dtype=numpy.float16):
    """
    Computes a 2D Gaussian kernel
    Parameters
    ----------
    backend : Backend to use for computation
    size : size in pixels
    sigma : Gaussian sigma
    dtype : dtype for kernel

    Returns
    -------
    2D Gaussian kernel

    """
    xp = backend.get_xp_module()
    ax = xp.linspace(-(size - 1) / 2., (size - 1) / 2., size)
    xx, yy = xp.meshgrid(ax, ax)
    kernel = xp.exp(-0.5 * (xp.square(xx) + xp.square(yy)) / xp.square(sigma))
    kernel /= xp.sum(kernel)
    kernel = kernel.astype(dtype=dtype)
    return kernel


def gaussian_kernel_nd(backend: Backend,
                       ndim: int = 3,
                       size: int = 5,
                       sigma: float = 1.0,
                       dtype=numpy.float16):
    """
    Computes a nD Gaussian kernel
    Parameters
    ----------
    backend : Backend to use for computation
    ndim : number of dimensions
    size : size in pixels
    sigma : Gaussian sigma
    dtype : dtype for kernel

    Returns
    -------
    nD Gaussian kernel

    """
    xp = backend.get_xp_module()
    sp = backend.get_sp_module()

    if type(backend) is NumpyBackend:
        dtype = numpy.float32

    kernel = xp.zeros(shape=(size,) * ndim, dtype=dtype)
    kernel[(slice(size // 2, size // 2 + 1, None),) * ndim] = 1
    kernel = sp.ndimage.gaussian_filter(kernel, sigma=sigma)

    kernel /= xp.sum(kernel)

    return kernel
