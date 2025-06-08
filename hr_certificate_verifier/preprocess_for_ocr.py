import cv2
import numpy as np

def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = 0
    if len(coords) > 0:
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = image.shape
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        image = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return image

def remove_borders(img, border_value=255):
    # Remove white or black borders from the image
    mask = img != border_value
    coords = np.argwhere(mask)
    if coords.size == 0:
        return img
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1
    cropped = img[y0:y1, x0:x1]
    return cropped

def preprocess_for_ocr(img):
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Aggressive denoising
    gray = cv2.fastNlMeansDenoising(gray, h=50)
    # Resize if too small
    h, w = gray.shape
    if w < 1000:
        scale = 1000 / w
        gray = cv2.resize(gray, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    # Contrast enhancement (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    # Sharpen
    kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
    gray = cv2.filter2D(gray, -1, kernel)
    # Try both adaptive and Otsu's thresholding
    adaptive = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
    )
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # Morphological closing
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    adaptive_closed = cv2.morphologyEx(adaptive, cv2.MORPH_CLOSE, kernel)
    otsu_closed = cv2.morphologyEx(otsu, cv2.MORPH_CLOSE, kernel)
    # Auto-invert if background is dark
    def auto_invert(img):
        if np.mean(img) < 127:
            return cv2.bitwise_not(img)
        return img
    adaptive_closed = auto_invert(adaptive_closed)
    otsu_closed = auto_invert(otsu_closed)
    # Remove borders
    adaptive_cropped = remove_borders(adaptive_closed)
    otsu_cropped = remove_borders(otsu_closed)
    # Deskew
    adaptive_final = deskew(adaptive_cropped)
    otsu_final = deskew(otsu_cropped)
    # Choose the one with more detected text (non-white pixels)
    if np.count_nonzero(adaptive_final < 200) > np.count_nonzero(otsu_final < 200):
        return adaptive_final
    else:
        return otsu_final
