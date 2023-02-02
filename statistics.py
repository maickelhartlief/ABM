from scipy import stats
import pandas as pd
import os
import matplotlib.pyplot as plt
import scikit_posthocs as sp

# VOTER PRECENTAGE: ANOVA
#os.chdir("results/")
df_dict = {}
conditions = ["not_connected",  "holme_kim", "homophily","fully_connected"]
for condition in conditions:
    df = pd.read_table(f'results/{condition}.txt',delim_whitespace=True, engine = "python", header = None, skipfooter = 4)
    df_dict[condition]  = df.iloc[:, 0].values.tolist()
    # with open('filename.txt', 'r') as f:
    # last_line = f.readlines()[-4]
    #print(df_dict[condition])

#homophily_voters = pd.read_table('homophily.txt',delim_whitespace=True, engine = "python", header = None, skipfooter = 5)
#homophily_voters = pd.read_table('holme_kim.txt',delim_whitespace=True, engine = "python", header = None, skipfooter = 5)

# test assumption of normality
# if stats.shapiro(homophily_voters).pvalue < 0.05:
#     print("not normal")
# else:
#     #anova
#print(*list(df_dict.values()))

if (stats.levene(*list(df_dict.values())).pvalue) < 0.05:
    # For unequally distributed variances
    print(f"The assumption of equality of variances was not met; {stats.levene(*list(df_dict.values())).pvalue} \n"
    f"Therefore, the results of the Kruskal-Wallis test were: {stats.kruskal(*list(df_dict.values()))}")
    post_hoc = sp.posthoc_dunn((list(df_dict.values())), p_adjust = 'bonferroni')
    post_hoc.columns = conditions
    post_hoc.index = conditions
    print(f"Post hoc testing reveals the following: \n {post_hoc}")
else:
    print(f"The assumption of equality of variances was met.\n"
    f"Therefore, the results of the ANOVA test were: {stats.f_oneway(*list(df_dict.values()))} \n"
    f"The results of the post-hoc are the following: _")#{sp.posthoc_dunn(*list(df_dict.values())), p_adjust = 'bonferroni'}")
    # TODO there should be a post hoc test here as well


fig = plt.figure(figsize = (10, 10))
ax = fig.add_subplot(111)

ax.boxplot(list(df_dict.values()), labels=conditions, showmeans= True)
ax.set_title("Voter percentage across conditions", fontsize= 20)
plt.savefig(f"results/results_boxplot.png")
plt.clf()

# Chi square
