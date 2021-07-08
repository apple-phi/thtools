from typing import Collection, Optional

import nupack

from . import autoconfig, FASTA


def basic(
    ths: str,
    rbs: str = "AGAGGAGA",
    const_rna: Optional[Collection[str]] = None,
    max_size: int = 3,
    n_samples: int = 100,
    celsius: float = 37.0,
    filename: str = "output.txt",
    nupack_v: int = 4,
) -> None:
    """Basic test against miRNAs from the Homo sapiens miRBase which saves results as text. You can also set file ending to .csv for a spreadsheet."""
    if nupack_v == 4:
        model = nupack.Model(celsius=celsius)
    elif nupack_v == 3:
        model = nupack.Model(ensemble="some-nupack3", material="rna95-nupack3", celsius=celsius)
    else:
        raise ValueError(
            f"only NUPACK versions supported allowed, not 'nupack_v={nupack_v}'"
        )
    fasta = FASTA.fromspecies("Homo sapiens")
    t = autoconfig(
        ths=ths,
        rbs=rbs,
        triggers=fasta.seqs,
        set_size=1,
        names=fasta.IDs,
        const_rna=const_rna,
        model=model,
    )
    results = t.run(max_size, n_samples=n_samples)
    with open(filename, "w", encoding="utf-8-sig") as f:
        if filename.endswith(".csv"):
            f.write(results.to_csv())
        else:
            f.write(results.prettify())
