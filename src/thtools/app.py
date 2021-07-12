import os
import sys

import eel
import nupack

from . import HOME, FASTA, autoconfig
from . import analysis

analysis.USE_TIMER = False
eel.init(f"{HOME}/web")


class ErrorHandler:
    def __enter__(self):
        """Create ErrorHandler context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Report exception to JS."""
        if exc_type is not None:
            msg = f"{type(exc_val).__name__}: {str(exc_val)}"
            eel.report_error_js(msg)
            print(msg)
            sys.exit()


# globals
(
    data,
    ths,
    rbs,
    temperature,
    max_size,
    n_samples,
    fasta,
    model,
    test,
    result_generator,
) = [None] * 10


@eel.expose
def print_py(x):
    print(x)


@eel.expose
def species_options_py():
    return FASTA.specieslist


@eel.expose
def accept_data_py(x: dict):
    with ErrorHandler():
        global data
        global ths, rbs, temperature, max_size, n_samples
        global fasta, model

        data = x

        ths = data["ths"]
        rbs = data["rbs"]
        FASTA_txt = data["FASTA_txt"]
        temperature = data["temperature"]
        max_size = data["max_size"]
        n_samples = data["n_samples"]

        max_size = int(max_size)
        n_samples = int(n_samples)
        temperature = float(temperature)

        fasta = FASTA(FASTA_txt)
        model = nupack.Model(celsius=temperature)


@eel.expose
def FASTA_num_py():
    return fasta.num


@eel.expose
def get_FASTA_text_py(species: str):
    return FASTA.fromspecies(species).txt.strip()


@eel.expose
def run_test_py():
    with ErrorHandler():
        global test, result_generator
        test = autoconfig(
            ths=ths,
            rbs=rbs,
            triggers=fasta.seqs,
            set_size=1,
            names=fasta.IDs,
            model=model,
        )
        result_generator = test.generate(
            max_size, n_samples=n_samples, n_chunks=os.cpu_count() * 10
        )


@eel.expose
def next_chunk_len_py():
    with ErrorHandler():
        try:
            chunk = next(result_generator)
            chunk_len = len(chunk.activations)
        except StopIteration:
            chunk_len = "StopIteration"
        return chunk_len


@eel.expose
def send_results_py():
    with ErrorHandler():
        table = test.results.tabulate()
        for col in [
            "RBS exposure %",
            "AUG exposure %",
            "Post-AUG exposure %",
            "Standard error %",
        ]:
            table.del_column(col)
        # table.float_format = ".4"
        table_html = table.get_html_string(
            attributes={"class": "ui celled striped table", "id": "results_table"}
        )
        specificity = (
            "{:.4f}".format(test.results.specificity * 100)
            + " ± "
            + "{:.4f}".format(1.96 * test.results.se * 100)  # for 95% confidence
            + " %"
        )

        with open(
            f"{HOME}/web/results.csv", "w", encoding="utf-8-sig"
        ) as f:  # utf-8-sig includes BOM so MS Excel can read utf-8
            f.write(test.results.to_csv())  # implicitly generates new table first

        eel.create_table_js(table_html, specificity)


print("Python loaded")
eel.start("index.html", size=(1920, 1080))
