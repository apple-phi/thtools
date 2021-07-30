import sys
import os

import eel
import nupack

from . import HOME
from ..fasta import FParser
from ..utils import autoconfig
from .. import core

################################################################################

APP_HOME = os.path.join(HOME, "app")
core.USE_TIMER = False
eel.init(os.path.join(APP_HOME, "web"))

################################################################################


SUPPRESS_ERRORS = True


class ErrorHandler:
    """Suppress errors in Python and emit them to Fomantic modal via JS."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if SUPPRESS_ERRORS and exc_type is not None:
            msg = f"{type(exc_val).__name__}: {str(exc_val)}"
            eel.report_error_js(msg)
            print(msg)
            sys.exit()


################################################################################


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

################################################################################


@eel.expose
def print_py(x):
    print(x)


################################################################################


@eel.expose
def species_options_py():
    return FParser.specieslist


################################################################################


@eel.expose
def accept_data_py(x: dict):
    with ErrorHandler():
        global data
        global ths, rbs, temperature, max_size, n_samples
        global fasta, model

        data = x

        ths = data["ths"]
        rbs = data["rbs"]
        FASTA_text = data["FASTA_text"]
        temperature = data["temperature"]
        max_size = data["max_size"]
        n_samples = data["n_samples"]

        max_size = int(max_size)
        n_samples = int(n_samples)
        temperature = float(temperature)

        fasta = FParser(FASTA_text)
        model = nupack.Model(celsius=temperature)


################################################################################


@eel.expose
def FASTA_num_py():
    return fasta.num


################################################################################
@eel.expose
def get_FASTA_text_py(species: str):
    return FParser.fromspecies(species).text.strip()


################################################################################


@eel.expose
def run_test_py():
    with ErrorHandler():
        global test, result_generator
        test = autoconfig(
            ths=ths,
            rbs=rbs,
            triggers=fasta.seqs,
            set_size=1,
            names=fasta.ids,
            model=model,
        )
        result_generator = test.generate(
            max_size=max_size, n_samples=n_samples, chunks_per_node=10
        )


################################################################################


@eel.expose
def next_trigger_py():
    with ErrorHandler():
        try:
            next(result_generator)
        except StopIteration:
            return "StopIteration"


################################################################################


@eel.expose
def send_result_py():
    with ErrorHandler():
        table = test.result.tabulate()
        for col in [
            "RBS unbinding %",
            "AUG unbinding %",
            "Post-AUG unbinding %",
        ]:
            table.del_column(col)
        table_html = table.get_html_string(
            attributes={"class": "ui celled striped table", "id": "result_table"}
        )
        specificity = (
            "{:.4f}".format(test.result.specificity * 100)
            + " ± "
            + "{:.4f}".format(
                1.96 * test.result.specificity_se * 100
            )  # for 95% confidence
            + " %"
        )
        with open(
            os.path.join(APP_HOME, "web", "result.csv"), "w", encoding="utf-8-sig"
        ) as f:  # utf-8-sig includes BOM so MS Excel can read utf-8
            f.write(test.result.to_csv())  # implicitly generates new table first
        eel.create_table_js(table_html, specificity)


################################################################################


def start(suppress_errors=True):
    global SUPPRESS_ERRORS
    SUPPRESS_ERRORS = suppress_errors
    eel.start("index.html", size=(1920, 1080))


################################################################################


print("Python loaded")
