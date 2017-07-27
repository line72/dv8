# start_poller

This script will begin to poll the Real time API for the BJCTA Max Bus
System every 30 seconds, and record all data to a local sqlite
database called `poller.db`.

Once events have been collected, you can run the other analysis tools
that utilize this database.

## Requirements

 * python 3
 * sqlalchemy
 * python-requests

# create_deviation_graph

This script reads from the `poller.db` and generates a pdf showing the
deviation of the buses from the schedule (on time performance). By
default, this will graph all the data in the database in one, very
large pdf.

You can optionally pass in a start and end day to have this only plot
a specific range. For example, if you only want to see July 20th,
then:

`python3 create_deviation_graph 20170720 20170720`

If you want to plot a range of multiple days, like July 19th-21st:

`python3 create_deivation_graph 20170719 20170721`

## Requirements
 
 * python 3
 * sqlalchemy
 * matplotlib
