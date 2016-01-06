#from ROOT import TTree, TFile
#from nympy import zeros
from getpass import getpass
import mysql.connector as sql
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from datetime import datetime
from cPickle import dump, load
import sys

if len(sys.argv) == 2 and sys.argv[1] == 'fetch':
    con   = sql.connect(user='alcap', password=getpass('DB Password:'),
                        host='muon.npl.washington.edu', database='alcap')
    cur   = con.cursor()
    query = ('SELECT run, TIMESTAMPDIFF(SECOND, starttime, stoptime), '
             'starttime, stoptime, nblock, size, target FROM R15b '
             'WHERE stoptime IS NOT NULL '
             'ORDER BY run ASC')
    cur.execute(query)

    runs, dts, starts, stops, nblocks, sizes = [], [], [], [], [], []
    blockrates, datarates = [], []
    tmat, tthick = [], []
    for run, dt, start, stop, nblock, size, targ in cur:
        runs.append(run)
        dts.append(dt)
        starts.append(start)
        stops.append(stop)
        nblocks.append(nblock)
        sizes.append(size)
        blockrates.append(nblock/dt)
        datarates.append(size/dt/2**20)
    dump((runs,dts,starts,stops,nblocks,sizes,blockrates,datarates,tmat,tthick),
         open('runinfo.p', 'w'))


runs,dts,starts,stops,nblocks,sizes,blockrates,datarates,tmat,tthick = load(open('runinfo.p', 'r'))

# TEMPORARY
with open('timesincelastrun.csv', 'w') as ofile:
    for r, ti, tj in zip(runs[1:], starts[1:], stops[:-1]):
        ofile.write(str(r)+','+str(ti)+','+str(ti-tj)+'\n')
exit()

n = len(runs)
pos = [0.3, 0.1, 0.65, 0.8]

plt.figure(figsize=(40, 6))
layout = GridSpec(1, 2, width_ratios=[1,20])

ax0 = plt.subplot(layout[1])
plt.plot_date(starts[-n:], nblocks[-n:], 'ro')
plt.xlabel('Start time')
plt.ylabel('Block count')
plt.xticks(rotation=25)
color='red'
ax0.yaxis.label.set_color(color)
ax0.spines['left'].set_color(color)
ax0.tick_params(axis='y', color=color)
[i.set_color(color) for i in plt.gca().get_yticklabels()]

ax0.twinx()
ax = plt.gca()
plt.plot_date(starts[-n:], datarates[-n:], 'go')
plt.ylabel('Data rate (MB/s)')
ax.yaxis.set_ticks_position('left')
ax.yaxis.set_label_position('left')
ax.spines['left'].set_position(('axes', -0.035))
color='green'
ax.yaxis.label.set_color(color)
ax.spines['left'].set_color(color)
ax.tick_params(axis='y', color=color)
[i.set_color(color) for i in plt.gca().get_yticklabels()]

ax0.twinx()
ax = plt.gca()
plt.plot_date(starts[-n:], [t/60. for t in dts[-n:]], 'bo')
plt.ylabel('Run length (min)')
ax.yaxis.set_ticks_position('left')
ax.yaxis.set_label_position('left')
ax.spines['left'].set_position(('axes', -0.06))
color='blue'
ax.yaxis.label.set_color(color)
ax.spines['left'].set_color(color)
ax.tick_params(axis='y', color=color)
[i.set_color(color) for i in plt.gca().get_yticklabels()]

# Force every day to get a tick mark
ax.xaxis.get_major_locator().intervald[3] = [1]
# Add axis to top with ticks for run numbers
xmin, xmax, _, _ = plt.axis()
plt.twiny().spines['left'].set_visible(False)
runticklocs = [((dt - datetime(1,1,1)).total_seconds()/(24.*60.*60.) - xmin)/(xmax-xmin)
               for dt in starts[0::50]]
runticklabs = [str(r) for r in runs][0::50]
print len(runticklocs), len(runticklabs)
plt.xticks(runticklocs, runticklabs, rotation=90)

plt.savefig('r15btrend.pdf', orientation='landscape')
