import numpy as np
import pickle
from scipy import ndimage
import pylab


# print(os.path.abspath(os.curdir))


# Forward projection
def forward_projection(image, theta):  # theta
    sinogram = np.zeros((image.shape[1], len(theta)), dtype=np.float32)  # L*W*typelen
    for ind, angle in enumerate(theta):
        rotate_image = ndimage.rotate(image, -angle, reshape=False)
        sinogram[:, ind] = np.sum(rotate_image, axis=0)
    return sinogram


# Backward projection（）
def backprojection(sinogram, theta, zoom_out_scale=1, angle_step=1, projection_step=1):  # , image_size):
    """
    backproject the projections in "sinogram" to image domain
    assuming that the shape of the sinogram is in (number of views, number of projections per view)
    the actual view angle is given in the list "theta"
    input:
        sinogram, an array in shape (number_of_projections_per_view, view_angle)
        theta, a list retaining the actual view angles
        image_size, the size of the images to be reconstructed
    output:
        return an image array with a shape specified by the parameter image_size
    """
    # zoom_out_scale = 1  
    # angle_step = 1  
    # projection_step = 1  
    # count = 0  
    image_data_list = []
    # initialize an image space
    w, h = [int(round(sinogram.shape[0] / zoom_out_scale))] * 2
    image = np.zeros([w, h])
    # origin = [e / 2 for e in image.shape]

    ys, xs = np.mgrid[0:image.shape[0], 0:image.shape[1]]
    ys = np.float64(ys)
    xs = np.float64(xs)
    ys -= (image.shape[0] / 2.)
    xs -= (image.shape[1] / 2.)
    beta = np.arctan2(ys, xs)

    for ind, angle in enumerate(theta[::angle_step]):
        alpha = beta + angle / 180 * np.pi
        ksi = np.cos(alpha) * np.sqrt(xs * xs + ys * ys)
        ksi += (image.shape[1] / 2.)
        # scaling factor
        ksi *= zoom_out_scale
        # projection step
        ksi = np.uint32(np.around(ksi / projection_step, 0) * projection_step)
        ksi[np.where(ksi < 0)] = 0
        #
        ksi[np.where(ksi > sinogram.shape[0] - 1)] = sinogram.shape[0] - 1
        ksi = np.uint32(np.around(ksi, 0))

        slc = sinogram[:, ind * angle_step]
        backp = slc[ksi]

        image += backp

        image_data_list.append(np.copy(image))

        # if count % 10 == 0:
        #     image_data_list.append(np.copy(image))
        # count += 1

    image[image < 0] = 0  # Remove outliers
    image /= len(theta)  # Normalization

    return image, image_data_list


def sinogram_filtering(sinogram, filter_type):
    """
    Apply a filter to the sinogram in the frequency domain.
    :param filter_type:
    :param sinogram: A 2D np array representing the sinogram to be filtered.
    :return: A 2D np array representing the filtered sinogram.
    """
    size = sinogram.shape[0]
    # print(size)
    n = np.concatenate((np.arange(1, size / 2 + 1, 2, dtype=int),
                        np.arange(size / 2 - 1, 0, -2, dtype=int)))
    f = np.zeros(size)
    f[0] = 0.25
    f[1::2] = -1 / (np.pi * n) ** 2
    #    pylab.plot(f)
    #    pylab.show()

    if filter_type == "ramp":
        # Computing the ramp filter from the fourier transform of its
        # frequency domain representation lessens artifacts and removes a
        # small bias
        ftr = 2 * np.real(np.fft.fft(f)).reshape(-1, 1)  # ramp filter

    #        pylab.plot(filter)
    #        pylab.show()
    elif filter_type == "None":
        pass

    sinogram_fft = np.fft.fft(sinogram, axis=0)
    filtered_fft = sinogram_fft * ftr
    filtered_sinogram = np.real(np.fft.ifft(filtered_fft, axis=0))

    return filtered_sinogram


def data_processing(filename):
    fp = open(file=filename, mode='rb')
    array = pickle.load(fp)
    fp.close()
    sinogram = array[1]
    ft_sinogram = sinogram_filtering(sinogram, "ramp")
    image, image_list = backprojection(ft_sinogram, np.arange(360))
    return image, image_list


def image_show(image_list):
    pylab.ion()
    for image_data in image_list:
        pylab.clf()
        pylab.imshow(image_data, cmap='gray')
        pylab.axis('off')
        pylab.pause(0.01)  
    pylab.ioff()
    # pylab.show()
    pylab.close()


def image_package(data, file_pack_path):
    with open(file_pack_path, 'wb') as f:
        pickle.dump(data, f)
    print()


if __name__ == '__main__':
    img, img_list = data_processing("\\data.pkl")
    image_show(img_list)
