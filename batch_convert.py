# %% [markdown]
# Batch convert multiple PDF files and export results in several formats.

# What this example does
# - Loads a small set of sample PDFs.
# - Runs the Docling PDF pipeline once per file.
# - Writes outputs to `scratch/` in multiple formats (JSON, HTML, Markdown, text, doctags, YAML).

# Prerequisites
# - Install Docling and dependencies as described in the repository README.
# - Ensure you can import `docling` from your Python environment.
# <!-- YAML export requires `PyYAML` (`pip install pyyaml`). -->

# Input documents
# - By default, this example uses a few PDFs from `tests/data/pdf/` in the repo.
# - If you cloned without test data, or want to use your own files, edit
#   `input_doc_paths` below to point to PDFs on your machine.

# Output formats (controlled by flags)
# - `USE_V2 = True` enables the current Docling document exports (recommended).
# - `USE_LEGACY = False` keeps legacy Deep Search exports disabled.
#   You can set it to `True` if you need legacy formats for compatibility tests.

# Notes
# - Set `pipeline_options.generate_page_images = True` to include page images in HTML.
# - The script logs conversion progress and raises if any documents fail.
# <!-- This example shows both helper methods like `save_as_*` and lower-level
#   `export_to_*` + manual file writes; outputs may overlap intentionally. -->
# %%

import logging
import time
from collections.abc import Iterable
from pathlib import Path

from docling_core.types.doc import ImageRefMode

from docling.backend.docling_parse_backend import DoclingParseDocumentBackend
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import ThreadedPdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions

_log = logging.getLogger(__name__)

NUM_THREADS = 32

def export_documents(
    conv_results: Iterable[ConversionResult],
    output_dir: Path,
):
    output_dir.mkdir(parents=True, exist_ok=True)

    success_count = 0
    failure_count = 0
    partial_success_count = 0

    for conv_res in conv_results:
        if conv_res.status == ConversionStatus.SUCCESS:
            success_count += 1
            doc_filename = conv_res.input.file.stem

            conv_res.document.save_as_markdown(
                output_dir / f"{doc_filename}.txt",
                image_mode=ImageRefMode.PLACEHOLDER,
            )

        elif conv_res.status == ConversionStatus.PARTIAL_SUCCESS:
            _log.info(
                f"Document {conv_res.input.file} was partially converted with the following errors:"
            )
            for item in conv_res.errors:
                _log.info(f"\t{item.error_message}")
            partial_success_count += 1
        else:
            _log.info(f"Document {conv_res.input.file} failed to convert.")
            failure_count += 1

    _log.info(
        f"Processed {success_count + partial_success_count + failure_count} docs, "
        f"of which {failure_count} failed "
        f"and {partial_success_count} were partially converted."
    )
    return success_count, partial_success_count, failure_count


def main():
    logging.basicConfig(level=logging.INFO)

    # Location of sample PDFs used by this example. If your checkout does not
    # include test data, change `data_folder` or point `input_doc_paths` to
    # your own files.
    data_folder = Path(__file__).parent / "out"
    input_doc_paths = data_folder.glob("*.pdf")

    # buf = BytesIO((data_folder / "pdf/2206.01062.pdf").open("rb").read())
    # docs = [DocumentStream(name="my_doc.pdf", stream=buf)]
    # input = DocumentConversionInput.from_streams(docs)

    # # Turn on inline debug visualizations:
    # settings.debug.visualize_layout = True
    # settings.debug.visualize_ocr = True
    # settings.debug.visualize_tables = True
    # settings.debug.visualize_cells = True

    # Configure the PDF pipeline. Enabling page image generation improves HTML
    # previews (embedded images) but adds processing time.
    gpu_accel = AcceleratorOptions(num_threads=NUM_THREADS, device=AcceleratorDevice.CUDA)
    pipeline_options = ThreadedPdfPipelineOptions(
        accelerator_options=gpu_accel,
        generate_page_images=False,
        generate_picture_images=False,
        do_table_structure=False,
        do_code_enrichment=False,
        do_formula_enrichment=False,
        ocr_batch_size=64,
        layout_batch_size=64,
        table_batch_size=64,
        batch_timeout_seconds=2.0,
        queue_max_size=1000,
        
    )

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options, backend=DoclingParseDocumentBackend
            )
        }
    )

    start_time = time.time()

    # Convert all inputs. Set `raises_on_error=False` to keep processing other
    # files even if one fails; errors are summarized after the run.
    conv_results = doc_converter.convert_all(
        input_doc_paths,
        raises_on_error=False,  # to let conversion run through all and examine results at the end
    )
    # Write outputs to ./scratch and log a summary.
    _success_count, _partial_success_count, failure_count = export_documents(
        conv_results, output_dir=Path("scratch")
    )

    end_time = time.time() - start_time

    _log.info(f"Document conversion complete in {end_time:.2f} seconds.")

    if failure_count > 0:
        raise RuntimeError(
            f"The example failed converting {failure_count} on {len(input_doc_paths)}."
        )

if __name__ == "__main__":
    main()