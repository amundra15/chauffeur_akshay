from test_machine_performance import PerformanceTester

tester = PerformanceTester()

score = tester.evaluate([299.41556,	-1493.6473], [0.77082264,	-0.6365625,	0.024910014])
score = score + tester.evaluate([1086.2275,-2127.1917],[0.820242,	-0.5720079,	0.0031751338])

print 'score: ',score

tester.plot_map()
