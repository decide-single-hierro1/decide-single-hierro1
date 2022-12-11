import seaborn as sns
import matplotlib.pyplot as plt
from . import metrics

def votingBarPlotAll(file):
    colors = sns.color_palette('pastel')[0:4]
    unstarted = metrics.unstartedVotings()
    started = metrics.startedVotings()
    finished = metrics.finishedVotings()
    closed = metrics.closedVotings()
    sns.barplot(x=['sin empezar', 'empezadas', 'finalizadas', 'cerradas'], y=[unstarted, started, finished, closed], palette=colors)
    plt.savefig(file)
    plt.clf()

def votingBarPlot(file, names, res):
    colors = sns.color_palette('pastel')[0:len(res)]

    sns.barplot(x=names, y=res, palette=colors)
    plt.savefig(file)
    plt.clf()

def votingPieChartAll(file):
    colors = sns.color_palette('pastel')[0:4]
    unstarted = metrics.unstartedVotings()
    started = metrics.startedVotings()
    finished = metrics.finishedVotings()
    closed = metrics.closedVotings()
    total = unstarted + started + finished + closed
    data = [unstarted/total, started/total, finished/total, closed/total]
    labels = ['sin empezar', 'empezadas', 'finalizadas', 'cerradas']
    plt.pie(data, labels=labels, colors=colors, autopct='%.0f%%')
    plt.savefig(file)
    plt.clf()

def votingPieChart(file, names, res):
    colors = sns.color_palette('pastel')[0:len(res)]
    plt.pie(res, labels=names, colors=colors, autopct='%.0f%%')
    plt.savefig(file)
    plt.clf()
