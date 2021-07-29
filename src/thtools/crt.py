"""A sub-module to run a :class:`~thtools.core.ToeholdTest` across temperature ranges.`"""

from typing import Sequence, Optional, Generator
import datetime

import nupack
import numpy as np
import prettytable
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt

from . import CPU_COUNT
from .core import ToeholdTest, ToeholdResult


class CelsiusRangeResult:
    """
    Data container for a :class:`CelsiusRangeTest`.

    Not intended to be constructed manually.

    .. note:: All float values are given as decimals, not percentages.

    Attributes
    ----------
    results : Sequence[ToeholdResult]
        The :class:`~thtools.core.ToeholdResult` objects from each temperature.
    celsius_range : Sequence[float]
    targets : Sequence[str]
        The highest activating item from the trigger_sets of each :class:`~thtools.core.ToeholdResult`.
    target_names : Sequence[str], optional
        The names of each item in :attr:`targets`.
    unix_created : datetime.datetime
    date : str
    meta : dict
    pretty_meta : str
    activation : Sequence[float]
    rbs_unbinding : Sequence[float]
    aug_unbinding : Sequence[float]
    post_aug_unbinding : Sequence[float]
    specificity : Sequence[float]
    activation_se : Sequence[float]
        The standard error of the activation probability.
    specificity_se : Sequence[float]
        The standard error of the specificity.

    Examples
    --------

    .. plot::
        :context: close-figs
        :include-source:

        >>> import thtools as tt
        >>> ths = "UUAGCCGCUGUCACACGCACAGGGAUUUACAAAAAGAGGAGAGUAAAAUGCUGUGCGUGCACCAUAAAACGAACAUAGAC"
        >>> rbs = "AGAGGAGA"
        >>> fasta = tt.FParser.fromspecies("Homo sapiens")[295:305]
        >>> triggers = fasta.seqs
        >>> temperatures = range(10, 101, 10)
        >>> my_test = tt.autoconfig(ths, rbs, triggers)
        >>> my_crt = tt.CelsiusRangeTest(my_test, temperatures)
        >>> my_result = my_crt.run(max_size=3, n_samples=200)
        >>> my_result.plot().show()

    See Also
    --------
    CelsiusRangeTest
    """

    __slots__ = (
        "results",
        "celsius_range",
        "targets",
        "target_names",
        "unix_created",
        "date",
        "meta",
        "pretty_meta",
        "_inferred_target",
        "_inferred_target_name",
        "activation",
        "rbs_unbinding",
        "aug_unbinding",
        "post_aug_unbinding",
        "specificity",
        "activation_se",
        "specificity_se",
    )

    results: Sequence[ToeholdResult]
    celsius_range: Sequence[float]
    targets: Sequence[str]
    target_names: Optional[Sequence[str]]

    unix_created: datetime.datetime
    date: str
    meta: dict
    pretty_meta: str

    _inferred_target: str
    _inferred_target_name: str

    activation: Sequence[float]
    rbs_unbinding: Sequence[float]
    aug_unbinding: Sequence[float]
    post_aug_unbinding: Sequence[float]
    specificity: Sequence[float]
    activation_se: Sequence[float]
    specificity_se: Sequence[float]

    def __init__(
        self,
        results: Sequence[ToeholdResult],
        celsius_range: Sequence[float],
        meta: dict,
    ):
        self.results = results
        self.celsius_range = celsius_range
        self.meta = meta
        self.unix_created = datetime.datetime.now()
        self.date = self.unix_created.strftime("%b %-d %Y at %H:%M:%S")

        self.targets = [result.target for result in results]
        self.target_names = [result.target_name for result in results]

        # assume the mode is the actual target
        self.inferred_target = max(set(self.targets), key=self.targets.count)

    @property
    def inferred_target(self):
        """The target sequence inferred from the mode of the individual :class:`~thtools.core.ToeholdTest` highest activators."""
        return self._inferred_target

    @inferred_target.setter
    def inferred_target(self, value):
        self.meta["Target"] = self._inferred_target = value
        self.meta["Target name"] = self._inferred_target_name = self.target_names[
            self.targets.index(value)
        ]
        self.pretty_meta = "\n".join(
            [f"{key}: {value}" for key, value in self.meta.items()]
        )
        self.specificity = []
        self.specificity_se = []
        self.activation = []
        self.activation_se = []
        self.aug_unbinding = []
        self.rbs_unbinding = []
        self.post_aug_unbinding = []
        for result in self.results:
            target_index = next(  # the first result from the below generator
                (
                    index
                    for index, val in enumerate(result.trigger_sets)
                    if val == self.inferred_target
                    or (len(val) == 1 and val[0] == self.inferred_target)
                )
            )
            self.activation.append(result.activation[target_index])
            self.activation_se.append(result.activation_se[target_index])
            self.rbs_unbinding.append(result.rbs_unbinding[target_index])
            self.aug_unbinding.append(result.aug_unbinding[target_index])
            self.post_aug_unbinding.append(result.post_aug_unbinding[target_index])
            if result.target == self.inferred_target:
                self.specificity.append(result.specificity)
                self.specificity_se.append(result.specificity_se)
            else:
                self.specificity.append(0)
                self.specificity_se.append(0)

    @property
    def inferred_target_name(self):
        """The name of the :attr:`inferred_target`."""
        return self._inferred_target_name

    @inferred_target_name.setter
    def inferred_target_name(self, value):
        # can just call the inferred_target_name setter to avoid code repetition
        self.inferred_target = self.targets[self.target_names.index(value)]

    def __repr__(self):
        return f"<{self.__module__}.{type(self).__qualname__} of {len(self.results)} ToeholdTests at {hex(id(self))}>"

    def plot(
        self, y: str = "activation", filename: Optional[str] = None, swap: bool = False
    ):
        """
        Plot temperature against specificity, with color being the activation.

        The following axes are plotted:

        .. list-table::
            :widths: auto
            :align: center
            :header-rows: 1

            * - Axis
              - Value
            * - x
              - temperature /°C
            * - y
              - toehold switch activation %
            * - color
              - specificity %

        Parameters
        ----------
        filename : str, optional
            The filename to save the figure to if desired.
        swap : bool, optional
            Whether or not to swap the specificity and activation in the plot. Defaults to False.
        """
        y = y.strip().lower().replace(" ", "_").replace("-", "_")
        y_name = y.replace("_", " ").capitalize()
        x_vals = self.celsius_range
        cmap = sns.color_palette("crest", as_cmap=True)
        fig, ax = plt.subplots()
        formatter = matplotlib.ticker.ScalarFormatter(useOffset=False)
        if not swap:
            y_vals = np.array(getattr(self, y)) * 100
            z_vals = np.array(self.specificity) * 100
            scatter = ax.scatter(x_vals, y_vals, c=z_vals, cmap=cmap)
            fig.colorbar(scatter, label="Specificity %", format=formatter)
            ax.set_xlabel("Temperature /°C")
            ax.set_ylabel(y_name)
        else:
            y_vals = np.array(self.specificity) * 100
            z_vals = np.array(getattr(self, y)) * 100
            scatter = ax.scatter(x_vals, y_vals, c=z_vals, cmap=cmap)
            fig.colorbar(scatter, label=y_name, format=formatter)
            ax.set_xlabel("Temperature /°C")
            ax.set_ylabel("Specificity %")
        ax.set_axisbelow(True)
        ax.grid()
        plt.title(
            f"CRT for toehold detecting {self.inferred_target_name if self.inferred_target_name is not None else self.inferred_target}"
        )
        if filename is not None:
            fig.savefig(filename, dpi=1200)
            return plt
        else:
            return plt

    def __str__(self):
        return self.prettify()

    def tabulate(self, dp: Optional[int] = None):
        """
        Create a :class:`prettytable.PrettyTable` of the result.

        Parameters
        ----------
        dp : int, optional
            The decimal places to use.
        """
        table = prettytable.PrettyTable()
        table.add_column("Temperature /°C", self.celsius_range)
        table.add_column("Target", self.targets)
        if len(self.target_names) > 0 and not all(self.target_names):
            names = ["+".join(name) for name in self.target_names]
            table.add_column("Name", names)
        table.add_column("Activation %", [i * 100 for i in self.activation])
        table.add_column("Specificity %", [i * 100 for i in self.specificity])
        table.add_column("Activation SE", [i * 100 for i in self.activation_se])
        table.add_column("Specificity SE", [i * 100 for i in self.specificity_se])
        table.align = "l"
        table.reversesort = True
        if dp is not None:
            table.float_format = f".{dp}"
        return table

    def prettify(self, dp: Optional[int] = None) -> str:
        """
        Alias to str(self). Get the result as its :class:`prettytable.PrettyTable`
        in string form, with added metadata.

        Parameters
        ----------
        dp : int, optional
            The decimal places to use.
        """
        return f"{self.date}\n\n{self.pretty_meta}\n\n{self.tabulate(dp)}"

    def to_csv(self, dp: Optional[int] = None, **kwargs) -> str:
        """
        Get the result as a CSV with added metadata.

        Parameters
        ----------
        dp : int, optional
            The decimal places to use.
        **kwargs
            Extra arguments to be passed to :func:`csv.writer` via :class:`prettytable.PrettyTable`.
        """
        csv_meta = self.pretty_meta.replace(": ", ",")
        return (
            f"{self.date}\n\n{csv_meta}\n\n{self.tabulate(dp).get_csv_string(**kwargs)}"
        )

    def to_html(self, dp: Optional[int] = None, **kwargs) -> str:
        """
        Get the result as a HTML table.

        Parameters
        ----------
        dp : int, optional
            The decimal places to use.
        **kwargs
            Extra arguments to be passed to :mod:`PrettyTable`.
        """
        return self.tabulate(dp).get_html_string(**kwargs)

    def to_json(self, dp: Optional[int] = None, **kwargs) -> str:
        """
        Get the result as a JSON string.

        Parameters
        ----------
        dp : int, optional
            The decimal places to use.
        **kwargs
            Extra arguments to be passed to :mod:`PrettyTable`.
        """
        return self.tabulate(dp).get_json_string(**kwargs)


################################################################################


class CelsiusRangeTest:
    """
    Utility for running a :class:`~thtools.core.ToeholdTest` at a range of temperatures.

    The name is sometimes abbreviated to CRT as a shorthand.

    .. note::
        There is no performance to be gained from using the :metH:`run` method
        instead of :meth:`generate`, unlike with :class:`~thtools.core.ToeholdTest`.

        This is because each individual :class:`~thtools.core.ToeholdTest`
        in the temperature range already utilizes the specified number of CPU core,
        so further multiprocessing is impossible.

    Parameters
    ----------
    thtest : ToeholdTest
        The :class:`~thtools.core.ToeholdTest` to adjust the temperature of.
    celsius_range : Sequence[float]
        The array of temperature values in °C.

    Attributes
    ----------
    thtest : ToeholdTest
    celsius_range : Sequence[float]

    Examples
    --------
    >>> import thtools as tt
    >>> ths = "UUAGCCGCUGUCACACGCACAGGGAUUUACAAAAAGAGGAGAGUAAAAUGCUGUGCGUGCACCAUAAAACGAACAUAGAC"
    >>> rbs = "AGAGGAGA"
    >>> triggers = ["CUGUGCGUGUGACAGCGGCUGA", "CUAUACAAUCUACUGUCUUUCC", "UGUACAGCCUCCUAGCUUUCC"]
    >>> temperatures = range(10, 61, 5)
    >>> my_test = tt.autoconfig(ths, rbs, triggers)
    >>> my_crt = tt.CelsiusRangeTest(my_test, temperatures)
    >>> my_result = my_crt.run(max_size=3, n_samples=100)
    >>> my_result.inferred_target
    'CUGUGCGUGUGACAGCGGCUGA'

    See Also
    --------
    CelsiusRangeResult
    """

    thtest: ToeholdTest
    celsius_range: Sequence[float]

    def __init__(self, thtest: ToeholdTest, celsius_range: Sequence[float]):
        self.thtest = thtest
        self.celsius_range = celsius_range

    def run(
        self, max_size: int, n_samples: int = 100, n_nodes: int = CPU_COUNT
    ) -> CelsiusRangeResult:
        """
        Run the test.

        This is an alias to the :meth:`generate` method and handles the iteration for you.
        Thus, there is no performance gain from using this over :meth:`generate`.

        Parameters
        ----------
        max_size : int
            The maximum RNA complex size to simulate
        n_samples : int, default=100
            The number of Boltzmann samples to take of each complex's secondary structure.
        n_nodes : int, default=os.cpu_count()
            The number of CPU cores to distribute work across using Pathos.

        Returns
        -------
        ToeholdResult
            A container for the data.

        Notes
        -----
        The result is also stored in the :attr:`result` attribute.
        """
        for _ in self.generate(max_size, n_samples, n_nodes):
            pass
        return self.result

    def generate(
        self, max_size: int, n_samples: int = 100, n_nodes: int = CPU_COUNT
    ) -> Generator[ToeholdResult, None, None]:
        """
        Run the test, returning a generator that the user must iterate through.

        It stores a :class:`CelsiusRangeResult` to the :attr:`result` attribute.

        Parameters
        ----------
        max_size : int
            The maximum RNA complex size to simulate
        n_samples : int, default = 100
            The number of Boltzmann samples to take of each complex's secondary structure.
        n_nodes : int, default = :func:`os.cpu_count()`
            The number of CPU cores to distribute work across using Pathos.

        Yields
        ------
        ToeholdResult
            The result of the test at the nth temperature in the :attr:`celsius_range`.

        Notes
        -----
        Unlike :meth:`generate`, this method has no significant performance penalty compared to :meth:`run`.
        """
        chunks = []
        for celsius in self.celsius_range:
            chunks.append(
                self._adjust_temperature(celsius).run(max_size, n_samples, n_nodes)
            )
            yield chunks[-1]
        self.result = CelsiusRangeResult(
            chunks, self.celsius_range, meta={"THS": self.thtest.ths}
        )

    def _adjust_temperature(self, celsius: float) -> ToeholdTest:
        new_thtest = self.thtest.copy()
        ensemble = self.thtest.model.ensemble
        material = self.thtest.model.material
        conditions = self.thtest.model.conditions.save()
        del conditions["temperature"]
        self.thtest.model = nupack.Model(
            ensemble=ensemble, material=material, celsius=celsius, **conditions
        )
        return new_thtest
