#!python
#cython: language_level=3, cdivision=True, initializedcheck=False, binding=True, linetrace=True
#distutils: define_macros=CYTHON_TRACE_NOGIL=1
#distutils: define_macros=NPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION

"""
The core data powerhouse of the ToeholdTools library.
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

from typing import Collection, Generator, Sequence, Mapping, Optional, Union

import os
import time
import datetime

import pathos
import nupack
import prettytable
import numpy as np

cimport numpy as np
cimport cython
from cpython cimport datetime
from libc.float cimport DBL_MIN
from libc.math cimport sqrt #, fabs


__all__ = ["USE_TIMER", "ToeholdTest", "ToeholdResult"]


cdef int CPU_COUNT = os.cpu_count()
cdef object BASIC_MODEL = nupack.Model()

USE_TIMER: bool = False # docstring doesn't get compiled :(
"""
Whether to show the simulation event log.

If True, every time a NUPACK simulation
or data processing event finishes on any CPU core,
the event type and runtime will be printed.
"""

cdef class _Timer:
    """
    Basic class for timing tests.

    Turn on with :attr:`thtools.core.USE_TIMER = True`.
    
    Built in use is as a context manager.
    It prints the time taken once the context manager has been exited.
    """
    cdef:
        double start
        double end
        double elapsed
        str name
    def __init__(self, str name=""):
        self.start = time.time()
        self.name = name
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, exc_tb):
        if <bint> USE_TIMER:
            self.stop()
            print(f"{self.name} took {self.elapsed}s")
    cdef void stop(self):
        self.end = time.time()
        self.elapsed = self.end - self.start
        


@cython.auto_pickle(True)
@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
cdef class ToeholdTest:
    """
    A class to test different trigger sets against the toehold switch
    for activation, in order to find specificity.

    All parameters are safe to be mutated after instantiation
    but before the simulation is run.

    Parameters
    ----------
    ths : str
        Your toehold switch.
    ths_conc : float
        The concentration of your toehold switch.
    rbs_slice : slice
        The slice of the toehold switch containing the RBS.
    trigger_sets : Collection[Collection[str]]
        An array-like of trigger sets.
        Each trigger set will be tested seperately from the others.
    conc_sets : Collection[Collection[float]]
        Concentrations of the above triggers in each trigger set.
    const_rna : Mapping[str, float], default={}
        Mapping of `{sequence : concentration}`
        for any RNAs you want to be present/constant
        in all test tube simulations.
    model : nupack.Model, default=nupack.Model()
        The thermodynamic model to use.
    names : Collection[str | Collection[str]], optional
        The names of each trigger set.
        If a collection of names is given for each trigger set,
        they will be joined with '+' signs.
        This can also be set through the names attribute of :class:`ToeholdResult`
        or passed as an argument to one of the :class:`ToeholdResult` methods.

    Attributes
    ----------
    ths : str
    ths_conc : float
    rbs_slice : slice
    trigger_sets : Collection[Collection[str]]
    conc_sets : Collection[Collection[float]]
    const_rna : Mapping[str, float], default = {}
    model : nupack.Model, default = nupack.Model()
    names : Collection[str | Collection[str]], optional
    result : ToeholdResult

    Raises
    ------
    AssertionError
        If :attr:`trigger_sets` has a different shape to :attr:`conc_sets`.

    Notes
    -----
    - Runs a test tube simulation for each trigger set using NUPACK.
    - Analyzes the complexes and their concentrations up to a complex size of :attr:`max_size`.
    - Each complex has :attr:`n_samples` Boltzmann samples taken.
    - Hence the probability of the toehold being properly unbound is calculated.
    
    Examples
    --------
    >>> import thtools as tt
    >>> ths = "UUAGCCGCUGUCACACGCACAGGGAUUUACAAAAAGAGGAGAGUAAAAUGCUGUGCGUGCACCAUAAAACGAACAUAGAC"
    >>> ths_conc = 1e-7
    >>> rbs_slice = slice(34, 42)
    >>> trigger_sets = [["CUGUGCGUGUGACAGCGGCUGA"],
    ...                 ["CUAUACAAUCUACUGUCUUUCC"],
    ...                 ["UGUACAGCCUCCUAGCUUUCC"]]
    >>> conc_sets = [[1e-7],
    ...              [1e-7],
    ...              [1e-7]]
    >>> my_test = tt.ToeholdTest(ths, ths_conc, rbs_slice, trigger_sets, conc_sets)
    >>> my_result = my_test.run(max_size=3, n_samples=100)
    >>> my_result.specificity # gives as decimal, not percentage
    0.9999999801562275

    See Also
    --------
    ToeholdResult
        Data container for the result of a :class:`ToeholdTest`.
    :func:`~thtools.utils.autoconfig`
        Quick configuration of ToeholdTests,
        assuming every RNA has the concentration of
        :attr:`thtools.utils.ASSUMED_STRAND_CONC`.
    """
    cdef:
        # public attrs: ths, ths_conc, model

        # init
        public str ths
        public double ths_conc
        public slice rbs_slice
        public object trigger_sets
        public object conc_sets
        public dict const_rna
        public object model
        public object names
        

        # setup
        (size_t, size_t) _rbs_slice
        list const_rna_seqs
        list const_rna_concs
        double start
        readonly Py_ssize_t aug_position # readonly for testing
        list chunked_trigger_sets
        list chunked_conc_sets
        dict const_strands
        object pool
        dict meta

        # run
        public int max_size
        public int n_samples
        public int n_nodes
        public int n_chunks

        # output
        readonly ToeholdResult result
    
    def __init__(self,
                 ths: str,
                 ths_conc: float,
                 rbs_slice: slice,
                 trigger_sets: Collection[Collection[str]] = np.empty(shape=(0,0), dtype=str), # in form [set1, set2, set3, ...]
                 conc_sets: Collection[Collection[float]] = np.empty(shape=(0,0), dtype=np.float64), # in same shape as trigger_sets
                 const_rna: Mapping[str, float] = {}, # {RNA:conc, RNA:conc, etc ...}
                 model: nupack.Model = BASIC_MODEL,
                 names: Optional[Collection[Union[str,Collection[str]]]] = None):

        self.ths = ths
        self.ths_conc = ths_conc
        self.rbs_slice = rbs_slice
        self.trigger_sets = trigger_sets
        self.conc_sets = conc_sets
        self.const_rna = const_rna
        self.model = model
        self.names = names

    def __eq__(self, ToeholdTest other):
        cdef object item
        return <bint> (
            self.ths == other.ths
            and self.ths_conc == other.ths_conc
            and self.rbs_slice == other.rbs_slice
            and np.asarray(self.trigger_sets == other.trigger_sets).all()
            and np.asarray(self.conc_sets == other.conc_sets).all()
            and self.const_rna == other.const_rna
            and self.model == other.model
            and np.asarray(self.names == other.names).all()
        )

    def copy(self) -> ToeholdTest:
        """Return a copy of self."""
        # since the only public attrs are ths, ths_conc and model, we only need to make a proper copy of nupack.Model
        cdef ToeholdTest new = ToeholdTest(
            ths=self.ths,
            ths_conc=self.ths_conc,
            rbs_slice=self.rbs_slice,
            trigger_sets=self.trigger_sets,
            conc_sets=self.conc_sets,
            const_rna=self.const_rna,
            model=copy_model(self.model),
            names=self.names
        )
        new.result = <ToeholdResult> self.result
        return <ToeholdTest> new
    
    def run(self,
            max_size: int,
            n_samples: int = 100,
            n_nodes: int = CPU_COUNT) -> ToeholdResult:
        """
        Run the test.

        Parameters
        ----------
        max_size : int
            The maximum RNA complex size to simulate.
        n_samples : int, default = 100
            The number of Boltzmann samples to take of each complex's secondary structure.
        n_nodes : int, default = :func:`os.cpu_count()`
            The number of CPU cores to distribute work across using :mod:`pathos`.

        Returns
        -------
        ToeholdResult
            A container for the data.

        Notes
        -----
        The result is also stored in the :attr:`result` attribute.
        """
        
        self.max_size = max_size
        self.n_samples = n_samples
        self.n_nodes = n_nodes
        self.n_chunks = CPU_COUNT
        
        self._setup()
        
        cdef:
            object chunked_result
            np.ndarray final_result
        if self.chunked_trigger_sets != []: # support for testing only the ths + constants
            chunked_result = self.pool.map(self._worker,
                                            self.chunked_trigger_sets,
                                            self.chunked_conc_sets,
                                            chunksize=1)                                            
            final_result = np.concatenate(chunked_result, axis=1)
        else:
            final_result = self._worker()
        self._finally(final_result)
        return self.result
        
    def generate(self,
                 max_size: int,
                 n_samples: int = 100,
                 n_nodes: int = CPU_COUNT,
                 chunks_per_node: int = 1) -> Generator[np.ndarray, None, None]:
        """
        Run the test, returning a generator that the user must iterate through.

        This generator allows the display of progress bars for the work, but is slower than the :meth:`run` method.
        It stores a :class:`ToeholdResult` to the `result` attribute.

        Parameters
        ----------
        max_size : int
            The maximum RNA complex size to simulate.
        n_samples : int, default = 100
            The number of Boltzmann samples to take of each complex's secondary structure.
        n_nodes : int, default = :func:`os.cpu_count()`
            The number of CPU cores to distribute work across using Pathos.
        chunks_per_node : int, default = 1
            The number of chunks to split each node's work into.
            Increasing this will produce a smoother progress bar, but a slower simulation.

        Yields
        ------
        np.ndarray
            `[activation, RBS unbinding, start codon unbinding, post-start codon unbinding, activation standard error]`
            for each trigger set in :attr:`trigger_sets`.

        Notes
        -----
        This method is significantly slower than :meth:`run` (>20% slower for large jobs).
            
        """
        
        self.max_size = max_size
        self.n_samples = n_samples
        self.n_nodes = n_nodes
        self.n_chunks = chunks_per_node * n_nodes
        
        self._setup()
        cdef:
            list chunked_result
            np.ndarray chunk
            np.ndarray final_result 
            np.ndarray subarray
        chunked_result = []
        for chunk in self.pool.imap(self._worker, self.chunked_trigger_sets,self.chunked_conc_sets, chunksize=1):
            chunked_result.append(chunk)
            for subarray in chunk.T:
                yield subarray
        final_result = np.concatenate(chunked_result, axis=1)
        self._finally(final_result)

    cpdef void _setup(self) except *:
        cdef:
            Py_ssize_t i, c
            object trig_arr
            object conc_arr

        # extract RBS indicies
        self._rbs_slice = self.rbs_slice.start, self.rbs_slice.stop

        # data extraction
        self.const_rna_seqs, self.const_rna_concs = list(self.const_rna.keys()), list(self.const_rna.values())
        self.ths = self.ths.upper()

        # timer
        self.start = time.time()
    
        # locate aug -> this must be done before safety checks
        # find the first AUG sequence after the RBS
        for i in range(self._rbs_slice[1], len(self.ths)):
            if self.ths[i:i+3] == "AUG":
                self.aug_position = i
                break
        else:
            raise UserWarning("No AUG found after RBS!")

        # chunk trigger_sets and remove empty arrays from end
        self.chunked_trigger_sets = [trig_arr for trig_arr in np.array_split(self.trigger_sets,self.n_chunks) if trig_arr.size != 0]
        self.chunked_conc_sets = [conc_arr for conc_arr in np.array_split(self.conc_sets,self.n_chunks) if conc_arr.size != 0]

        # make constant strands
        self.const_strands = {nupack.Strand(self.ths, name = "ths") : self.ths_conc,
                                **{
                                    nupack.Strand(self.const_rna_seqs[c],name = self.const_rna_seqs[c]) : self.const_rna_concs[c]
                                    for c in range(len(self.const_rna_seqs))
                                    }
                                }
        
        # create worker pool
        self.pool = pathos.multiprocessing.ProcessPool(nodes=self.n_nodes)

        # store meta
        self.meta = {"THS"                              :self.ths,
                     "THS concentration"                :self.ths_conc,
                     "RBS"                              :self.ths[self.rbs_slice],
                     "No. trigger sets"                 :len(self.trigger_sets),
                     "Constant RNAs"                    :self.const_rna_seqs,
                     "Concentrations of constant RNAs"  :self.const_rna_concs,
                     "Temperature /°C"                  :self.model.temperature-273.15,
                     "Max. complex size"                :self.max_size,
                     "Sample number"                    :self.n_samples}

        # safety checks
        cdef:
            object trigger_array = np.asarray(self.trigger_sets)
            object conc_array = np.asarray(self.conc_sets, dtype=np.float64)
        assert trigger_array.ndim == 2, "trigger_sets must have exactly 2 dimensions."
        assert conc_array.ndim == 2, "conc_sets must have exactly 2 dimensions."
        assert <bint> (conc_array > 0).all(), "all concentrations must be > 0."

    cdef void _finally(self, np.ndarray final_result):
        self.meta["Runtime /s"] = time.time()-self.start
        self.result = ToeholdResult(self.trigger_sets,
                                    *final_result,
                                    self.meta)
        self.result.names = self.names # make sure to use property setter
        self.pool.close()
        self.pool.join()
        self.pool.clear()

    def _worker(self,
                object trigger_sets_chunk = np.empty(shape=(1,0), dtype=str),
                object conc_sets_chunk = np.empty(shape=(1,0), dtype=np.float64)):
        
        cdef:
            Py_ssize_t i,j
            dict strands
            list tubes = [nupack.Tube(strands = {**self.const_strands,
                                                  **{nupack.Strand(trigger_sets_chunk[i,j], name=trigger_sets_chunk[i,j]) : conc_sets_chunk[i,j]
                                                    for j in range(trigger_sets_chunk.shape[1])}},
                                       complexes=nupack.SetSpec(max_size=self.max_size),
                                       name = str(i)) # make unique IDs for tubes -> non-unique IDs makes numpy throw an error from NUPACK
                           for i in range(trigger_sets_chunk.shape[0])]
            object tube_result

        with _Timer("nupack"):
            tube_result = nupack.tube_analysis(tubes=tubes,
                                            compute=("sample",),
                                            options={'num_sample': self.n_samples,},
                                            model=self.model)
        
        
        ###########################################################################################################################
        
        cdef:
            (int, int) result_shape = (5, trigger_sets_chunk.shape[0]) # each subarray corresponds to a single an array of activation by trigger
            np.float64_t [::1,:] result = np.empty(
                    shape = result_shape, # (5 for activation, rbs, aug, post, stand. err.; num tubes)
                    dtype = np.float64,
                    order = "F"
                )
        
        #   object tube_result_vals = map(lambda tube: tuple(tube.complex_concentrations.items()), tube_result.tubes.values())
            list tube_result_vals = [tuple(tube.complex_concentrations.items()) for tube in tube_result.tubes.values()]

            Py_ssize_t tube_index, comp_index, sample_index, pos_index
            double tube_activation, tube_rbs_activation, tube_aug_activation, tube_post_aug_activation
            float active_ths_count, active_rbs_count, active_aug_count, active_post_augs
            tuple tube_data
            object comp
            double conc
            list sample_objects
            list samples
            str sample
            list split_sample
            list comp_strands
            list ths_positions
            int ths_pos_len
            float total_ths_count
            Py_ssize_t pos
            str ths_struct
            (bint, bint, bint) unbinding
            double sum_w_squared

        # TODO: prevent constant type conversions between python and cython types, e.g. indices
        # remember that Py_ssize_t counts as c-int so much be converted to py-ints when indexing -> bad!

        with _Timer("processing"):
            for tube_index in range(trigger_sets_chunk.shape[0]):

                tube_data = tube_result_vals[tube_index] # next(tube_result_vals)
                
                tube_activation = 0
                tube_rbs_activation = 0
                tube_aug_activation = 0
                tube_post_aug_activation = 0
                tube_variance = 0
                for comp_index in range(len(tube_data)):
                    
                    comp, conc = tube_data[comp_index]
                    samples = [s.dp() for s in tube_result[comp].sample[:self.n_samples]] # limit num to n_samples (due to bug Lucas found in NUPACK)

                    comp_strands =  [str(s) for s in comp.strands]
                    ths_positions = [i for i in range(len(comp_strands)) if self.ths==comp_strands[i]]
                    ths_pos_len = len(ths_positions)
                    total_ths_count = ths_pos_len * self.n_samples # the total number of ths in all samples of this complex

                    if total_ths_count != 0:
                        active_ths_count = 0
                        active_rbs_count = 0
                        active_aug_count = 0
                        active_post_augs = 0
                    
                        for sample_index in range(self.n_samples):
                            sample = samples[sample_index] # next(samples)
                            split_sample = sample.split("+")

                            for pos_index in range(ths_pos_len):
                                pos = ths_positions[pos_index]
                                ths_struct = split_sample[pos]
                            
                                unbinding = (self._rbs_exposed(ths_struct),
                                             self._aug_exposed(ths_struct),
                                             self._post_aug_exposed(ths_struct))

                                if unbinding[0] == True and unbinding[1] == True and unbinding[2] == True:
                                    active_ths_count += 1
                                if unbinding[0]:
                                    active_rbs_count += 1
                                if unbinding[1]:
                                    active_aug_count += 1
                                if unbinding[2]:
                                    active_post_augs += 1
                                
                        
                        # add active fraction, weighted by complex concentration
                        tube_activation += active_ths_count / total_ths_count * conc
                        tube_rbs_activation += active_rbs_count / total_ths_count * conc
                        tube_aug_activation += active_aug_count / total_ths_count * conc
                        tube_post_aug_activation += active_post_augs / total_ths_count * conc
                        tube_variance += (active_ths_count / total_ths_count) * (1 - active_ths_count / total_ths_count) / self.n_samples * conc # npq weighted by conc


                # fraction of THSs out of the total THSs
                result[0, tube_index] = tube_activation / self.ths_conc
                result[1, tube_index] = tube_rbs_activation / self.ths_conc
                result[2, tube_index] = tube_aug_activation / self.ths_conc
                result[3, tube_index] = tube_post_aug_activation / self.ths_conc
                result[4, tube_index] = sqrt(tube_variance / self.ths_conc)

        return <np.ndarray[np.float64_t, ndim=2]> np.asarray(result)

    # TODO: use memviews instead
    # N.B. the following sections test for structure attributes via DPP
    # Maybe speed could be improved by using a memoryview of the c-contig [:,::1] np.ndarray nupack.Structure.matrix()
    # or perhaps even faster using nupack.Structure.view() which returns a numpy array of pairlist indices
    # or perhaps even faster by accessing the underlying np.uint32_t memoryview using Structure.values.cast(memoryview)
    # this is 1D so is both C and F continguous, aka [::1,::1]
    # however, then you must consider how to get the indices of the required sections --> maybe the 1D Structure.nicks ndarray?
    # may or may not be worth it in terms of effort per performance
    # perhaps str types are never needed in processing: just directly interface with nupack C++???

    @cython.profile(False)
    cdef inline bint _rbs_exposed(self, str ths_struct):
        """Test if rbs is fully unbound"""
        cdef str rbs_struct = ths_struct[self._rbs_slice[0]:self._rbs_slice[1]]
        cdef int rbs_len = self._rbs_slice[1] - self._rbs_slice[0]
        return rbs_struct == ("." * rbs_len)

    @cython.profile(False)
    cdef inline bint _aug_exposed(self, str ths_struct):
        """Test if aug is fully unbound"""
        return ths_struct[self.aug_position:self.aug_position+3] == "..."
    
    @cython.profile(False)
    cdef inline bint _post_aug_exposed(self, str ths_struct):
        """Test for binding to previous regions based of DPP notation"""
        cdef str post_aug = ths_struct[self.aug_position+3:]
        if post_aug == "":  # handling for THSs without linkers?! <-- just in case this is a thing
            return True
        return post_aug.count("(") >= post_aug.count(")")


@cython.auto_pickle(True)
cdef class ToeholdResult:
    """
    Data container for the result of a :class:`ToeholdTest`.

    Not intended to be constructed manually.

    .. note:: All activation and unbinding values are given as decimals, not percentages.

    Attributes
    ----------
    trigger_sets : Collection[Collection[str]]
        The trigger sets that were tested.
    names : Collection[str | Collection[str]]
        The names of each trigger set in :attr:`trigger_sets`.
        If a collection of names is given for each trigger set,
        they will be joined with '+' signs.
        This can also be set through the names parameter of :class:`ToeholdTest`
        or passed to an argument to one of the methods defined here.

    activation : np.ndarray[np.float64]
        An array of the activation by each trigger set.
    rbs_unbinding : np.ndarray[np.float64]
        An array of the RBS unbinding by each trigger set.
    aug_unbinding : np.ndarray[np.float64]
        An array of the AUG unbinding by each trigger set.
    post_aug_unbinding : np.ndarray[np.float64]
        An array of the post-AUG unbinding by each trigger set.
    activation_se : np.ndarray[np.float64]
        The standard error of each value in the :attr:`activation` attribute array.

    specificity : np.ndarray[np.float64]
        The level of specificity to the highest activating trigger set.
    specificity_se : np.ndarray[np.float64]
        The standard error of the :attr:`specificity` attribute.

    target_index : int
        The index of the trigger_sets with the highest activation probability.
    target_set : Collection[str]
        The item in the trigger_sets with the highest activation probability.
    target : str | Collection[str]
        Same as target_set, but if the trigger_set only contains a single RNA,
        this is the RNA sequence.
    target_name : str
        The name of the trigger_set with the highest activation probability.
    target_activation : float
        The switch activation probability with the target trigger set.
    target_activation_se : float
        The standard error of the switch activation probability with the target trigger set.

    unix_created : datetime.datetime
        UNIX timestamp of the creation of the :class:`ToeholdResult`.
    date : str
    meta : dict
    pretty_meta : str

    See Also
    --------
    ToeholdTest
        A class to test different trigger sets against the toehold switch
        for activation probability, in order to find its specificity.
    """

    cdef:
        readonly object trigger_sets
        object _names

        readonly np.ndarray activation
        readonly np.ndarray rbs_unbinding
        readonly np.ndarray aug_unbinding
        readonly np.ndarray post_aug_unbinding
        readonly np.ndarray activation_se

        readonly double specificity
        readonly double specificity_se # standard error 

        readonly object target
        readonly object target_set
        readonly Py_ssize_t target_index
        readonly str target_name
        readonly double target_activation
        readonly double target_activation_se

        readonly datetime.datetime unix_created
        readonly str date

        readonly dict meta
        readonly str pretty_meta
        
    def __init__(self,
                 object trigger_sets,
                 np.ndarray[np.float64_t, ndim=1] activation,
                 np.ndarray[np.float64_t, ndim=1] rbs_unbinding,
                 np.ndarray[np.float64_t, ndim=1] aug_unbinding,
                 np.ndarray[np.float64_t, ndim=1] post_aug_unbinding,
                 np.ndarray[np.float64_t, ndim=1] activation_se,
                 dict meta = {}):

        self.trigger_sets = trigger_sets
        if len(trigger_sets)==0 :
            self.trigger_sets.append("None")

        self.activation = activation
        self.rbs_unbinding = rbs_unbinding
        self.aug_unbinding = aug_unbinding
        self.post_aug_unbinding = post_aug_unbinding
        self.activation_se = activation_se

        self.target_index = np.argmax(self.activation)
        self.target = self.trigger_sets[self.target_index]
        if len(self.target) == 1:
            self.target = self.target[0]
        self.target_activation = self.activation[self.target_index]
        self.target_activation_se = self.activation_se[self.target_index]

        self.specificity, self.specificity_se = specificity_ci(activation, activation_se)

        self.unix_created = datetime.datetime.now()
        self.meta = meta

        self.meta["Target sequence"] = self.target
        self.meta["Target name"] = self.target_name
        self.meta["Specificity %"] = self.specificity*100
        self.meta["Specificity SE"] = self.specificity_se*100

        self.pretty_meta = "\n".join(
                [f"{key}: {value}" for key, value in self.meta.items()]
            )
        self.date = self.unix_created.strftime("%b %-d %Y at %H:%M:%S")

    @property
    def names(self):
        return self._names

    @names.setter
    def names(self, value: Collection[Union[str, Collection[str]]]):
        if value is None:
            return
        self._names = value
        if value[self.target_index] is not str:
            self.target_name = str(value[self.target_index][0]) # must force cast with Python since dtype might be np.str_
        else:
            self.target_name = "+".join(value[self.target_index])

    def __str__(self):
        return self.prettify()

    def tabulate(self,
                 dp: Optional[int] = None,
                 names: Collection[Union[str,Collection[str]]] = None,
                 show_unbinding: bool = True) -> prettytable.PrettyTable:
        """
        Create a :class:`prettytable.PrettyTable` of the result.
        
        Parameters
        ----------
        dp : int, optional
            The decimal places to limit the display to.
        names : Collection[str | Collection[str]], optional
            The names of each trigger set in :attr:`trigger_sets`.
        show_unbinding : bool, default = True
            Whether to display the individual unbinding probability
            of the RBS, start codon and post-start codon region
        """
        cdef object table = prettytable.PrettyTable()
        if names is not None or self._names is not None:
            if names is None:
                names = self._names
            # assert hasattr(names, "__len__"), "names must have a __len__ method"
            names = ["+".join(name)
                     if not isinstance(name, str)
                     else name
                     for name in names]
            table.add_column("Name", names)
        table.add_column("Sequence", ["+".join(s) for s in self.trigger_sets])
        table.add_column("Activation %", self.activation*100)
        if <bint> show_unbinding:
            table.add_column("RBS unbinding %", self.rbs_unbinding*100)
            table.add_column("AUG unbinding %", self.aug_unbinding*100)
            table.add_column("Post-AUG unbinding %", self.post_aug_unbinding*100)
        table.add_column("Standard Error", self.activation_se*100)
        table.align = "l"
        table.sortby = "Activation %"
        table.reversesort = True
        if dp is not None:
            table.float_format = f".{dp}"
        return table

    def prettify(self,
                 dp: Optional[int] = None,
                 names: Collection[Union[str,Collection[str]]] = None,
                 show_unbinding: bool = True) -> str:
        """
        Alias to str(self). Get the result as its :class:`prettytable.PrettyTable`
        in string form, with added metadata.
        
        Parameters
        ----------
        dp : int, optional
            The decimal places to limit the display to.
        names : Collection[str | Collection[str]], optional
            The names of each trigger set in :attr:`trigger_sets`.
        show_unbinding : bool, default = True
            Whether to display the individual unbinding probability
            of the RBS, start codon and post-start codon region
        """
        return f"{self.date}\n\n{self.pretty_meta}\n\n{self.tabulate(dp, names, show_unbinding)}"
    
    def to_csv(self,
               dp: Optional[int] = None,
              names: Collection[Union[str,Collection[str]]] = None,
              show_unbinding: bool = True,
              **kwargs) -> str:
        """
        Get the result as a CSV with added metadata.

        Parameters
        ----------
        dp : int, optional
            The decimal places to limit the display to.
        names : Collection[str | Collection[str]], optional
            The names of each trigger set in :attr:`trigger_sets`.
        show_unbinding : bool, default = True
            Whether to display the individual unbinding probability
            of the RBS, start codon and post-start codon region
        **kwargs
            Extra arguments to be passed to :func:`csv.writer`
            via the :class:`PrettyTable.prettytable` instance.
        """
        cdef str csv_meta = self.pretty_meta.replace(": ", ",")
        return (
            f"{self.date}\n\n{csv_meta}\n\n{self.tabulate(dp, names, show_unbinding).get_csv_string(**kwargs)}"
        )
    
    def to_html(self,
                dp: Optional[int] = None,
                names: Collection[Union[str,Collection[str]]] = None,
                show_unbinding: bool = True,
                **kwargs) -> str:
        """
        Get the result as a HTML table.
        
        Parameters
        ----------
        dp : int, optional
            The decimal places to limit the display to.
        names : Collection[str | Collection[str]], optional
            The names of each trigger set in :attr:`trigger_sets`.
        show_unbinding : bool, default = True
            Whether to display the individual unbinding probability
            of the RBS, start codon and post-start codon region
        **kwargs
            Extra arguments to be passed to the
            :class:`PrettyTable.prettytable` instance.
        """
        return self.tabulate(dp, names, show_unbinding).get_html_string(**kwargs)

    def to_json(self, 
                dp: Optional[int] = None,
                names: Collection[Union[str,Collection[str]]] = None,
                show_unbinding: bool = True,
                **kwargs) -> str:
        """
        Get the result as a JSON string.
        
        Parameters
        ----------
        dp : int, optional
            The decimal places to limit the display to.
        names : Collection[str | Collection[str]], optional
            The names of each trigger set in :attr:`trigger_sets`.
        show_unbinding : bool, default = True
            Whether to display the individual unbinding probability
            of the RBS, start codon and post-start codon region
        **kwargs
            Extra arguments to be passed to the
            :class:`PrettyTable.prettytable` instance.
        """
        return self.tabulate(dp, names, show_unbinding).get_json_string(**kwargs)


@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
cpdef inline (double, double) specificity_ci(np.float64_t [:] activation, np.float64_t [:] activation_se):
    """Use uncertainty operations to find the confidence interval, returning (specificity, specificity standard error)."""
    cdef:
        double largest = DBL_MIN
        double second_largest = 0
        double largest_error
        double second_largest_error
        double best, max_, min_, se
    for i in range(activation.shape[0]):
        if activation[i] > largest:
            second_largest = largest # shift largest down to second largest
            second_largest_error = largest_error
            largest = activation[i]
            largest_error = activation_se[i]
        elif activation[i] > second_largest:
            second_largest = activation[i]
            second_largest_error = activation_se[i]
    best = 1 - second_largest / largest # aka (1st - 2nd)/1st
    max_ = 1 - (second_largest - second_largest_error) / (largest + largest_error)
    min_ = 1 - (second_largest + second_largest_error) / (largest - largest_error)
    se = (max_ - min_) / 2
    if se < 0 or se > 1: # force nonsensical SE to be full uncertainty
        se = float("inf")
    return (best, se)

def copy_model(model: nupack.Model) -> nupack.Model:
    """Copy a :class:`nupack.Model`."""
    return nupack.Model().from_json(model.to_json())
