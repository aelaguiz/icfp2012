I spent a couple days trying to come up with goofy machine learning algorithms to find solutions for the icfp2012 competition. This is the result of that. The motivation was to try to find a totally unique way of solving the challenge.


Methods:
1) Baseline - Rule based regression
2) SVM Assisted Regression
	- Used manually solved maps to provide training data for a SVMs which were evolved by a GA
	- Used the best model from that data to "guide" regression - was used as the first method in a depth first search
3) GA Path Generation
	- Fixed length strings evolved by a GA with a custom fitness function that tries to encourage exploration of the map, modification of the environment, and a few other heuristics
4) GA Dynamic Length Path Generation
	- Same as #3 with varying length genomes and custom mutators

For most of these it was basically multivariate optimization attempting to simultaneously maximize score and minimize length. Best results were achived with SVM Assisted regression. Within the 150 second window was able to solve many of the contest maps to optimal or near optimal.  Truthfully the assisted regression method might actually be good enough for a submission if I went through and made it efficient - the code is quite lazy.

If I had more time to work on this I'd also add some neural network solutions. Also I would like to try some of the machine learning approaches with different goals (gathering highest value lambda) or even stage "situations" so the goal is to gather groups of nearby lambdas, and we optimize for that and let completion be a separate goal.

Hope someone else finds something interesting in this.
