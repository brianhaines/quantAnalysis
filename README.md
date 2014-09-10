Time Series Analysis
=============

This project is intended to make use of the other projects that I have completed, namely my Stock Price Server. 

How it works
============

This project uses the Python's asyncio library to concurrently pull price histories from either my Stock Price Server or directly from my database. 

The returned time series are analysed using Python3.4's statistical stack: numpy, scipy, statsmodels(0.6.0), and matplotlib. 

Objectives
============

1. Test pairs of stocks for the tendency of their joint returns to behave in a mean reverting nature using tests for cointegration and stationarity.

2. Use the results of these tests to generate trade signals. e.g. If two stocks have shown a tendency to mean-revert and they are now at an extreme point.
