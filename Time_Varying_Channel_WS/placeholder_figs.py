import matplotlib.pyplot as plt

ds = range(1000,1500,10)
ECC = []

for d in ds:
    if d > 1400:
        ECC.append(80)
    elif d > 1300:
        ECC.append(40)
    elif d > 1200:
        ECC.append(20)
    else:
        ECC.append(0)

plt.figure()
plt.plot(ds,ECC)
plt.title("Placeholder")
plt.ylabel("ECC value")
plt.xlabel("Distance")



plt.figure()
plt.scatter([1000,1100,1200,1300,1400],[100,200,300,400,500],marker="o")
plt.scatter([1000,1100,1200,1300,1400],[300,600,900,1200,1500])
plt.title("Placeholder")
plt.ylabel("Power Consumed (J)")
plt.xlabel("Distance")
plt.show()

