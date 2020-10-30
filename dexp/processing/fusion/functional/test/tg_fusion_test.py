import numpy

from dexp.processing.backends.cupy_backend import CupyBackend
from dexp.processing.backends.numpy_backend import NumpyBackend
from dexp.processing.fusion.functional.test.fusion_test_data import generate_fusion_test_data
from dexp.processing.fusion.functional.tg_fusion import fuse_tg_nd


def test_tg_fusion_numpy():
    backend = NumpyBackend()
    tg_fusion(backend)

def test_tg_fusion_cupy():
    try:
        backend = CupyBackend()
        tg_fusion(backend)
    except ModuleNotFoundError:
        print("Cupy module not found! Test passes nevertheless!")


def tg_fusion(backend):
    image_gt, image_lowq, blend_a, blend_b, image1, image2 = generate_fusion_test_data(add_noise=False)
    image_fused = fuse_tg_nd(backend, image1, image2)
    error = numpy.median(numpy.abs(image_gt - image_fused))
    print(error)
    assert error < 23

    from napari import Viewer, gui_qt
    with gui_qt():
        viewer = Viewer()
        viewer.add_image(image_gt, name='image_gt')
        viewer.add_image(image_lowq, name='image_lowq')
        viewer.add_image(blend_a, name='blend_a')
        viewer.add_image(blend_b, name='blend_b')
        viewer.add_image(image1, name='image1')
        viewer.add_image(image2, name='image2')
        viewer.add_image(image_fused, name='image_fused')


