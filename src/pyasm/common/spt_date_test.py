
import tacticenv

from pyasm.common import SPTDate
from dateutil import parser

#2.43680555556

import unittest

class DurationTest(unittest.TestCase):

    def test_duration(self):

        # intraday
        start = "2018-11-02 02:00:00"
        end =   "2018-11-02 08:00:00"

        diff = SPTDate.get_business_days_duration(start, end)
        expected =  0.25
        self.assertEqual(expected, diff)

        # intraday + 1
        start = "2018-11-05 18:00:00"
        end =   "2018-11-07 06:00:00"

        diff = SPTDate.get_business_days_duration(start, end)
        expected =  1.5
        self.assertEqual(expected, diff)


        # intraday + 1
        start = "2018-11-01 02:00:00"
        end =   "2018-11-02 08:00:00"

        diff = SPTDate.get_business_days_duration(start, end)
        expected =  1.25
        self.assertEqual(expected, diff)


        # friday to monday
        start = "2018-11-02 18:00:00"
        end =   "2018-11-05 06:00:00"

        diff = SPTDate.get_business_days_duration(start, end)
        expected =  0.5
        self.assertEqual(expected, diff)

        # monday to friday
        start = "2018-11-05 18:00:00"
        end =   "2018-11-09 06:00:00"

        diff = SPTDate.get_business_days_duration(start, end)
        expected =  3.5
        self.assertEqual(expected, diff)


        # saturday to monday
        start = "2018-11-03 18:00:00"
        end =   "2018-11-05 06:00:00"

        diff = SPTDate.get_business_days_duration(start, end)
        expected =  0.25
        self.assertEqual(expected, diff)


        # thursday to sunday
        start = "2018-11-01 18:00:00"
        end =   "2018-11-04 06:00:00"

        diff = SPTDate.get_business_days_duration(start, end)
        expected =  1.25
        self.assertEqual(expected, diff)


        # wednesday to next wednesday
        start = "2018-11-07 00:00:00"
        end =   "2018-11-14 00:00:00"

        diff = SPTDate.get_business_days_duration(start, end)
        expected =  5.0
        self.assertEqual(expected, diff)













if __name__ == '__main__':
    unittest.main()
