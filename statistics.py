from scipy import stats
import pandas as pd
import os
import matplotlib.pyplot as plt
import scikit_posthocs as sp

# VOTER PRECENTAGE: ANOVA
#os.chdir("results/")
voter_dict = {}
cond_cat_dict = {}
conditions = ["not_connected",  "holme_kim", "homophily","fully_connected"]
# result_path = 'results/' + network
#     if not os.path.exists(result_path):
#        os.makedirs(result_path)
#     result_path += '/'
cat_list = []
nr_per_cat = []
for condition in conditions:
    file = f'results/{condition}/{condition}'
    df = pd.read_table(file, delim_whitespace=True, engine = "python", header = None, skipfooter = 4)
    voter_dict[condition]  = df.iloc[:, 0].values.tolist()
    nr_list = []
    with open(file, 'r') as f:
        for line in (f.readlines() [-4:]):
            cat, nr = line.split(":")
            if cat not in cat_list:
                cat_list.append(cat)
            nr_list.append(float(nr))

    nr_per_cat.append(nr_list)


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
    # TODO there should be a post hoc test here as well


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
