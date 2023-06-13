import numpy as np
import matplotlib.pyplot as plt

""" Questions
1. 10 najpopularnijih zanrova u odnosu na njihovu prosecnu ocenu i broj pojavljivanja
2. Koliko epizoda imaju 10 serija sa najvecom prosecnom ocenom
3. Koja sezona je najbolje ocenjena u okviru serije?
4. Kolika je razlika prosecne ocene serije u odnosu na prosecnu ocenu njenih epizoda?
5. Koji reditelj je snimio najvise filmova?
6. Top 5 glumaca u odnosu na broj snimljenih filmova
7. Osobe koje istovremeno obavljaju funkciju reditelja i glumca, lista filmova
8. Koja kombinacija zanra je najpopularnija?
9. Koliki je broj umrlih osoba u 21. veku?
10. Koliki je ukupan broj minuta koje su proveli glumci na sceni sa najvisom prosecnom ocenom i bar 10 snimljenih
    filmova?

"""

data = [
    [13.253, 9.522, 32.789, 17.264, 38.941, 55.741, 33.159, 4.598, 3.159, 187.600],
    [13.253, 1.500, 11.402, 0.008, 4.272, 6.228, 0.052, 4.598, 1.559, 8.003]
]

X = np.arange(10)
fig, ax = plt.subplots()

v1_query_time_bar = ax.bar(X, data[0], color='r', width=0.25)
v2_query_time_bar = ax.bar(X + 0.25, data[1], color='g', width=0.25)

ax.set_ylabel('Seconds')
ax.set_xlabel('Queries')
ax.set_xticks(X + 0.50 / 2)
ax.set_xticklabels(X+1)

ax.legend((v1_query_time_bar[0], v2_query_time_bar), ('v1', 'v2'))
plt.savefig("query_plot.png")
plt.show()
