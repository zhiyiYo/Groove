import numpy as np
import cv2
from scipy.interpolate import splprep, splev

im = cv2.imread('image1.jpeg')

bk = im.copy()

# Fill background with black color
cv2.floodFill(im, None, seedPoint=(1, 1), newVal=(
    0, 0, 0), loDiff=(5, 5, 5), upDiff=(5, 5, 5))
gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)

ret, thresh_gray = cv2.threshold(gray, 5, 255, cv2.THRESH_BINARY)

# Use "open" morphological operation for removing small contours (noise)
thresh_gray = cv2.morphologyEx(
    thresh_gray, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))

# Background
bk[(thresh_gray > 0)] = 0
bk = cv2.morphologyEx(bk, cv2.MORPH_DILATE,
                      cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20, 20)))
#cv2.imshow('bk', bk)

# Foreground
fg = im.copy()
tmm_fg = cv2.morphologyEx(
    fg, cv2.MORPH_DILATE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20, 20)))
fg_gray = cv2.cvtColor(fg, cv2.COLOR_RGB2GRAY)
fg[(fg_gray == 0)] = tmm_fg[(fg_gray == 0)]


#thresh_gray = cv2.morphologyEx(thresh_gray, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (50,50)));

#Find contours (there is only one contour)
_, contours, _ = cv2.findContours(
    thresh_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
c = contours[0]

# Smooth contour
# https://agniva.me/scipy/2016/10/25/contour-smoothing.html
x, y = c.T
x = x.tolist()[0]
y = y.tolist()[0]
tck, u = splprep([x, y], u=None, s=1.0, per=1)
u_new = np.linspace(u.min(), u.max(), 150)
x_new, y_new = splev(u_new, tck, der=0)
res_array = [[[int(i[0]), int(i[1])]] for i in zip(x_new, y_new)]
smoothened = np.asarray(res_array, dtype=np.int32)

# Build a mask
mask = np.zeros_like(thresh_gray)
cv2.drawContours(mask, [smoothened], -1, 255, -1)

# For testig
test_im = cv2.cvtColor(thresh_gray, cv2.COLOR_GRAY2RGB)
cv2.drawContours(test_im, [smoothened], 0, (0, 255, 0), 1)

res = bk
res[(mask > 0)] = fg[(mask > 0)]

cv2.imshow('test_im', test_im)
cv2.imshow('res', res)
cv2.waitKey(0)
cv2.destroyAllWindows()
