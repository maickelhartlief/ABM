###### statistics.py
# Runs the statistical tests that checks whether there is a significant difference 
# between different network implementations in the model.
####

# Internal imports
from utils import make_path

# External imports
from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt
import scikit_posthocs as sp
from numpy import mean, std, add

# Initialize string to store results in
results = ''

# List of condition names to loop over
conditions = ["not_connected",  "holme_kim", "homophily", "fully_connected"]

# Initialize dictionary with voter percentages per condition
voter_dict = {}

# List of categories for the chi square test
cat_list = []

# List of list of number of agents in each category per condition
nr_per_cat = []

# Loop over all result files
for condition in conditions:
    
    # Make a list of every line
    file = open(make_path(condition) + condition)
    lines = file.read().splitlines()
    file.close()

    # Convert values to float
    floats = list(map(float, lines[:-4]))
    results += f"For {condition}, the mean is {mean(floats):.3f} with SD {std(floats):.3f}\n"
    
    # Save all the values for the voter data, i.e. all except the last 4 lines, in a dict
    voter_dict[condition] = floats

    # Save the data for the 4 categories of political participation
    nr_list = []
    for line in lines[-4:]:
        cat, nr = line.split(":")

        # List of categories for the chi square test
        if cat not in cat_list:
            cat_list.append(cat)
        
        # Convert list to float to strip of additional characters
        nr_list.append(float(nr))
    nr_per_cat.append(nr_list)    

# Descriptives
contig_table = pd.DataFrame(nr_per_cat, columns = cat_list, index = conditions)
results += f"The number of agents per category is: \n {contig_table}\n\n"

# ANOVA
if (stats.levene(*list(voter_dict.values())).pvalue) <= 0.05:
    # For unequally distributed variances
    results += (f"The assumption of equality of variances was not met;" 
                f"{stats.levene(*list(voter_dict.values())).pvalue}\n"
                f"Therefore, the results of the Kruskal-Wallis test were:" 
                f"{stats.kruskal(*list(voter_dict.values()))}\n\n")
    post_hoc = sp.posthoc_dunn((list(voter_dict.values())), p_adjust = 'bonferroni')
    post_hoc.columns = conditions
    post_hoc.index = conditions
    results += f"Post hoc testing reveals the following: \n {post_hoc}\n"
else:
    results += (f"The assumption of equality of variances was met.\n"
                f"Therefore, the results of the ANOVA test were:"
                f"{stats.f_oneway(*list(voter_dict.values()))} \n"
                f"The results of the post-hoc are the following: _\n")

# Chi square
test_chi, p_val_chi, dof = stats.chi2_contingency(nr_per_cat)[0:3]
results += (f"The results of the Pearson's chi test for independence are as follows: \n"
            f"Test statistic:{test_chi} \nP-value: {p_val_chi}, degrees of freedom: {dof}\n\n")

posthoc_chi = pd.DataFrame(columns = conditions, index = conditions)
for index, cond_1 in enumerate(nr_per_cat):
    for index_2, cond_2 in enumerate(nr_per_cat):
        p_val_chi = stats.chi2_contingency([cond_1, cond_2])[1]
        posthoc_chi.iloc[index, index_2] = p_val_chi
results += f"A pairwise comparison of the groups reveals the following: \n{posthoc_chi}"



## Visualizations 

# Set location
path = make_path('statistics')

# Textfile with results
with open(f'{path}statistical_tests', 'w') as file:
    file.write(results)

# Boxplot
fig = plt.figure(figsize = (10, 10))
ax = fig.add_subplot(111)
ax.boxplot(list(voter_dict.values()), labels = conditions, showmeans = True)
ax.set_title("Voter percentage across conditions", fontsize = 20)
plt.savefig(f"{path}results_boxplot.png")
plt.clf()

# Stacked bar chart
def reform_list(nr_per_cat, idx):
    return [int(nr_list[idx]) for nr_list in nr_per_cat]

apathetic = reform_list(nr_per_cat, 0)
spectators = reform_list(nr_per_cat, 1)
transitionals = reform_list(nr_per_cat, 2)
gladiators = reform_list(nr_per_cat, 3)

plt.bar(conditions, apathetic, color = "tan")
plt.bar(conditions, spectators, bottom = apathetic, color = "orange" )
spec_apath = add(spectators, apathetic).tolist()
plt.bar(conditions, transitionals, bottom = spec_apath, color = "pink")
plt.bar(conditions, gladiators, bottom = add(spec_apath, transitionals).tolist(), color = "red")
plt.title("Bar plot of number of agents in each political participation category")
plt.savefig(f"{path}barplot.png")
plt.clf()
