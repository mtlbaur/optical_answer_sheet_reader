# Optical Answer Sheet Reader

This program reads a PDF scan of custom Optical Answer Sheet test forms, processes the data, and writes the results into PDF, CSV, and JSON files. The format of the PDF is always: 1 key form followed by N response forms where each response form corresponds to a single person's responses. The question-related responses are compared to what is entered in the key to determine correctness. A form contains the following fields:

- Last Name (10 chars A-Z)
- First Name (10 chars A-Z)
- Field 1 (10 chars A-Z)
- Field 2 (10 digits 0-9)
- Field 3 (10 digits 0-9)
- Questions (120 * 5 choices of A, B, C, D, E)

Fields 1-3 are generic so as to allow a wide variety of uses.

## Usage

- Use a color printer to print copies of the `./form/oasr-f#.pdf` form.

- Fill in a single key form with the correct answers.

- Allow the test subjects to fill in their copies of the form.

- Stack the copies in such a way that the key form will be scanned first (the key form must be at the top of the resulting PDF) and that all have the same orientation.

- Scan the stack of copies and save it as a PDF (a scan precision of 300 DPI is known to to be sufficient).

- Launch the OASR program from anywhere via the `./start/oasr_start.py` script.

- Fill in the Infile Path field with the path of PDF via the "Select" button.

- Optionally:
    - Generate/fill in a Outfile Name.

    - Select which types of output files to write.

    - Enable/disable data plotting (the plots can be saved to image files via Matplotlib's GUI).

    - Enable/disable debug mode (will display many images visualizing what the program sees while reading the scans).

    - Enable/disable cache writing which has two uses:
        1. Fix any errors that might occur as a result of filling in the form answers by hand. This is done by editing a formatted Python dictionary data structure of the entire scanned PDF.

        2. Greatly speed up subsequent processing of the same test scan. Note: because the test data is read directly from the data structure, the scan-reading part is skipped entirely. This means that any changes to settings related to this reading have no effect, e.g.: DPI, rotation, and darkness threshold.

    - Change the DPI to match the PDF's DPI.

    - Change the base rotation in degrees of all pages within the PDF (in case the scanner oriented them horizontally or even up-side-down).

    - Change the darkness threshold which is used to determine what constitutes "dark enough" to be a penciled-in response (it is not recommended to change this value from the default 128). The lower the value the more dark responses have to be.

    - Switch the GUI theme between System, Light, and Dark.

- Click Start and wait until the GUI console displays `[done]`.

- By default the output file location will be automatically opened in file explorer (togglable via the "Open Output" checkbox). To do this manually, click the "Open Outpath" button.

- A task can be terminated before completion via the Stop button.

- Execution can take several minutes depending on the processing capability of the computer and the number of pages in the PDF.

- The configuration of settings is automatically saved to `./cfg/oasr.cfg`. To perform a hard-reset of all settings without having to use the built-in Default button on the GUI, delete this file.

## Installation

This program relies on Python and Poppler being installed. Poppler is used to extract images from the PDF scans.

- Install Python.

- Download/extract Windows-compatible Poppler: https://github.com/oschwartz10612/poppler-windows/releases.

- Add the `.../poppler-VERSION/Library/bin` path to the Windows environment variable `Path`.

- Download/extract the newest release located in `./rel` of this repo and navigate to the `./rel/dist` subfolder.

- Execute `pip install ./oasr-VERSION-py2.py3-none-any.whl`.

- Launch the program from anywhere via the `./start/oasr_start.py` script.

## Updating

- Download/extract the newest release located in `./rel` of this repo and navigate to the `./rel/dist` subfolder.

- Execute `pip install --upgrade ./oasr-VERSION-py2.py3-none-any.whl`.

## Uninstallation

- Execute `pip uninstall oasr`.

- Remove the `.../poppler-VERSION/Library/bin` path from the Windows environment variable `Path`.

- Uninstall Python.

## Credits

- Poppler and pdf2image for easy extraction of images from PDF files.
- OpenCV-Python for crucial computer vision functionality used to read the form images.
- Flet for a nice, easy to use, GUI library.
- Matplotlib for plotting.
- ReportLab for PDF output file creation.
