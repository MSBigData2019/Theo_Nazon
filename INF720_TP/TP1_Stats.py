import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.interpolate import BSpline
import numpy as np
import math as m
from scipy.stats import t
import scipy.stats as stats


plt.style.use('seaborn')

df = pd.read_csv("https://bitbucket.org/portierf/shared_files/downloads/invest.txt", sep = " ")

display(df.head(5))

# Add units
# Smoothen lines

graph = plt.plot(df['gnp'], df['invest'])

plt.xlabel("Gross National Product")

plt.ylabel("Investment")
plt.title("GNP vs. Investment")
plt.show()


# xnew = np.linspace(T.min(),T.max(),300) #300 represents number of points to make between T.min and T.max
# power_smooth = spline(T,power,xnew)
# x_new = np.linspace(df["gnp"].min(), df["gnp"].max(), 400)
# investment_smooth = BSpline(df["gnp"], df["invest"], x_new)
# plt.plot(xnew,power_smooth)
plt.show()

df["gnp"] = np.log(df["gnp"])
df["invest"] = np.log(df["invest"])

# Calcul des moyennes des Xi et des Yi
X_avg = np.average(df['gnp'])
Y_avg = np.average(df['invest'])

# Creation d'un vecteur de meme dimension que X et Y
I = np.ones(df['gnp'].shape)

# Appelons cov_X_Y le numerateur de theta_1
cov_X_Y = np.dot(df['gnp'] - np.multiply(X_avg, np.transpose(I)), df['invest'] - np.multiply(Y_avg, np.transpose(I)))

# Appelons var_X le denumerateur de theta_1
var_X = np.dot(np.transpose(df['gnp'] - np.multiply(X_avg, np.transpose(I))), df['gnp'] - np.multiply(X_avg, np.transpose(I)))

theta_1_chap = cov_X_Y/var_X

print("La valeur de theta_1 est : " + "{0:.5f}".format(theta_1_chap))

# Intercept Beta0
theta_0_chap = avg_invest - theta_1_chap * avg_gnp

print("La valeur de theta_0 est : " + "{0:.5f}".format(theta_0_chap))


n = df['invest'].shape[0]
sigma_chap_2 = 1/(n-2) * ((df['invest'] - theta_0 - theta_1 * df['gnp']) ** 2).sum()
print(sigma_chap_2)

V_theta_1 = sigma_chap_2 / var_X
print(V_theta_1)

t_stat = theta_1 / m.sqrt(V_theta_1)
print(theta_1 / m.sqrt(V_theta_1))

p_value = stats.t.sf(t_stat, df=13) * 2
print(p_value)

predicted_value_log = theta_0 + theta_1 * m.log(1000)
print(predicted_value_log)

print(m.exp(predicted_value))

# CI
x_new = m.log(1000)
quantile = 1.350

def ci_inf(x):
    return np.dot(np.transpose([1, x]), [theta_0, theta_1]) - quantile * (1 - 0.05/2) * m.sqrt(sigma_chap_2) * ((1 / n) * ((x - avg_gnp) ** 2) / var_X)

def ci_sup(x):
    return np.dot(np.transpose([1, x]), [theta_0, theta_1]) + quantile * (1 - 0.05/2) * m.sqrt(sigma_chap_2) * ((1 / n) * ((x - avg_gnp) ** 2) / var_X)

print(ci_inf(x_new), ci_sup(x_new))


# PI

def pi_sup(x):
    return np.dot(np.transpose([1, x]), [theta_0, theta_1]) + quantile * (1 - 0.05/2) * m.sqrt(sigma_chap_2) * (1 + (1 / n) * ((x - avg_gnp) ** 2) / theta_1_denum)

def pi_inf(x):
    return np.dot(np.transpose([1, x]), [theta_0, theta_1]) - quantile * (1 - 0.05/2) * m.sqrt(sigma_chap_2) * (1 + (1 / n) * ((x - avg_gnp) ** 2) / theta_1_denum)

print(pi_inf(x_new), pi_sup(x_new))


plt.scatter(df['gnp'], df['invest'], color = 'green')
x_reg = np.linspace(df['gnp'].min(), df['gnp'].max(), 500)
y_reg = theta_0 + theta_1 * x_reg
plt.plot(x_reg, y_reg)

sup_pi = list(map(pi_sup, x_reg))
inf_pi = list(map(pi_inf, x_reg))

sup_ci = list(map(ci_sup, x_reg))
inf_ci = list(map(ci_inf, x_reg))

# Shade the confidence interval
plt.fill_between(x_reg, inf_pi, sup_pi, color = '#539caf', alpha = 0.4, label = '95% CI')
# Label the axes and provide a title
plt.fill_between(x_reg, inf_ci, sup_ci, color = 'red', alpha = 0, label = '95% CI')


# Display legend


# https://www.datascience.com/blog/learn-data-science-intro-to-data-visualization-in-matplotlib
plt.show()