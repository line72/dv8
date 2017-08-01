# DV8 (Deviate)

(c) 2017 Marcus Dillavou <line72@line72.net>
https://github.com/line72/dv8

This is a set of simple scripts that uses the public real time tracking API
for the BJCTA Max Bus System at:

https://realtimebjcta.availtec.com/InfoPoint/swagger/docs/v1

This pulls down the information on all the buses every few seconds and
records it in a database, so that later on, we can run reports.

*All code is released under the MIT License*

## start_poller

This script will begin to poll the Real time API for the BJCTA Max Bus
System every 30 seconds, and record all data to a local sqlite
database called `poller.db`.

Once events have been collected, you can run the other analysis tools
that utilize this database.

### Requirements

 * python 3
 * sqlalchemy
 * python-requests

## create_graph

This script reads from the `poller.db` and generates a graph as a pdf. It can graph different variables for each route.

Currently, there are two graph types:

 - deviation: This graph shows the deviation of the buses from the
schedule (on time performance). By default, this will graph all the
data in the database in one, very large pdf called `deviation.pdf`
 - onboard: This graph shows how many riders are on the bus at any given time. By default, this will graph all the data in the database in one, very large pdf called `onboard.pdf`.

You can optionally pass in a start and end day to have this only plot
a specific range. For example, if you only want to see July 20th,
then:

`python3 create_graph deviation 20170720 20170720`

If you want to plot a range of multiple days, like July 19th-21st:

`python3 create_graph onboard 20170719 20170721`

### Requirements
 
 * python 3
 * sqlalchemy
 * matplotlib
