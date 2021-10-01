import os
import pathlib
from typing import Mapping, Any
import math
import decimal
import gc
import sys

import tomli
import tqdm
import nupack

import thtools as tt

nupack.config.cache = 2  # GB

HOME = os.path.dirname(os.path.abspath(__file__))
URLLIB_RETRIES = 10

EXTRA_SIZE = 1
N_SAMPLES = 100
CELSIUS_RANGE = range(0, 100, 10)
Z_SCORE = 1.96

TEXT = """===Information contributed by City of London UK (2021)===
[[File:ToeholdTools.png|x200px|center]]

This toehold switch was characterized <i>in silico</i> using the ToeholdTools project that our team developed.
See https://github.com/lkn849/thtools for more information.
 
Metadata:
*'''Group:''' City of London UK 2021
*'''Author:''' Lucas Ng
*'''Summary:''' Used our software ToeholdTools to investigate the target miRNA specificity and activation of this part.
 
Raw data:
*[[Media:{part}_thtest.txt]]
*[[Media:{part}_thtest.csv]]
*[[Media:{part}_crt.txt]]
*[[Media:{part}_crt.csv]]

This contribution was autogenerated by the script https://github.com/lkn849/thtools/registry/contrib.py using the configuration file https://github.com/lkn849/thtools/registry/{team}.toml.

----

This switch was designed to detect the miRNA {target} at a temperature of {celsius}.
We tested it against every <i>{species}</i> RNA in miRBase and our analysis shows that it is best used to detect {inferred_target_name}.

With {inferred_target_name} at {celsius}°C, the switch has a specificity of {specificity} ± {specificity_se} % and an activation of {activation} ± {activation_se} %.
These values represent 95% confidence limits (z=1.96).

The temperature&ndash;activation&ndash;specificity relationship is shown here:

[[File:{part}_crt.png|500px|center]]

Error bars represent the standard error (SE).
The line of best fit was calculated using a univariate cubic spline weighted inverse to each point's SE.
"""
BAD_SWITCH = """As per the above, we cannot confirm that this switch detects the desired RNA sequence."""
UNRELIABLE_SWITCH = """
Although at the indented usage temperature of {celsius}°C this switch best detected {inferred_target_name}, 
this RNA did not appear as a best target for any of separate tests 
taken at the temperatures tested in the above graph ({temperature_range}). 
Therefore, we cannot confirm the reliability of this switch. 
""".replace(
    "\n", ""
)
CAVEATS = """
'''Caveats:'''
"""
BAD_CONCLUSION = """
We do not recommend this part for future usage.
"""


def mkdir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass


def to_one_sf(x: float) -> decimal.Decimal:
    if x != float("inf"):
        raw = round(x, -int(math.floor(math.log10(abs(x)))))
        if raw >= 1:
            raw = int(raw)
    else:
        raw = x
    return decimal.Decimal(str(raw))


def to_dp(x: float, dp) -> decimal.Decimal:
    x = decimal.Decimal(str(x))
    try:
        return x.quantize(decimal.Decimal(str(10 ** -dp)))
    except decimal.InvalidOperation:
        return x


def dp_count(x: decimal.Decimal) -> int:
    val = x.as_tuple().exponent
    return abs(val) if not isinstance(val, str) else 0


def to_same_dp(x, template):
    return to_dp(x, dp_count(template)) if template != float("inf") else int(x)


class Contribution:
    """A class to generate a contribution to the iGEM Parts Registry based on a team.toml configuration file."""

    __slots__ = (
        "toml_dict",
        "team",
        "rbs",
        "species",
        "celsius",
        "fasta",
        "mirna",
    )
    toml_dict: Mapping[str, Any]
    team: str
    rbs: str
    species: str
    celsius: str
    fasta: tt.FParser
    mirna: Mapping[str, Any]

    def __init__(self, path: str, autorun=True):
        self.team = pathlib.Path(path).stem
        with open(path, "rb") as f:
            self.toml_dict = tomli.load(f)
        self.rbs = self.toml_dict["rbs"]
        self.species = self.toml_dict["species"]
        self.celsius = self.toml_dict["celsius"]
        self.fasta = tt.FParser.fromspecies(self.species)
        self.mirna = {
            key: value
            for key, value in self.toml_dict.items()
            if key not in ("rbs", "species", "celsius")
        }
        mkdir(os.path.join(HOME, "contributions"))
        mkdir(os.path.join(HOME, "contributions", self.team))
        if autorun:
            self.run()

    def run(self):
        with tqdm.tqdm(self.mirna.items(), desc=self.team) as team_bar:
            for mirna, switch in team_bar:
                toeholds = tt.FParser.fromregistry(
                    parts=switch["toeholds"], retries=URLLIB_RETRIES
                )
                if "antis" in switch:
                    antis = [
                        [
                            tt.FParser.fromregistry(part=part, retries=URLLIB_RETRIES)
                            .seqs[0]
                            .upper()
                        ]
                        if part
                        else None
                        for part in switch["antis"]
                    ]
                else:
                    antis = [None] * len(toeholds)
                for ths, toehold_name, anti in tqdm.tqdm(
                    zip(toeholds.seqs, toeholds.ids, antis),
                    total=len(toeholds),
                    desc=mirna,
                    leave=None,
                ):
                    thtest = tt.autoconfig(
                        ths.replace("T", "U").replace("t", "U"),
                        self.rbs,
                        self.fasta.seqs,
                        names=self.fasta.ids,
                        const_rna=anti,
                    )
                    with tqdm.tqdm(
                        total=len(CELSIUS_RANGE) + 1, desc=toehold_name, leave=None
                    ) as switch_bar:
                        thtest.run(
                            max_size=3 + len(antis) + EXTRA_SIZE,
                            n_nodes=tt.CPU_COUNT - 1,
                        )
                        switch_bar.update()
                        crt = tt.CelsiusRangeTest(thtest, CELSIUS_RANGE)
                        for _ in crt.generate(
                            max_size=3 + len(antis) + EXTRA_SIZE,
                            n_nodes=tt.CPU_COUNT - 1,
                        ):
                            switch_bar.update()
                    self.save(mirna, toehold_name, thtest.result, crt.result, team_bar)
                    del thtest
                    del crt
                    gc.collect()

    def save(
        self,
        mirna: str,
        toehold_name: str,
        thtest_res: tt.ToeholdResult,
        crt_res: tt.CelsiusRangeResult,
        bar: tqdm.tqdm,
    ):
        caveats = CAVEATS
        if mirna != thtest_res.target_name:
            caveats += "*" + BAD_SWITCH + "\n"
        try:
            crt_res.inferred_target = thtest_res.target
        except ValueError:
            caveats += "*" + UNRELIABLE_SWITCH + "\n"
        if caveats == CAVEATS:
            caveats = ""
        else:
            caveats += BAD_CONCLUSION
        partdir = os.path.join(HOME, "contributions", self.team, toehold_name)
        mkdir(partdir)
        with open(
            os.path.join(partdir, toehold_name + "_thtest.txt"),
            "w",
        ) as f:
            f.write(thtest_res.prettify())
        with open(
            os.path.join(partdir, toehold_name + "_thtest.csv"),
            "w",
        ) as f:
            f.write(thtest_res.to_csv())
        with open(
            os.path.join(partdir, toehold_name + "_crt.txt"),
            "w",
        ) as f:
            f.write(crt_res.prettify())
        with open(
            os.path.join(partdir, toehold_name + "_crt.csv"),
            "w",
        ) as f:
            f.write(crt_res.to_csv())
        crt_res.savefig(os.path.join(partdir, toehold_name + "_graph.png"), z_score=1)
        specificity_se = to_one_sf(thtest_res.specificity_se * Z_SCORE * 100)
        specificity = to_same_dp(thtest_res.specificity * 100, specificity_se)
        activation_se = to_one_sf(thtest_res.target_activation_se * Z_SCORE * 100)
        activation = to_same_dp(
            thtest_res.target_activation * Z_SCORE * 100, activation_se
        )
        desc = (
            TEXT.format(
                part=toehold_name,
                target=mirna,
                inferred_target_name=thtest_res.target_name,
                celsius=self.celsius,
                specificity=specificity,
                specificity_se=specificity_se,
                activation=activation,
                activation_se=activation_se,
                team=self.team,
                species=self.species,
            )
            + caveats
        )
        with open(os.path.join(partdir, "desc"), "w") as f:
            f.write(desc)
        bar.write(f"Results for {toehold_name} saved.")


if __name__ == "__main__":
    assert (
        len(sys.argv) > 1
    ), "make sure to run the program specifying the team config TOML file!"
    for team in sys.argv[1:]:
        Contribution(os.path.join(HOME, team))
