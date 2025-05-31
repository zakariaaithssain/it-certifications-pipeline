import seaborn as sns
from tqdm import tqdm
# for plots of costs and durations, I excluded unknown values (set to 0) so they don't affect the real results.
# you should call plt.tight_layout() and plt.show() after calling a method, except for plot_all().

class EDA:
    sns.set_theme()
    def __init__(self, data):
        self.data = data

    def nbre_certification_per_lvl_and_provider(self, axe, st = False, st_col = None): #in case integrated with st we use st = True
        axe.set_title('Number of Certifications per Level and Provider')
        axe.set_ylabel('Number of Certifications')
        sns.countplot(data = self.data, x = 'Level', hue = 'Provider', ax = axe)
        if st: st_col.pyplot(axe.figure)



    def avg_cost_per_lvl_and_provider(self, axe, st = False, st_col = None):
        axe.set_title(' AVG Cost of Certifications per Level and Provider')
        sns.barplot(data = self.data[self.data['Cost (USD)'] > 0], x = 'Level', y = 'Cost (USD)', hue = 'Provider', ax = axe, errorbar= None)
        if st: st_col.pyplot(axe.figure)

    def avg_duration_per_lvl_and_provider(self, axe, st = False, st_col = None):
        axe.set_title('AVG Exam Duration per Level and Provider')
        sns.barplot(data = self.data[self.data['Exam Duration (min)'] > 0], x= 'Level', y = 'Exam Duration (min)', hue = 'Provider', ax = axe, errorbar= None)
        if st: st_col.pyplot(axe.figure)


    def top_five_languages(self, axe, st = False, st_col = None):
        lang_exploded = self.data.assign(Language=self.data['Languages'].str.split(',')).explode('Language')
        lang_exploded['Language'] = lang_exploded['Language'].str.strip()
        top_langs = lang_exploded['Language'].value_counts().head(5)
        sns.barplot(x=top_langs.values, y=top_langs.index, ax = axe)
        axe.set_title('Top 5 Languages in Certifications')
        axe.set_xlabel('Number of Certifications')
        axe.set_ylabel('Languages')
        if st: st_col.pyplot(axe.figure)

    def cost_distribution(self, axe, st = False, st_col = None):
        axe.set_title('Distribution of Certifications Costs')
        axe.set_xlabel('Cost (USD)')
        axe.set_ylabel('Number of Certifications')
        sns.histplot(self.data[self.data['Cost (USD)'] > 0], x = 'Cost (USD)', kde=True, ax = axe)
        if st: st_col.pyplot(axe.figure)


    def duration_distribution(self, axe, st = False, st_col = None):
        axe.set_title('Distribution of Exams Durations')
        axe.set_xlabel('Duration (min)')
        axe.set_ylabel('Number of Certifications')
        sns.histplot(self.data[self.data['Exam Duration (min)'] > 0], x = 'Exam Duration (min)', kde = True, ax = axe)
        if st: st_col.pyplot(axe.figure)


    def cost_boxplot(self, axe, st = False, st_col = None):
        axe.set_title('Boxplot of Certifications Costs')
        sns.boxplot(data = self.data[self.data['Cost (USD)'] > 0], x = self.data['Provider'], y = self.data['Cost (USD)'], ax = axe, showfliers=True)
        sns.stripplot(data=self.data, x='Provider', y='Cost (USD)', color='red', size=4, jitter=True, alpha=0.5, ax = axe)
        if st: st_col.pyplot(axe.figure)



    def duration_boxplot(self, axe, st = False, st_col = None):
        axe.set_title('Boxplot of Exam Duration')
        sns.boxplot(data = self.data[self.data['Exam Duration (min)'] > 0], x = 'Provider', y = 'Exam Duration (min)', ax = axe, showfliers=True)
        sns.stripplot(data=self.data, x='Provider', y='Exam Duration (min)', color='red', size=4, jitter=True, alpha=0.5, ax = axe)
        if st: st_col.pyplot(axe.figure)

    def nbre_certification_per_domain(self, axe, st = False, st_col = None):
        domains = self.data.Domain.value_counts()
        sns.barplot(x= domains.values, y = domains.index, ax = axe)
        axe.set_title('Number of Certifications per Domain')
        axe.set_xlabel('Number of Certifications')
        axe.set_ylabel('Domain')
        if st: st_col.pyplot(axe.figure)

    def plot_all(self, directory_path):
        import matplotlib.pyplot as plt
        axes = [plt.subplots()[1] for _ in range(9)]
        methods_names = [method_name for method_name in dir(self) if callable(getattr(self, method_name))
                         and not method_name.startswith("__") and not method_name == 'plot_all']

        for (method_name, axe) in tqdm(zip(methods_names, axes)):
            getattr(self, method_name)(axe)
            plt.tight_layout()
            axe.figure.savefig(fr"{directory_path}\{method_name}.png", dpi=300, bbox_inches='tight')




