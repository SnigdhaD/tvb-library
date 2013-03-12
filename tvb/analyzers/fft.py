# -*- coding: utf-8 -*-
#
#
# (c)  Baycrest Centre for Geriatric Care ("Baycrest"), 2012, all rights reserved.
#
# No redistribution, clinical use or commercial re-sale is permitted.
# Usage-license is only granted for personal or academic usage.
# You may change sources for your private or academic use.
# If you want to contribute to the project, you need to sign a contributor's license. 
# Please contact info@thevirtualbrain.org for further details.
# Neither the name of Baycrest nor the names of any TVB contributors may be used to endorse or 
# promote products or services derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY BAYCREST ''AS IS'' AND ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, 
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL BAYCREST BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS 
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY 
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
#
#

"""
Calculate an FFT on a TimeSeries datatype and return a FourierSpectrum datatype.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import numpy
from scipy import signal as sp_signal
from tvb.basic.logger.builder import get_logger
#TODO: Currently built around the Simulator's 4D timeseries -- generalise...
import tvb.datatypes.time_series as time_series
import tvb.datatypes.spectral as spectral
import tvb.basic.traits.core as core
import tvb.basic.traits.types_basic as basic
import tvb.basic.traits.util as util


LOG = get_logger(__name__)
SUPPORTED_WINDOWING_FUNCTIONS = ("hamming", "bartlett", "blackman", "hanning")




class FFT(core.Type):
    """
    A class for calculating the FFT of a TimeSeries object of TVB and returning
    a FourierSpectrum object. A segment length and windowing function can be
    optionally specified. By default the time series is segmented into 1 second
    blocks and no windowing function is applied.
    """
    
    time_series = time_series.TimeSeries(
        label = "Time Series",
        required = True,
        doc = """The timeseries to which the FFT is to be applied.""")
    
    segment_length = basic.Float(
        label = "Segment(window) length (ms)",
        default = 1000.0,
        required = False,
        doc = """The timeseries can be segmented into equally sized blocks
            (overlapping if necessary). The segement length determines the
            frequency resolution of the resulting power spectra -- longer
            windows produce finer frequency resolution.""")
    
    window_function = basic.String(
        label = "Windowing function",
        default = None,
        required = False,
        doc = """Windowing functions can be applied before the FFT is performed.
             Default is None, possibilities are: 'hamming'; 'bartlett';
            'blackman'; and 'hanning'. See, numpy.<function_name>.""")
    
    
    def evaluate(self):
        """
        Calculate the FFT of time_series broken into segments of length
        segment_length and filtered by window_function.
        """
        cls_attr_name = self.__class__.__name__+".time_series"
        self.time_series.trait["data"].log_debug(owner = cls_attr_name)
        
        tpts = self.time_series.data.shape[0]
        time_series_length = tpts * self.time_series.sample_period
        
        #Segment time-series, overlapping if necessary
        nseg = int(numpy.ceil(time_series_length / self.segment_length))
        if nseg > 1:
            seg_tpts = self.segment_length / self.time_series.sample_period
            overlap = ((seg_tpts * nseg) - tpts) / (nseg-1)
            starts = [max(seg*(seg_tpts - overlap), 0) for seg in range(nseg)]
            segments =  [self.time_series.data[start:start+seg_tpts]
                         for start in starts]
            segments = [segment[:, :, :, numpy.newaxis] for segment in segments]
            time_series = numpy.concatenate(segments, axis=4)
        else:
            self.segment_length = time_series_length
            time_series = self.time_series.data[:, :, :, numpy.newaxis]
            seg_tpts = time_series.shape[0]
        
        LOG.debug("Segment length being used is: %s" % self.segment_length)
        
        #Base-line correct the segmented time-series  
        time_series = sp_signal.detrend(time_series, axis=0)
        util.log_debug_array(LOG, time_series, "time_series")
        
        #Apply windowing function
        if self.window_function is not None:
            if self.window_function not in SUPPORTED_WINDOWING_FUNCTIONS:
                LOG.error("Windowing function is: %s" % self.window_function)
                LOG.error("Must be in: %s" % str(SUPPORTED_WINDOWING_FUNCTIONS))
            
            window_function = eval("".join(("numpy.", self.window_function)))
            window_mask = numpy.reshape(window_function(seg_tpts), 
                                        (seg_tpts, 1, 1, 1, 1))
            time_series = time_series * window_mask
        
        #Calculate the FFT
        result =  numpy.fft.fft(time_series, axis=0)
        nfreq = result.shape[0] / 2
        result = result[1:nfreq+1, :]
        util.log_debug_array(LOG, result, "result")
        
        spectra = spectral.FourierSpectrum(source = self.time_series, 
                                  segment_length = self.segment_length,
                                  window_function = self.window_function,
                                  array_data = result,
                                  use_storage = False)
        
        return spectra
    
    
    def result_shape(self, input_shape, segment_length, sample_period):
        """Returns the shape of the main result (complex array) of the FFT."""
        freq_len = (segment_length / sample_period) / 2.0
        freq_len = int(min((input_shape[0], freq_len)))
        nseg = max((1, int(numpy.ceil(input_shape[0] * sample_period / segment_length))))
        result_shape = (freq_len, input_shape[1], input_shape[2], input_shape[3], nseg)
        return result_shape
    
    
    def result_size(self, input_shape, segment_length, sample_period):
        """
        Returns the storage size in Bytes of the main result (complex array) of 
        the FFT.
        """
        result_size = numpy.prod(self.result_shape(input_shape, segment_length,
                                                   sample_period)) * 2.0 * 8.0 #complex*Bytes
        return result_size
    
    
    def extended_result_size(self, input_shape, segment_length, sample_period):
        """
        Returns the storage size in Bytes of the extended result of the FFT. 
        That is, it includes storage of the evaluated FourierSpectrum attributes
        such as power, phase, amplitude, etc.
        """
        result_shape = self.result_shape(input_shape, segment_length, sample_period)
        result_size = self.result_size(input_shape, segment_length, sample_period)
        extend_size = result_size #Main array
        extend_size = extend_size + 0.5 * result_size #Amplitude
        extend_size = extend_size + 0.5 * result_size #Phase
        extend_size = extend_size + 0.5 * result_size #Power
        extend_size = extend_size + 0.5 * result_size / result_shape[4] #Average power
        extend_size = extend_size + 0.5 * result_size / result_shape[4] #Normalised Average power
        extend_size = extend_size + result_shape[0] * 8.0 #Frequency
        return extend_size

