import io
import math
from typing import Any, Dict, List, Tuple
import numpy as np
from PIL import Image as PILImage, ImageOps
import cv2
from sklearn.cluster import MiniBatchKMeans
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern


class DescriptorEngineError(Exception):
    """Base exception for descriptor extraction engine."""
    pass


class InvalidImageStreamError(DescriptorEngineError):
    """Raised when image bytes are empty, invalid, or corrupted."""
    pass


class UnsupportedFeatureTypeError(DescriptorEngineError):
    """Raised when an unrecognized feature_type is requested."""
    pass


SUPPORTED_FEATURE_TYPES = {
    "color_histogram",
    "color_moments",
    "dominant_colors",
    "glcm",
    "lbp_histogram",
}

EXTRACTOR_VERSION = "1.0.0"


class DescriptorEngine:
    """
    Stateless extraction engine for visual descriptors.
    Converts raw image bytes into canonical feature dictionaries and vector representations.
    """

    @staticmethod
    def decode_image_rgb(image_bytes: bytes) -> np.ndarray:
        """
        Decodes raw image bytes into an RGB uint8 NumPy array with EXIF orientation corrected.
        """
        if not image_bytes:
            raise InvalidImageStreamError("Image bytes cannot be empty.")

        try:
            with PILImage.open(io.BytesIO(image_bytes)) as img:
                transposed = ImageOps.exif_transpose(img)
                working_img = transposed if transposed is not None else img
                rgb_img = working_img.convert("RGB")
                arr = np.array(rgb_img, dtype=np.uint8)
                if arr.size == 0 or arr.ndim != 3 or arr.shape[2] != 3:
                    raise InvalidImageStreamError("Decoded image array is invalid.")
                return arr
        except Exception as exc:
            raise InvalidImageStreamError(f"Failed to decode image data: {exc}") from exc

    @classmethod
    def extract_color_histogram(cls, rgb_arr: np.ndarray) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Extracts 768-D L1-normalized HSV color histogram (H=256, S=256, V=256).
        """
        resized = cv2.resize(rgb_arr, (256, 256), interpolation=cv2.INTER_AREA)
        hsv = cv2.cvtColor(resized, cv2.COLOR_RGB2HSV)

        # In OpenCV: H in [0, 180), S in [0, 256), V in [0, 256)
        hist_h = cv2.calcHist([hsv], [0], None, [256], [0, 180]).flatten()
        hist_s = cv2.calcHist([hsv], [1], None, [256], [0, 256]).flatten()
        hist_v = cv2.calcHist([hsv], [2], None, [256], [0, 256]).flatten()

        # L1-normalize each channel so each sums to 1.0
        sum_h = float(hist_h.sum()) or 1.0
        sum_s = float(hist_s.sum()) or 1.0
        sum_v = float(hist_v.sum()) or 1.0

        norm_h = [round(float(v / sum_h), 6) for v in hist_h]
        norm_s = [round(float(v / sum_s), 6) for v in hist_s]
        norm_v = [round(float(v / sum_v), 6) for v in hist_v]

        vector = norm_h + norm_s + norm_v

        parameters = {
            "color_space": "HSV",
            "bins": {"h": 256, "s": 256, "v": 256},
            "normalization": "L1",
        }
        feature_values = {
            "channels": {
                "h": norm_h,
                "s": norm_s,
                "v": norm_v,
            },
            "vector": vector,
        }
        return parameters, feature_values

    @classmethod
    def extract_color_moments(cls, rgb_arr: np.ndarray) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Extracts first 3 color moments (mean, std, skewness) per channel in normalized HSV [0, 1].
        9-D vector output.
        """
        hsv = cv2.cvtColor(rgb_arr, cv2.COLOR_RGB2HSV).astype(np.float64)

        # Normalize to [0, 1]
        hsv[:, :, 0] /= 179.0
        hsv[:, :, 1] /= 255.0
        hsv[:, :, 2] /= 255.0

        channels_data: Dict[str, Dict[str, float]] = {}
        vector: List[float] = []

        for idx, ch_name in enumerate(["h", "s", "v"]):
            channel = hsv[:, :, idx]
            mean_val = float(np.mean(channel))
            std_val = float(np.std(channel))

            # 3rd central moment (Stricker & Orengo sign-preserving cube root)
            diff = channel - mean_val
            m3 = float(np.mean(diff ** 3))
            skew_val = float(np.sign(m3) * (abs(m3) ** (1.0 / 3.0)))

            mean_r = round(mean_val, 4)
            std_r = round(std_val, 4)
            skew_r = round(skew_val, 4)

            channels_data[ch_name] = {
                "mean": mean_r,
                "std": std_r,
                "skewness": skew_r,
            }
            vector.extend([mean_r, std_r, skew_r])

        parameters = {
            "color_space": "HSV",
            "moments": ["mean", "std", "skewness"],
        }
        feature_values = {
            "channels": channels_data,
            "vector": vector,
        }
        return parameters, feature_values

    @classmethod
    def extract_dominant_colors(cls, rgb_arr: np.ndarray, k: int = 5) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Extracts top k dominant colors in RGB using MiniBatchKMeans clustering.
        """
        downsampled = cv2.resize(rgb_arr, (128, 128), interpolation=cv2.INTER_AREA)
        pixels = downsampled.reshape(-1, 3).astype(np.float64)
        sample_size = len(pixels)

        # Run MiniBatchKMeans with fixed seed for deterministic indexing
        kmeans = MiniBatchKMeans(n_clusters=k, random_state=42, batch_size=2048, n_init=3)
        labels = kmeans.fit_predict(pixels)
        centers = kmeans.cluster_centers_

        counts = np.bincount(labels, minlength=k)
        total = float(sample_size)

        # Sort clusters by descending weight/count
        sorted_indices = np.argsort(-counts)

        clusters: List[Dict[str, Any]] = []
        vector: List[float] = []

        for rank, idx in enumerate(sorted_indices, start=1):
            center = centers[idx]
            r = int(np.clip(round(center[0]), 0, 255))
            g = int(np.clip(round(center[1]), 0, 255))
            b = int(np.clip(round(center[2]), 0, 255))

            hex_code = f"#{r:02X}{g:02X}{b:02X}"
            pct = round(float(counts[idx] / total) * 100.0, 1)

            clusters.append({
                "rank": rank,
                "rgb": [r, g, b],
                "hex": hex_code,
                "percentage": pct,
            })

            # Vector component: normalized r, g, b, and weight
            vector.extend([
                round(r / 255.0, 4),
                round(g / 255.0, 4),
                round(b / 255.0, 4),
                round(pct / 100.0, 4),
            ])

        parameters = {
            "k": k,
            "color_space": "RGB",
            "sample_size": sample_size,
        }
        feature_values = {
            "clusters": clusters,
            "vector": vector,
        }
        return parameters, feature_values

    @classmethod
    def extract_glcm(cls, rgb_arr: np.ndarray, levels: int = 32) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Extracts Gray-Level Co-occurrence Matrix (GLCM) texture metrics across 4 angles (0°, 45°, 90°, 135°).
        Summary metrics (contrast, correlation, energy, homogeneity) form the 4-D vector.
        """
        gray = cv2.cvtColor(rgb_arr, cv2.COLOR_RGB2GRAY)
        # Quantize from 256 to 32 levels: [0..31]
        step = 256 // levels
        quantized = (gray // step).astype(np.uint8)
        quantized = np.clip(quantized, 0, levels - 1)

        angles_rad = [0.0, np.pi / 4.0, np.pi / 2.0, 3.0 * np.pi / 4.0]
        angle_keys = ["0", "45", "90", "135"]

        glcm = graycomatrix(
            quantized,
            distances=[1],
            angles=angles_rad,
            levels=levels,
            symmetric=True,
            normed=True,
        )

        contrasts = graycoprops(glcm, "contrast")[0]
        correlations = graycoprops(glcm, "correlation")[0]
        energies = graycoprops(glcm, "energy")[0]
        homogeneities = graycoprops(glcm, "homogeneity")[0]

        by_angle: Dict[str, Dict[str, float]] = {}
        for idx, key in enumerate(angle_keys):
            by_angle[key] = {
                "contrast": round(float(contrasts[idx]), 4),
                "correlation": round(float(correlations[idx]), 4) if not math.isnan(correlations[idx]) else 0.0,
                "energy": round(float(energies[idx]), 4),
                "homogeneity": round(float(homogeneities[idx]), 4),
            }

        mean_contrast = round(float(np.mean(contrasts)), 4)
        mean_correlation = round(float(np.nanmean(correlations)), 4) if not np.all(np.isnan(correlations)) else 0.0
        mean_energy = round(float(np.mean(energies)), 4)
        mean_homogeneity = round(float(np.mean(homogeneities)), 4)

        summary = {
            "contrast": mean_contrast,
            "correlation": mean_correlation,
            "energy": mean_energy,
            "homogeneity": mean_homogeneity,
        }
        vector = [mean_contrast, mean_correlation, mean_energy, mean_homogeneity]

        parameters = {
            "levels": levels,
            "distances": [1],
            "angles_deg": [0, 45, 90, 135],
        }
        feature_values = {
            "summary": summary,
            "by_angle": by_angle,
            "vector": vector,
        }
        return parameters, feature_values

    @classmethod
    def extract_lbp_histogram(cls, rgb_arr: np.ndarray, p: int = 8, r: int = 1) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Extracts 256-bin L1-normalized Local Binary Pattern (LBP) standard histogram (P=8, R=1).
        """
        resized = cv2.resize(rgb_arr, (256, 256), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)

        lbp = local_binary_pattern(gray, P=p, R=r, method="default")

        # In standard mode with P=8, outputs are integers in [0..255] (256 bins)
        hist, _ = np.histogram(lbp.ravel(), bins=256, range=(0, 256))
        sum_hist = float(hist.sum()) or 1.0
        norm_bins = [round(float(v / sum_hist), 6) for v in hist]

        labels = [str(i) for i in range(256)]

        parameters = {
            "P": p,
            "R": r,
            "method": "default",
            "bins": 256,
        }
        feature_values = {
            "bins": norm_bins,
            "labels": labels,
            "vector": norm_bins,
        }
        return parameters, feature_values

    @classmethod
    def extract(cls, image_bytes: bytes, feature_types: List[str] | None = None) -> Dict[str, Tuple[Dict[str, Any], Dict[str, Any]]]:
        """
        Decodes image bytes once and extracts all requested features.
        Returns a dict mapping feature_type -> (parameters, feature_values).
        """
        requested = list(feature_types) if feature_types else sorted(list(SUPPORTED_FEATURE_TYPES))

        for ft in requested:
            if ft not in SUPPORTED_FEATURE_TYPES:
                raise UnsupportedFeatureTypeError(
                    f"Unsupported feature type '{ft}'. Supported: {', '.join(sorted(SUPPORTED_FEATURE_TYPES))}"
                )

        rgb_arr = cls.decode_image_rgb(image_bytes)
        results: Dict[str, Tuple[Dict[str, Any], Dict[str, Any]]] = {}

        if "color_histogram" in requested:
            results["color_histogram"] = cls.extract_color_histogram(rgb_arr)
        if "color_moments" in requested:
            results["color_moments"] = cls.extract_color_moments(rgb_arr)
        if "dominant_colors" in requested:
            results["dominant_colors"] = cls.extract_dominant_colors(rgb_arr)
        if "glcm" in requested:
            results["glcm"] = cls.extract_glcm(rgb_arr)
        if "lbp_histogram" in requested:
            results["lbp_histogram"] = cls.extract_lbp_histogram(rgb_arr)

        return results
