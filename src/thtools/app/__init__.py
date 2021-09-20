"""
The browser connection for ToeholdTools's app.
"""

# This file is part of ToeholdTools (a library for the analysis of
# toehold switch riboregulators created by the iGEM team City of
# London UK 2021).
# Copyright (c) 2021 Lucas Ng

# ToeholdTools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# ToeholdTools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with ToeholdTools.  If not, see <https://www.gnu.org/licenses/>.


import os
from typing import Generator

import eel
import eel.browsers  # for Electron
import nupack
import numpy as np

from thtools import HOME, FParser, autoconfig, ToeholdTest
import thtools.core

__all__ = ["start", "eel"]

################################################################################

APP_HOME = os.path.join(HOME, "app")
thtools.core.USE_TIMER = False
eel.init(os.path.join(APP_HOME, "web"), allowed_extensions=["index.js"])


################################################################################
class GlobalData:
    data: dict
    ths: str
    rbs: str
    temperature: float
    max_size: int
    n_samples: int
    fasta: FParser
    model: nupack.Model
    test: ToeholdTest
    result_generator: Generator[np.ndarray, None, None]


gd = GlobalData()


################################################################################


class ErrorHandler:
    """Emit errors to Fomantic modal in JS."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            msg = f"{type(exc_val).__name__}: {exc_val}"
            eel.report_error_js(msg)


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
def accept_data_py(data: dict):
    with ErrorHandler():
        gd.ths = data["ths"]
        gd.rbs = data["rbs"]
        gd.max_size = int(data["max_size"])
        gd.n_samples = int(data["n_samples"])
        gd.temperature = float(data["temperature"])
        gd.fasta = FParser(data["FASTA_text"])
        gd.model = nupack.Model(celsius=gd.temperature)


################################################################################


@eel.expose
def FASTA_num_py():
    return gd.fasta.num


################################################################################
@eel.expose
def get_FASTA_text_py(species: str):
    return FParser.fromspecies(species).text.strip()


################################################################################


@eel.expose
def run_test_py():
    with ErrorHandler():
        gd.test = autoconfig(
            ths=gd.ths,
            rbs=gd.rbs,
            triggers=gd.fasta.seqs,
            set_size=1,
            names=gd.fasta.ids,
            model=gd.model,
        )
        gd.result_generator = gd.test.generate(
            max_size=gd.max_size, n_samples=gd.n_samples, chunks_per_node=10
        )


################################################################################


@eel.expose
def next_trigger_py():
    with ErrorHandler():
        try:
            next(gd.result_generator)
        except StopIteration:
            return "StopIteration"


################################################################################


@eel.expose
def send_result_py():
    with ErrorHandler():
        table = gd.test.result.tabulate()
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
            "{:.4f}".format(gd.test.result.specificity * 100)
            + " ± "
            + "{:.4f}".format(
                1.96 * gd.test.result.specificity_se * 100
            )  # for 95% confidence
            + " %"
        )
        with open(
            os.path.join(APP_HOME, "web", "result.csv"), "w", encoding="utf-8-sig"
        ) as f:  # utf-8-sig includes BOM so MS Excel can read utf-8
            f.write(gd.test.result.to_csv())  # implicitly generates new table first
        eel.create_table_js(table_html, specificity)


################################################################################


def start(**kwargs):
    print("Python loaded")
    eel.start("index.html", size=(1920, 1080), **kwargs)
