
import seaborn as sns
penguins = sns.load_dataset("penguins")
sns.displot(penguins, x="flipper_length_mm")

