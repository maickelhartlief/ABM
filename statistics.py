###### statistics.py
# 
####

# External imports
from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt
import scikit_posthocs as sp
import numpy as np

# List of condition names to loop over
conditions = ["not_connected",  "holme_kim", "homophily","fully_connected"]

# Initialize dictionary with voter percentages per condition
voter_dict = {}

# List of categories for the chi square test
cat_list = []

# List of list of number of agents in each category per condition
nr_per_cat = []

# Loop over all result files
for condition in conditions:
    file = f'results/{condition}/{condition}'

    # Make a list of every line
    lines = open(file).read().splitlines()

    # Convert values to float
    floats = list(map(float, lines[:-4]))
    # Save all the values for the voter data, i.e. all except the last 4 lines, in a dict
    voter_dict[condition] = floats#[:-4]

    # Save the data for the 4 categories of political participation
    nr_list = []
    for line in lines[-4:]:
        cat, nr = line.split(":")

        # List of categories for the chi square test
        if cat not in cat_list:
            cat_list.append(cat)
        # Convert list to float and then to int to strip of additional characters
        nr_list.append(float(nr))
    nr_per_cat.append(nr_list)

# ANOVA
if (stats.levene(*list(voter_dict.values())).pvalue) <= 0.05:
    # For unequally distributed variances
    print(f"The assumption of equality of variances was not met; {stats.levene(*list(voter_dict.values())).pvalue} \n"
    f"Therefore, the results of the Kruskal-Wallis test were: {stats.kruskal(*list(voter_dict.values()))}")
    post_hoc = sp.posthoc_dunn((list(voter_dict.values())), p_adjust = 'bonferroni')
    post_hoc.columns = conditions
    post_hoc.index = conditions
    print(f"Post hoc testing reveals the following: \n {post_hoc}")
else:
    print(f"The assumption of equality of variances was met.\n"
    f"Therefore, the results of the ANOVA test were: {stats.f_oneway(*list(voter_dict.values()))} \n"
    f"The results of the post-hoc are the following: _")#{sp.posthoc_dunn(*list(voter_dict.values())), p_adjust = 'bonferroni'}")


fig = plt.figure(figsize = (10, 10))
ax = fig.add_subplot(111)

ax.boxplot(list(voter_dict.values()), labels=conditions, showmeans= True)
ax.set_title("Voter percentage across conditions", fontsize= 20)
plt.savefig(f"results/results_boxplot.png")
plt.clf()

# # Chi square
test_chi, p_val_chi = stats.chi2_contingency(nr_per_cat)[0:2]
print(f"The results of the Pearson's chi test for independence are as follows: \n"
      f"Test statistic:{test_chi} \nP-value: {p_val_chi}")

posthoc_chi = pd.DataFrame(columns=conditions, index = conditions)
#print(nr_per_cat)
for index, cond_1 in enumerate(nr_per_cat):

    for index_2, cond_2 in enumerate(nr_per_cat):
        p_val_chi = stats.chi2_contingency([cond_1, cond_2])[1]
        posthoc_chi.iloc[index, index_2] = p_val_chi
print(f"A pairwise comparison of the groups reveals the following: \n{posthoc_chi}")

# Visualisation: stacked bar chart
def reform_list(nr_per_cat, idx):
    return [int(nr_list[idx]) for nr_list in nr_per_cat]

apathetic = reform_list(nr_per_cat, 0)
spectators = reform_list(nr_per_cat, 1)
transitionals = reform_list(nr_per_cat, 2)
gladiators = reform_list(nr_per_cat, 3)

plt.bar(conditions, apathetic, color = "tan")
plt.bar(conditions, spectators, bottom = apathetic, color = "orange" )
spec_apath = np.add(spectators, apathetic).tolist()
plt.bar(conditions, transitionals, bottom = spec_apath, color = "pink")
plt.bar(conditions, gladiators, bottom = np.add(spec_apath, transitionals).tolist(), color = "red")
plt.title("Bar plot of number of agents in each political participation category")
#plt.show()
plt.savefig(f"results/barplot.png")
plt.clf()
