import matplotlib.pyplot as plt


def plot_df(df, x_label, y_label, title, show_std = False):
    plt.figure(figsize=(15, 10))
    plt.title(title, size=20)
    plt.plot(df[x_label], df[y_label], 'b')
    if show_std:
        update_plot_df_mean_std(plt, df, x_label, y_label)
    plt.xticks(rotation=60)

def update_plot_df_mean_std(plt, df, x_label, y_label):
    m = df[y_label].mean()
    s = df[y_label].std()
    df["mean"] = m
    df["mean+std"] = s + m
    df["mean-std"] = m - s
    plt.plot(df[x_label], df["mean"], 'r--')
    plt.plot(df[x_label], df["mean+std"], 'g--')
    plt.plot(df[x_label], df["mean-std"], 'g--')

def plot_pie_df(df, x_label, y_label,  title):
    plt.figure(figsize=(15, 10))
    plt.title(title, size=20)
    plt.pie(df[x_label], labels=df[y_label], autopct='%.0f%%')

def plot_pie_df_subplot(df, x_label, y_label,  title, subplot_position):
    plt.subplot(subplot_position)
    plt.title(title, size=20)
    plt.pie(df[x_label], labels=df[y_label], autopct='%.0f%%')

# Plot bars, not related to df
def plot_bar(x_values, y_values, title):
    plt.figure(figsize=(15, 10))
    plt.title(title, size=20)
    plt.bar(range(0,len(y_values)), y_values, tick_label = x_values)
    plt.xticks(rotation=60)

# Not working!!! must be debugged
def plot_bar2(df, x_label, y_label, title, show_std = False):
    plt.figure(figsize=(15, 10))
    plt.title(title, size=20)
    plt.bar(range(0,len(df[y_label])), df[y_label], tick_label = df[x_label])
    if show_std:
        update_plot_df_mean_std(plt, df, x_label, y_label)
    plt.xticks(rotation=60)