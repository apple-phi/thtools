# cython: language_level=3
# cython: cdivision=True
# cython: profile=True
# cython: linetrace=True
# cython: initializedcheck=False
# cython: embedsignature=True

# distutils: define_macros=CYTHON_TRACE_NOGIL=1
# distutils: define_macros=NPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION

from typing import Collection, Generator, Sequence

import os
import time
import datetime

import psutil
import pathos
import nupack
import prettytable
import numpy as np

cimport numpy as np
cimport cython
from cpython cimport datetime
from libc.float cimport DBL_MIN
from libc.math cimport sqrt, fabs

USE_TIMER = False

cdef class Timer:
    """Basic class for timing tests"""
    cdef:
        double start
        double end
        double elapsed
        unicode name
    def __init__(self, unicode name=""):
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
    """A class to test different trigger sets against the ths in the prescence of any const RNAs"""
    cdef:
        # init
        readonly unicode ths
        readonly double ths_conc
        readonly (size_t, size_t) rbs_position
        readonly object trigger_sets
        readonly object conc_sets
        readonly list const_rna
        readonly list const_concs

        public object model

        # setup
        readonly double start
        readonly Py_ssize_t aug_position
        readonly list chunked_trigger_sets
        readonly list chunked_conc_sets
        readonly dict const_strands
        readonly object pool
        readonly dict meta

        # run
        readonly int max_size
        readonly int n_samples
        readonly int n_nodes
        readonly int n_chunks

        # output
        readonly ToeholdResult results
        public object names
    
    def __init__(self,
                 dict ths, # {ths: ths_conc}
                 slice rbs_position,
                 object trigger_sets: Collection[Collection[str]] = np.empty(shape=(0,0), dtype=str), # in form [set1, set2, set3, ...]
                 object conc_sets: Collection[Collection[float]] = np.empty(shape=(0,0), dtype=np.float64), # in same shape as trigger_sets
                 dict const_rna = {}, # {RNA:conc, RNA:conc, etc ...}
                 object model: nupack.Model = nupack.Model()):
        
        # set inputs as local attributes
        self.ths, self.ths_conc = list(ths.items())[0]
        self.rbs_position = rbs_position.start, rbs_position.stop
        self.trigger_sets = trigger_sets
        self.conc_sets = conc_sets
        self.const_rna, self.const_concs = list(const_rna.keys()), list(const_rna.values())
        self.model = model

        self.ths = self.ths.upper()
    
    cpdef ToeholdResult run(self,
                            int max_size,
                            int n_samples = 100,
                            int n_nodes = os.cpu_count()):
        
        self.max_size = max_size
        self.n_samples = n_samples
        self.n_nodes = n_nodes
        self.n_chunks = os.cpu_count()
        
        self._setup()
        
        cdef:
            object chunked_results
            np.ndarray final_results

        if self.chunked_trigger_sets != []: # support for testing only the ths + constants
            chunked_results = self.pool.map(self._worker,
                                            self.chunked_trigger_sets,
                                            self.chunked_conc_sets,
                                            chunksize=1)                                            
            final_results = np.concatenate(chunked_results, axis=1)
            # assert np.asarray(final_results, dtype=np.float64).shape==(5,len(self.trigger_sets))
        else:
            final_results = self._worker()

        self.meta["Runtime /s"] = time.time()-self.start

        self.results = ToeholdResult(self.trigger_sets,
                                    *final_results,
                                    self.meta)
        self.results.names = self.names
        return self.results
        
    def generate(self,
                 int max_size,
                 int n_samples = 100,
                 int n_nodes = os.cpu_count(),
                 int n_chunks = os.cpu_count()) -> Generator[ChunkResult]:
        
        self.max_size = max_size
        self.n_samples = n_samples
        self.n_nodes = n_nodes
        self.n_chunks = n_chunks
        
        self._setup()

        cdef:
            list chunked_results
            np.ndarray chunk
            np.ndarray final_results 

        if self.chunked_trigger_sets != []: # support for testing only the ths + constants
            chunked_results = []
            for chunk in self.pool.imap(self._worker, self.chunked_trigger_sets,self.chunked_conc_sets, chunksize=1):
                yield ChunkResult(*chunk)
                chunked_results.append(chunk)
            final_results = np.concatenate(chunked_results, axis=1)
            # assert np.asarray(final_results, dtype=np.float64).shape==(5,len(self.trigger_sets))
        else:
            final_results = self._worker()
            yield ChunkResult(*final_results)

        self.meta["Runtime /s"] = time.time()-self.start

        self.results = ToeholdResult(self.trigger_sets,
                                     *final_results,
                                     self.meta)
        self.results.names = self.names


    cdef void _setup(self) except *:
        cdef:
            Py_ssize_t i, c
            object trig_arr
            object conc_arr

        # timer
        self.start = time.time()
    
        # locate aug -> this must be done before safety checks
        for i in range(self.rbs_position[1], len(self.ths)):
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
                                    nupack.Strand(self.const_rna[c],name = self.const_rna[c]) : self.const_concs[c]
                                    for c in range(len(self.const_rna))
                                    }
                                }
        
        # create worker pool
        self.pool = pathos.multiprocessing.ProcessPool(nodes=self.n_nodes)
        
        # set NUPACK cache
        nupack.config.cache = psutil.virtual_memory().available * 1e-9

        # store meta
        self.meta = {"THS"                              :self.ths,
                     "THS concentration"                :self.ths_conc,
                     "RBS"                              :self.ths[self.rbs_position[0]:self.rbs_position[1]],
                     "# tests"                          :len(self.trigger_sets),
                     "Constant RNAs"                    :self.const_rna,
                     "Concentrations of constant RNAs"  :self.const_concs,
                     "Temperature /°C"                  :self.model.temperature-273.15,
                     "Max. complex size"                :self.max_size,
                     "Sample number"                    :self.n_samples}

        # safety checks
        assert np.asarray(self.trigger_sets).shape == np.asarray(self.conc_sets).shape, f"shape mismatch between trigger sets and trigger concentrations ({np.asarray(self.trigger_sets).shape} vs. {np.asarray(self.conc_sets).shape}"
            

    def _worker(self,
                object trigger_sets_chunk = np.empty(shape=(1,0), dtype=str),
                object conc_sets_chunk = np.empty(shape=(1,0), dtype=np.float64)):
        """Takes a chunk of trigger_sets and conc_sets and returns complexes and their concentrations"""
        
        cdef Py_ssize_t i,j
        cdef dict strands

        cdef list tubes = [nupack.Tube(strands = {**self.const_strands,
                                                  **{nupack.Strand(trigger_sets_chunk[i,j], name=trigger_sets_chunk[i,j]) : conc_sets_chunk[i,j]
                                                    for j in range(trigger_sets_chunk.shape[1])}},
                                       complexes=nupack.SetSpec(max_size=self.max_size),
                                       name = str(i)) # make unique IDs for tubes -> non-unique IDs makes numpy throw an error from NUPACK
                           for i in range(trigger_sets_chunk.shape[0])]
        
        
        cdef object tube_result
        with Timer("nupack"):
            tube_result = nupack.tube_analysis(tubes=tubes,
                                            compute=("sample",),
                                            options={'num_sample': self.n_samples,},
                                            model=self.model)
        
        
        ###########################################################################################################################
        
        cdef (int, int) results_shape = (5, trigger_sets_chunk.shape[0])

        cdef np.float64_t [::1,:] results = np.empty(
                    shape = results_shape, # (5 for activations, rbs, aug, post, stand. err.; num tubes)
                    dtype = np.float64,
                    order = "F"
                )

        
        # cdef object tube_result_vals = map(lambda tube: tuple(tube.complex_concentrations.items()), tube_result.tubes.values())
        cdef list tube_result_vals = [tuple(tube.complex_concentrations.items()) for tube in tube_result.tubes.values()]

        cdef:
            Py_ssize_t tube_index, comp_index, sample_index, pos_index
            double tube_activation, tube_rbs_activation, tube_aug_activation, tube_post_aug_activation
            float active_ths_count, active_rbs_count, active_aug_count, active_post_augs
            tuple tube_data
            object comp
            double conc
            list sample_objects
            list samples
            unicode sample
            list split_sample
            list comp_strands
            list ths_positions
            int ths_pos_len
            float total_ths_count
            Py_ssize_t pos
            unicode ths_struct
            (bint, bint, bint) exposures
            double sum_w_squared

        # TODO: prevent constant type conversions between python and cython types, e.g. indices
        # remember that Py_ssize_t counts as c-int so much be converted to py-ints when indexing -> bad!

        with Timer("processing"):
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
                            
                                exposures = (self._rbs_exposed(ths_struct),
                                             self._aug_exposed(ths_struct),
                                             self._post_aug_exposed(ths_struct))

                                if exposures[0] == True and exposures[1] == True and exposures[2] == True:
                                    active_ths_count += 1
                                if exposures[0]:
                                    active_rbs_count += 1
                                if exposures[1]:
                                    active_aug_count += 1
                                if exposures[2]:
                                    active_post_augs += 1
                                
                        
                        # add active fraction, weighted by complex concentration
                        tube_activation += active_ths_count / total_ths_count * conc
                        tube_rbs_activation += active_rbs_count / total_ths_count * conc
                        tube_aug_activation += active_aug_count / total_ths_count * conc
                        tube_post_aug_activation += active_post_augs / total_ths_count * conc
                        tube_variance += active_ths_count / total_ths_count * (1 - active_ths_count / total_ths_count) / self.n_samples * conc

                        
                
                # fraction of THSs out of the total THSs
                results[0,tube_index] = tube_activation / self.ths_conc
                results[1,tube_index] = tube_rbs_activation / self.ths_conc
                results[2,tube_index] = tube_aug_activation / self.ths_conc
                results[3,tube_index] = tube_post_aug_activation / self.ths_conc
                results[4,tube_index] = sqrt(tube_variance / self.ths_conc)


        return <np.ndarray[np.float64_t, ndim=2]> np.asarray(results)

    # TODO: use memviews
    # N.B. the following sections test for structure attributes via DPP
    # Maybe speed could be improved by using a memoryview of the [:,::1] np.ndarray nupack.Structure.matrix()
    # or perhaps even faster using nupack.Structure.view() which returns a numpy array of pairlist indices
    # or perhaps even faster by accessing the underlying np.uint32_t memoryview using Structure.values.cast(memoryview)
    # this is 1D so is both C and F continguous, aka [::1,::1]
    # however, then you must consider how to get the indices of the required sections --> maybe the 1D Structure.nicks ndarray?
    # may or may not be worth it in terms of effort per performance
    # perhaps str/unicode types are never needed in processing: just directly interface with nupack C++???

    cdef inline bint _rbs_exposed(self, unicode ths_struct):
        """Test if rbs is fully unbound"""
        cdef unicode rbs_struct = ths_struct[self.rbs_position[0]:self.rbs_position[1]]
        cdef int rbs_len = self.rbs_position[1] - self.rbs_position[0]
        return rbs_struct == ("." * rbs_len)
    
    cdef inline bint _aug_exposed(self, unicode ths_struct):
        """Test if aug is fully unbound"""
        return ths_struct[self.aug_position:self.aug_position+3] == "..."
    
    cdef inline bint _post_aug_exposed(self, unicode ths_struct):
        """Test for binding to previous regions based of DPP notation"""
        cdef unicode post_aug = ths_struct[self.aug_position+3:]
        if post_aug == "":  # handling for THSs without linkers?! <-- just in case this is a thing
            return True
        return post_aug.count("(") >= post_aug.count(")")

@cython.auto_pickle(True)
cdef class ChunkResult:
    cdef:
        readonly np.ndarray activations
        readonly np.ndarray rbs_exposures
        readonly np.ndarray aug_exposures
        readonly np.ndarray post_aug_exposures
        readonly np.ndarray standard_errors

        readonly double specificity
        readonly double se # standard error 

    def __init__(self,
                 np.ndarray[np.float64_t, ndim=1] activations,
                 np.ndarray[np.float64_t, ndim=1] rbs_exposures,
                 np.ndarray[np.float64_t, ndim=1] aug_exposures,
                 np.ndarray[np.float64_t, ndim=1] post_aug_exposures,
                 np.ndarray[np.float64_t, ndim=1] standard_errors):

        self.activations = activations
        self.rbs_exposures = rbs_exposures
        self.aug_exposures = aug_exposures
        self.post_aug_exposures = post_aug_exposures
        self.standard_errors = standard_errors

        self.specificity, self.se= confidence_interval(activations, standard_errors)

    def __str__(self):
        return f"{self.__repr__()} containing the results of {len(self.activations)} trigger sets (specificity of {self.specificity*100}%)"

    def __add__(self, ChunkResult res):
        return <ChunkResult>ChunkResult(np.concatenate((self.activations, res.activations)),
                                        np.concatenate((self.rbs_exposures, res.rbs_exposures)),
                                        np.concatenate((self.aug_exposures, res.aug_exposures)),
                                        np.concatenate((self.post_aug_exposures, res.post_aug_exposures)),
                                        np.concatenate((self.standard_errors, res.standard_errors)),
                                        )

@cython.auto_pickle(True)
cdef class ToeholdResult (ChunkResult):

    cdef:
        readonly object trigger_sets
        readonly datetime.datetime unix_created
        readonly dict meta

        readonly unicode pretty_meta
        readonly unicode date

        public object names
        
    def __init__(self,
                 object trigger_sets,
                 np.ndarray[np.float64_t, ndim=1] activations,
                 np.ndarray[np.float64_t, ndim=1] rbs_exposures,
                 np.ndarray[np.float64_t, ndim=1] aug_exposures,
                 np.ndarray[np.float64_t, ndim=1] post_aug_exposures,
                 np.ndarray[np.float64_t, ndim=1] standard_errors,
                 dict meta = {}):

        if len(trigger_sets)==0 :
            self.trigger_sets = ["None"]
        else:
            self.trigger_sets = trigger_sets
        super().__init__(activations,
                         rbs_exposures,
                         aug_exposures,
                         post_aug_exposures,
                         standard_errors)

        self.unix_created = datetime.datetime.now()
        self.meta = meta

        self.meta["Specificity %"] = self.specificity*100
        self.meta["Standard error"] = self.se*100

        self.pretty_meta = "\n".join([f"{key}: {value}" for key, value in self.meta.items()])
        self.date = self.unix_created.strftime("%d/%m/%Y at %H:%M:%S")


    def __add__(self, ToeholdResult other):
        """unfinished"""
        cdef set shared_meta = self.meta.keys() & other.meta.keys()
        return ToeholdResult.from_chunk(super().__add__(other),
                                        trigger_sets = np.concatenate((self.trigger_sets, other.trigger_sets)),
                                        meta = {key: self.meta[key] for key in shared_meta})

    def __str__(self):
        return self.prettify()

    def prettify(self, names: Collection[Sequence] = None) -> str:
        return f"{self.date}\n\n{self.pretty_meta}\n\n{self.tabulate(names)}"
    
    def to_csv(self, names: Collection[Sequence] = None, **kwargs) -> str:
        csv_meta = self.pretty_meta.replace(": ", ",")
        return f"{self.date}\n\n{csv_meta}\n\n{self.tabulate(names).get_csv_string(**kwargs)}"
    
    def to_html(self, names: Collection[Sequence] = None, **kwargs) -> str:
        return self.tabulate(names).get_html_string(**kwargs)

    def to_json(self, names: Collection[Sequence] = None, **kwargs) -> str:
        return self.tabulate(names).get_json_string(**kwargs)

    def tabulate(self, names: Collection[Sequence] = None) -> prettytable.PrettyTable:
        cdef object table = prettytable.PrettyTable()
        if names is not None or self.names is not None:
            if names is None:
                names = self.names
            assert hasattr(names, "__len__"), "names must have a __len__ method"
            if len(names) > 0:
                if type(names)!=str:
                    names = ["+".join(name) for name in names]
                table.add_column("Name", names)
        table.add_column("Sequence", ["+".join(s) for s in self.trigger_sets])
        table.add_column("Activation %", self.activations*100)
        table.add_column("RBS exposure %", self.rbs_exposures*100)
        table.add_column("AUG exposure %", self.aug_exposures*100)
        table.add_column("Post-AUG exposure %", self.post_aug_exposures*100)
        table.add_column("Standard error %", self.standard_errors*100)
        table.align = "l"
        table.sortby = "Activation %"
        table.reversesort = True
        return table

    @classmethod
    def from_chunk(cls,
                   ChunkResult chunk,
                   object trigger_sets,
                   dict meta = {}):

        return  cls(trigger_sets,
                    chunk.activations,
                    chunk.rbs_exposures,
                    chunk.aug_exposures,
                    chunk.post_aug_exposures,
                    meta=meta)


# @cython.boundscheck(False)  # Deactivate bounds checking
# @cython.wraparound(False)   # Deactivate negative indexing.
# cpdef inline double get_specificity (np.float64_t [:] activations) nogil:
#     """Calculate True Positive Rate(TPR) ± standard error"""
#     cdef:
#         double largest = DBL_MIN
#         double second_largest = 0
#     for i in range(activations.shape[0]):
#         if activations[i] > largest:
#             largest = activations[i]
#         elif activations[i] > second_largest:
#             second_largest = activations[i]
#     return 1 - (second_largest / largest)
# tpr = get_specificity #TPR (true positive rate) -> alias for analysis.get_specificity


@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
cpdef inline (double, double) confidence_interval(np.float64_t [:] activations, np.float64_t [:] standard_errors) nogil:
    """Use uncertainty operations to find CI, returning (best, SE)"""
    cdef:
        double largest = DBL_MIN
        double second_largest = 0
        double largest_error
        double second_largest_error
    for i in range(activations.shape[0]):
        if activations[i] > largest:
            largest = activations[i]
            largest_error = standard_errors[i]
        elif activations[i] > second_largest:
            second_largest = activations[i]
            second_largest_error = standard_errors[i]
    best = 1 - second_largest / largest # aka (1st - 2nd)/1st
    max_ = 1 - (second_largest - second_largest_error) / (largest + largest_error)
    min_ = 1 - (second_largest + second_largest_error) / (largest - largest_error)
    se = <double> fabs(max_ - min_) / 2
    return (best, se)

