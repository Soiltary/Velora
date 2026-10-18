# Third-party software

Velora includes the following independent components. Their licenses are not replaced by the app's license. Original wheel metadata and available license texts are retained under `runtime/Lib/site-packages/*.dist-info/` and package license directories.

| Component | License | Source / upstream |
| --- | --- | --- |
| Python 3.12.10 | Python Software Foundation License | https://www.python.org/downloads/release/python-31210/ |
| PySide6 / Qt 6 / Shiboken | LGPL v3 / GPL v3 / Qt third-party terms | https://code.qt.io/cgit/pyside/pyside-setup.git/ and https://code.qt.io/cgit/qt/ |
| Pillow | HPND (Pillow / PIL license) | https://github.com/python-pillow/Pillow |
| pillow-heif / libheif | BSD-3-Clause wrapper; libheif LGPL and codec licenses | https://github.com/bigcat88/pillow_heif and https://github.com/strukturag/libheif |
| PyMuPDF / MuPDF | GNU AGPL v3 | https://github.com/pymupdf/PyMuPDF and https://mupdf.com/releases/ |
| python-docx | MIT | https://github.com/python-openxml/python-docx |
| openpyxl | MIT | https://foss.heptapod.net/openpyxl/openpyxl |
| lxml | BSD-3-Clause with bundled libxml2 / libxslt notices | https://github.com/lxml/lxml |
| et-xmlfile | MIT | https://foss.heptapod.net/openpyxl/et_xmlfile |
| typing-extensions | PSF-2.0 | https://github.com/python/typing_extensions |
| imageio-ffmpeg | BSD-2-Clause | https://github.com/imageio/imageio-ffmpeg |
| FFmpeg binary and bundled codecs | GPL v3 build; see binary build configuration | https://github.com/imageio/imageio-binaries and https://ffmpeg.org/download.html |

Qt is dynamically linked and can be replaced by a compatible local build. There is no restriction on reverse engineering required to debug user modifications to LGPL components. Runtime binaries are unchanged. Unused Qt bindings, tools, headers and debug artifacts were omitted, and pillow-heif native libraries were relocated from wheel .data/platlib into site-packages. All bundled license and notice texts are retained. Upstream wheel RECORD metadata describes the original upstream wheels; use the top-level SHA256SUMS.txt for this portable package. FFmpeg can be overridden by placing your compatible build at `vendor/ffmpeg.exe` or by setting `IMAGEIO_FFMPEG_EXE`.

The FFmpeg executable distributed in the imageio wheel includes libx264 and other codecs. Its full `-version` output identifies build flags and the exact upstream build. Keep third-party notices and source availability with any redistribution. If publishing a binary release to others, satisfy the corresponding-source and notice obligations for all included AGPL/GPL/LGPL components, including their exact builds; upstream links alone may not satisfy every redistribution mode.

The original application artwork was created with the built-in image-generation tool for this project. Prompt: an original lavender and silver folded-ribbon V on a dark purple rounded square, crisp at small icon sizes, no text or watermark.
