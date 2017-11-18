from test_machine_performance import PerformanceTester

tester = PerformanceTester()

tester.plot_map()

score = tester.evaluate([5972.315,	9.68889], [-0.9999969,	7.4362545E-4,	0.0023726204])

print 'score: ',score