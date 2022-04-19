import streamlit as st
from src.encoder import Encoder


def local_css():
    with open("css/style.css") as f:
        st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)


def main():

    st.set_page_config(
        page_title="Avalanche Ring Generator",
        page_icon="img/favicon.png",
        layout="centered",
    )

    local_css()

    txt = st.text_input("", value="19292390")
    st.markdown("Enter any text to encode")

    _, col, _ = st.columns([1, 3, 3])

    with col:
        encoder = Encoder()
        if encoder.exceed_datasize(txt):
            st.warning("Text sequence is too long!")
        else:
            encoder.map(txt)
            img = encoder.plot(streamlit=True)
            st.markdown("#")
            st.image(img, use_column_width=False, width=500)

    st.markdown("#")

    st.markdown(
        """
            ```python

            import cv2
            import numpy as np
            from matplotlib import pyplot as plt
            from dataclasses import dataclass, asdict

            from src.utils import str_to_array_bits, opening


            class EncodingError(Exception):
                pass


            @dataclass
            class Encoder:

                module_size_pixels: int = 8 * 10
                min_radius_pixels: int = 80 * 10
                max_radius_pixels: int = 160 * 10

                def map(self, data):

                    data = str(data)
                    array_bits = str_to_array_bits(data)

                    self.set_params(array_bits)

                    self.encoding = np.full(
                        (self.number_of_circle, self.module_per_circle), 255, dtype=np.uint8)
                    self.add_vertical_zebras()
                    self.add_radial_zebras()
                    self.add_inner_circles()
                    self.add_data(array_bits)

                    return self.encoding

                def add_vertical_zebras(self):
                    N = self.encoding.shape[0]
                    self.encoding[:, 0] = 0
                    self.encoding[:, 1] = 255
                    self.encoding[:, 2] = ([255, 0] * (int((N)/2) + 1))[:N]
                    self.encoding[:, -1] = 255

                def add_radial_zebras(self):
                    radial_zebra = np.array([0, 255] * int(self.module_per_circle/2))
                    self.encoding = np.vstack([radial_zebra, self.encoding])

                def add_inner_circles(self):
                    marker_ring = np.zeros(self.module_per_circle)
                    indexes_marker = [
                        int(self.module_per_circle/4 * .5),
                        int(self.module_per_circle/4 * 1.5),
                        int(self.module_per_circle/4 * 2.5),
                        int(self.module_per_circle/4 * 3.5),
                    ]
                    for idx in indexes_marker:
                        marker_ring[idx] = 255
                    black_inner_ring = np.zeros(self.module_per_circle)
                    self.encoding = np.vstack([self.encoding, marker_ring])
                    self.encoding = np.vstack([self.encoding, black_inner_ring])

                def add_data(self, array_bits):

                    N, M = self.encoding.shape

                    start_row_encoding = 1
                    end_row_encoding = N - 2

                    start_col_encoding = 3
                    end_col_encoding = M - 2

                    idx, jdx = start_row_encoding, start_col_encoding
                    for bits in array_bits:
                        for bit in bits:
                            if bit == '0':
                                self.encoding[idx][jdx] = 0
                            jdx += 1
                            if jdx > end_col_encoding:
                                raise EncodingError(f"Error: jdx: {jdx}")
                        if end_col_encoding < (jdx + 8):
                            idx += 1
                            jdx = start_col_encoding
                            if idx > end_row_encoding:
                                raise EncodingError(f"Error: idx: {idx}")

                def plot(self, streamlit=False):

                    margin_pixels = 10
                    W = H = 2 * (margin_pixels + self.max_radius_pixels)
                    centroid = (int(H/2), int(W/2))

                    angle_step = 360 / self.module_per_circle
                    all_angles = [angle_step *
                                idx for idx in range(self.module_per_circle)]

                    current_radius_pixels = self.max_radius_pixels
                    current_circle_number = 0

                    img_code = np.full((H, W), 255, dtype=np.uint8)
                    img_code = cv2.ellipse(
                        img_code,
                        center=centroid,
                        axes=(current_radius_pixels, current_radius_pixels),
                        angle=0,
                        color=255,
                        startAngle=0,
                        endAngle=360,
                        thickness=-1,
                    )

                    while current_radius_pixels >= self.min_radius_pixels and current_circle_number < self.encoding.shape[0]:
                        for idx, angle in enumerate(all_angles):
                            next_angle = angle + angle_step
                            color = self.encoding[current_circle_number][idx]
                            if color == 0:
                                cv2.ellipse(
                                    img_code,
                                    center=centroid,
                                    angle=0,
                                    startAngle=angle,
                                    endAngle=next_angle,
                                    axes=(current_radius_pixels, current_radius_pixels),
                                    thickness=-1,
                                    color=0,
                                )

                        current_radius_pixels -= self.module_size_pixels
                        current_circle_number += 1

                        cv2.ellipse(
                            img_code,
                            center=centroid,
                            angle=0,
                            startAngle=0,
                            endAngle=360,
                            axes=(current_radius_pixels, current_radius_pixels),
                            thickness=-1,
                            color=255,
                        )

                    img_code = opening(img_code)

                    figure = plt.figure(figsize=(9, 9))
                    if streamlit:
                        return img_code

                    plt.imshow(img_code, cmap='gray')

                def set_params(self, array_bits):
                    self.min_perimeter_pixels = int(2 * np.pi * self.min_radius_pixels)
                    self.module_per_circle = int(
                        self.min_perimeter_pixels / self.module_size_pixels)
                    self.byte_per_circle = (self.module_per_circle - 4) // 8
                    self.number_of_circle = len(array_bits) // self.byte_per_circle + 1
                    self.max_number_of_circle = int(
                        (self.max_radius_pixels - self.min_radius_pixels) / self.module_size_pixels)

                def get_params(self):
                    return {
                        **asdict(self),
                        "min_perimeter_pixels": self.min_perimeter_pixels,
                        "module_per_circle": self.module_per_circle,
                        "byte_per_circle": self.byte_per_circle,
                        "number_of_circle": self.number_of_circle,
                        "max_number_of_circle": self.max_number_of_circle,
                    }

            ```
            """
    )


if __name__ == "__main__":
    main()
