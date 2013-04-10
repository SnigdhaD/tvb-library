# -*- coding: utf-8 -*-
#
#
# TheVirtualBrain-Framework Package. This package holds all Data Management, and 
# Web-UI helpful to run brain-simulations. To use it, you also need do download
# TheVirtualBrain-Scientific Package (for simulators). See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2013, Baycrest Centre for Geriatric Care ("Baycrest")
#
# This program is free software; you can redistribute it and/or modify it under 
# the terms of the GNU General Public License version 2 as published by the Free
# Software Foundation. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details. You should have received a copy of the GNU General 
# Public License along with this program; if not, you can download it here
# http://www.gnu.org/licenses/old-licenses/gpl-2.0
#
#
"""
Created on Mar 20, 2013

.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
"""
import numpy
import unittest

from tvb.datatypes import time_series
from tvb_library_test.base_testcase import BaseTestCase
        
class TemporalCorrelationsTest(BaseTestCase):
    
    def test_timeseries(self):
        data = numpy.random.random((10, 10))
        dt = time_series.TimeSeries(data=data)
        self.assertEqual(dt.data.shape, (10, 10))
        self.assertEqual(dt.sample_period, 1.0)
        self.assertEqual(dt.sample_rate, 0.0)
        self.assertEqual(dt.start_time, 0.0)
        self.assertEqual(dt.time.shape, (0,))
        
        
    def test_timeserieseeg(self):
        data = numpy.random.random((10, 10))
        dt = time_series.TimeSeriesEEG(data=data)
        self.assertEqual(dt.data.shape, (10, 10))
        self.assertEqual(dt.labels_ordering, ['Time', 'EEG Sensor'])
        self.assertEqual(dt.sample_period, 1.0)
        self.assertEqual(dt.sample_rate, 0.0)
        self.assertTrue(dt.sensors is None)
        self.assertEqual(dt.start_time, 0.0)
        self.assertEqual(dt.time.shape, (0,))
        
        
    def test_timeseriesmeg(self):
        data = numpy.random.random((10, 10))
        dt = time_series.TimeSeriesMEG(data=data)
        self.assertEqual(dt.data.shape, (10, 10))
        self.assertEqual(dt.labels_ordering, ['Time', 'MEG Sensor'])
        self.assertEqual(dt.sample_period, 1.0)
        self.assertEqual(dt.sample_rate, 0.0)
        self.assertTrue(dt.sensors is None)
        self.assertEqual(dt.start_time, 0.0)
        self.assertEqual(dt.time.shape, (0,))
        
        
    def test_timeseriesregion(self):
        data = numpy.random.random((10, 10))
        dt = time_series.TimeSeriesRegion(data=data)
        self.assertEqual(dt.data.shape, (10, 10))
        self.assertEqual(dt.labels_ordering, ['Time', 'State Variable', 'Region', 'Mode'])
        self.assertEqual(dt.sample_period, 1.0)
        self.assertEqual(dt.sample_rate, 0.0)
        self.assertEqual(dt.start_time, 0.0)
        self.assertEqual(dt.time.shape, (0,))
        
        
    def test_timeseriessurface(self):
        data = numpy.random.random((10, 10))
        dt = time_series.TimeSeriesSurface(data=data)
        self.assertEqual(dt.data.shape, (10, 10))
        self.assertEqual(dt.labels_ordering, ['Time', 'State Variable', 'Vertex', 'Mode'])
        self.assertEqual(dt.sample_period, 1.0)
        self.assertEqual(dt.sample_rate, 0.0)
        self.assertEqual(dt.start_time, 0.0)
        self.assertEqual(dt.time.shape, (0,))
        
        
    def test_timeseriesvolume(self):
        data = numpy.random.random((10, 10))
        dt = time_series.TimeSeriesVolume(data=data)
        self.assertEqual(dt.data.shape, (10, 10))
        self.assertEqual(dt.labels_ordering, ['Time', 'X', 'Y', 'Z'])
        self.assertEqual(dt.sample_period, 1.0)
        self.assertEqual(dt.sample_rate, 0.0)
        self.assertEqual(dt.start_time, 0.0)
        self.assertEqual(dt.time.shape, (0,))  
        
        
def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TemporalCorrelationsTest))
    return test_suite


if __name__ == "__main__":
    #So you can run tests from this package individually.
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run(TEST_SUITE) 