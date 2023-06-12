import matplotlib.pyplot as plt

data = {
    '1':13,
    '2':9,
    '3':21,
    '4':17,
    '5':15,
    '6':24,
    '7':0.076,
    '8':15,
    '9':12,
    '10':70
}

question = list(data.keys())
time = list(data.values())

fig = plt.figure(figsize=(10, 15))
plt.bar(question, time, color='maroon', width=0.4)

plt.xlabel('Question')
plt.ylabel('Time in seconds')
plt.title('Query execution time')
plt.show()