"""
Type hints for the `core` submodule of ToeholdTools.
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

from typing import Collection, Mapping, Union, Optional, Generator
import os
import datetime

import numpy as np
import nupack
import prettytable

CPU_COUNT = os.cpu_count()
BASIC_MODEL = nupack.Model()

USE_TIMER: bool = False

class ToeholdResult:
    trigger_sets: Collection[Collection[str]]
    activation: np.ndarray
    rbs_unbinding: np.ndarray
    aug_unbinding: np.ndarray
    post_aug_unbinding: np.ndarray
    activation_se: np.ndarray
    specificity: np.ndarray
    specificity_se: np.ndarray
    target_index: int
    target_set: Collection[str]
    target: Union[str, Collection[str]]
    target_name: str
    target_activation: float
    target_activation_se: float
    unix_created: datetime.datetime
    date: str
    meta: dict
    pretty_meta: str
    @property
    def names(self) -> Collection[Union[str, Collection[str]]]: ...
    @names.setter
    def names(self, value: Collection[Union[str, Collection[str]]]): ...
    def tabulate(
        self,
        dp: Optional[int],
        names: Optional[Collection[Union[str, Collection[str]]]],
        show_unbinding: bool,
    ) -> prettytable.PrettyTable: ...
    def prettify(
        self,
        dp: Optional[int],
        names: Optional[Collection[Union[str, Collection[str]]]],
        show_unbinding: bool,
    ) -> str: ...
    def to_csv(
        self,
        dp: Optional[int],
        names: Optional[Collection[Union[str, Collection[str]]]],
        show_unbinding: bool,
        **kwargs
    ) -> str: ...
    def to_html(
        self,
        dp: Optional[int],
        names: Optional[Collection[Union[str, Collection[str]]]],
        show_unbinding: bool,
        **kwargs
    ) -> str: ...
    def to_json(
        self,
        dp: Optional[int],
        names: Optional[Collection[Union[str, Collection[str]]]],
        show_unbinding: bool,
        **kwargs
    ) -> str: ...

class ToeholdTest:
    # init
    ths: str
    ths_conc: float
    rbs_slice: slice
    trigger_sets: Collection[Collection[str]]
    conc_sets: Collection[Collection[float]]
    const_rna: Mapping[str, float]
    model: nupack.Model
    names: Optional[Collection[Union[str, Collection[str]]]]
    # run
    max_size: int
    n_samples: int
    n_nodes: int
    n_chunks: int
    # result
    result: ToeholdResult
    def __init__(
        self,
        ths: str,
        ths_conc: float,
        rbs_slice: slice,
        trigger_sets: Collection[Collection[str]],
        conc_sets: Collection[Collection[float]],
        const_rna: Mapping[str, float],
        model: nupack.Model,
        names: Optional[Collection[Union[str, Collection[str]]]],
    ): ...
    def copy(self): ...
    def run(
        self, max_size: int, n_samples: int = 100, n_nodes: int = CPU_COUNT
    ) -> ToeholdResult: ...
    def generate(
        self,
        max_size: int,
        n_samples: int = 100,
        n_nodes: int = CPU_COUNT,
        chunks_per_node: int = 1,
    ) -> Generator[np.ndarray, None, None]: ...
