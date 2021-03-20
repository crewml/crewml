# -*- coding: utf-8 -*-
"""
Created on Sat Aug 22 12:46:43 2020

@author: cybel
"""

import itertools
import datetime
import pytz
import pandas as pd
import calendar


timezone1 = pytz.timezone("America/New_York")
atl = timezone1.localize(datetime.datetime(2020, 1, 16, 10, 0, 0, 0))
timezone2 = pytz.timezone("Pacific/Honolulu")
hnl = timezone2.localize(datetime.datetime(2020, 1, 16, 22, 0, 0, 0))


print("time difference=", hnl-atl)


def calculate(x, y):
    return x*2, y*3


df = pd.DataFrame({'a': [1, 2, 3], 'b': [2, 3, 4]})
print(df)

# df["A1"], df["A2"] = zip(*df["a","b"].map(calculate))

df["NewCol1"], df["NewCol2"] = zip(
    *df.apply(lambda x: calculate(x['a'], x['b']), axis=1))

print(df)

x = 2
temp = str(x).zfill(3)
print()


def calculateFltTime(x, y, z):

    if str(y) == "nan" or str(z) == "nan":
        return
    print("x=", x, "y=", y, "z=", z)
    flt_dt = datetime.datetime.strptime(x, "%m/%d/%Y")

    y = str(int(y)).zfill(4)
    z = str(int(z)).zfill(4)
    print("y=", y, type(y), "z=", z)
    print(y[2:4])
    # org_hm= pd.to_datetime(y, format='%H%M')
    # dest_hm= pd.to_datetime(z, format='%H%M')

    dt1 = datetime.datetime(flt_dt.year, flt_dt.month,
                            flt_dt.day, int(y[0:2])-1, int(y[2:4]), 0, 0)
    dt2 = datetime.datetime(flt_dt.year, flt_dt.month,
                            flt_dt.day, int(z[0:2])-1, int(z[2:4]), 0, 0)

    tot_days = calendar.monthrange(flt_dt.year, flt_dt.month)[1]
    print("tot_days=", tot_days)

    if dt1 > dt2:
        if tot_days == flt_dt.day:
            month = flt_dt.month+1
            day = 1
        else:
            month = flt_dt.month
            day = flt_dt.day+1

        print("month=", month, "day=", day)
        dt2 = datetime.datetime(flt_dt.year, month, day,
                                int(z[0:2])-1, int(z[2:4]), 0, 0)

    print("time diff=", dt2-dt1)


calculateFltTime("1/31/2020", 2020, 1900)

bases = ["ATL", "MSP", "EWR"]
temp1 = list(itertools.combinations(bases, 2))
