#!/usr/bin/env python

import datetime
import configparser
import csv
import os
import sys
from collections import defaultdict

import pandas as pd

CURRENTPATH = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config.read("datalocations.conf")


class DateException(Exception):
    pass


class TimeData(object):
    def __init__(self, date, dataname, lookback=100):
        self.date = self.dateParse(date)
        self.lookback = lookback
        self.dataname = dataname
        self.path = self.localPath()
        self.link = self.remotePath(2019)

    @staticmethod
    def dateParse(date) -> datetime:
        if isinstance(date, (int, float)):
            return datetime.datetime.strptime(str(int(date)), "%Y%m%d")
        elif isinstance(date, str):

            try:
                if len(date) == 8:
                    if '/' in date:
                        return datetime.datetime.strptime(date, "%m/%d/%y")
                    else:
                        return datetime.datetime.strptime(date, "%Y%m%d")
                elif len(date) == 10:
                    if "-" in date:
                        return datetime.datetime.strptime(date, "%Y-%m-%d")
                    else:
                        return datetime.datetime.strptime(date, "%m/%d/%Y")
                else:
                    return datetime.datetime.strptime(date, "%b %d, %Y")
            except ValueError:
                raise DateException("Could not parse date format")
        elif isinstance(date, datetime.datetime):
            return date
        else:
            raise DateException("Could not determine date datatype")

    @staticmethod
    def columnFormat(columns):
        tranform = lambda x: str(x).replace(' ', '_').lower()
        return map(tranform, columns)

    def localPath(self) -> str:
        return os.path.join(
            CURRENTPATH,
            *config.get(self.dataname, "localpath").split(",")
        )

    def remotePath(self, *args) -> str:
        return config.get(self.dataname, "link").format(*args)

    @property
    def lastDate(self) -> datetime:
        if self.path.split(".")[-1] == "csv":
            with open(self.path) as csvfile:
                rowreader = csv.DictReader(csvfile)
                alldates = [self.dateParse(row["date"]) for row in rowreader]

                return max(alldates)

    def pullNewData(self) -> pd.DataFrame:
        newData = pd.read_html(self.link)[1]
        newData.columns = self.columnFormat(newData.columns)
        newData.date = newData.date.apply(self.dateParse)

        return newData[newData.date > self.lastDate]

    def loadExistingData(self) -> pd.DataFrame:
        data = pd.read_csv(self.path)
        data.date = data.date.apply(self.dateParse)

        return data[data.date <= self.date].tail(self.lookback)

    def refreshLocal(self):
        if self.date > self.lastDate:
            newData = self.pullNewData()
            newData.to_csv(self.path, mode='a', header=False, index=False)

    def frame(self) -> pd.DataFrame:
        self.refreshLocal()
        return self.loadExistingData()



if __name__ == "__main__":

    data = TimeData(20190615, 'treasuryyields')
    print(data.frame().to_string(index=False))
