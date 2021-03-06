import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
from texttable import Texttable
from datetime import datetime
import calendar
from Plotting import *



# returns the file name with the file path
def get_file_path(dimensions, nb_days, table_name, with_label_number = False):
    return "files/" + get_filename(dimensions, nb_days, table_name, with_label_number)

# computes the file name
def get_filename(dimensions, nb_days, table_name, with_label_number = False):
    days = str(nb_days) + "days" if nb_days > -1 else "alldays"
    description = "labelnb" + table_name  if with_label_number else table_name
    return "_".join([description, "_".join(dimensions), days]) + ".txt"

# Reads a file
def read_and_clean(filename, dimensions, sorting_dimensions=[], ascending=True):
    df = pd.read_csv(filename, sep='\t', header=None)
    names = list(dimensions)
    names.extend(['Count', "Output"])
    df.columns = names
    df = df.fillna("Other")

    # order
    if len(sorting_dimensions) > 0:
        df = df.sort_values(by=sorting_dimensions, ascending=ascending)

    return df


## Splitting and grouping per dimensions

# split into 2 df, one aggregated per day, the other per hour.
# Note: it cannot be done with split_dimensions because it doesnt use the same group (the aggregation
# per hour is actually on the average of the days)
def split_day_hour(df):
    df_by_day = group_by_label_sum(df, ["day"])
    df_by_day = compute_ratio(df_by_day)
    df_by_hour = group_by_label_average(df, "hour")
    df_by_hour = compute_ratio(df_by_hour)
    return [df_by_day, df_by_hour]

# split into several data frames aggregated per each dimension
def split_dimensions(df, dimensions,sortingLabels = "", ascending= True):
    groups = [group_by_label_sum(df, dimension, sortingLabels, ascending) for dimension in dimensions]
    return [compute_ratio(group) for group in groups]

# aggregate the data frame by summing
def group_by_label_sum(df, labels, sortingLabels = "", ascending= True): #, orderByLabel, )
    df_by_label = df.groupby(labels, as_index = False).sum()
    if len(sortingLabels) > 0 :
        df_by_label = df_by_label.sort_values(by=sortingLabels, ascending=ascending)
    return df_by_label

# aggregate the data frame by averaging
def group_by_label_average(df, labels, sortingLabels = "", ascending= True): #, orderByLabel, ascending)
    df_by_label = df.groupby(labels, as_index = False).mean()
    if len(sortingLabels) > 0 :
        df_by_label = df_by_label.sort_values(by=sortingLabels, ascending=ascending)
    return df_by_label


def ComputeRatio(x):
    return 100 * x[1] / x[0]


# Compute the ratio as a percentage from a df
def compute_ratio(df):
    df['Ratio'] = df[["Count","Output"]].apply(lambda x: ComputeRatio(x.values),axis = 1)
    return df

def compute_additional_columns(df):
    # Compute the columns relatives to date that are missing
    df['WeekDay'] = df[["Day"]].apply(lambda x: calendar.day_name[datetime.strptime(x.values[0], '%Y-%m-%d').weekday()], axis=1)
    df['WeekHour'] = df[["WeekDay", "Hour"]].apply(lambda x: str(x.values[0]) + str(x.values[1]), axis=1)
    df['DayAndHour'] = df[["Day", "Hour"]].apply(lambda x: str(x.values[0]) + str(x.values[1]), axis=1)
    return df

def compute_percentage_volumes(df, volumeLabel):
    df["Percentage "+ volumeLabel] = df[[volumeLabel]] * 100 / df[volumeLabel].sum()
    df["CumSum " + volumeLabel] = df[["Percentage "+ volumeLabel]].cumsum(axis=0)
    return df


## To display the main data

def get_average_std(df, desc, label):
    mean = df[label].mean()
    mean_string = '{:,.2f}'.format(mean) if mean < 1 else '{:,.0f}'.format(mean)

    std = df[label].std()
    std_string = 'undefined' if np.isnan(std) else'{:,.2f}'.format(std) if std < 1 else '{:,.0f}'.format(std)

    relative_std = '{:.1f}%'.format(100 * std / mean)
    return [desc, mean_string, std_string, relative_std]


def display(rows):
    t = Texttable()
    t.add_rows(rows)
    print(t.draw())

def display_rows_by_aggretor(df,aggregator,volume_label, values=[]):
    i = 0
    rows = [["", "Mean", 'Std', "Std/Mean percent"]]

    values = df[aggregator].unique() if len(values)== 0 else values
    for value in values:
        df_aggregator = df[df[aggregator] == value]
        df_aggregator_by_day = group_by_label_sum(df_aggregator, ["day"])
        df_aggregator_by_day = compute_ratio(df_aggregator_by_day)

        df_aggregator_by_hour = group_by_label_average(df_aggregator, ["hour"])
        df_aggregator_by_hour = compute_ratio(df_aggregator_by_hour)
        update_rows(rows, [(df_aggregator_by_day, "day"), (df_aggregator_by_hour, "hour")], [volume_label], str(value))

    display(rows)

def display_global_rows(tables, labels):
    rows = [["", "Mean", 'Std', "Std/Mean percent"]]
    return update_rows(rows, tables, labels)

def update_rows(rows, tables,labels, value=""):
    for label in labels:
        title = value + ": " + label if value != "" else label
        for (table, table_title) in tables:
            rows.append(get_average_std(table, title + " per " + table_title, label))
    return rows


# Select the top first rows
def select_top_rows(df, nb_rows):
    if nb_rows < 0 : # in case negative value, not cropped
        return [df,pd.DataFrame()]
    return [df[0:nb_rows], df[nb_rows:] ]

# Crop values that are lower than threshold.
def crop_values(df, label, threshold):
    return [df[df[label]>=threshold], df[df[label]<threshold] ]

def crop_and_group_others(df, criteria_label, volume_label, threshold=0, nb_rows=-1):
    [df_cropped_values, df_others_values] = crop_values(df, volume_label, threshold)
    [df_cropped_rows, df_others_rows] = select_top_rows(df_cropped_values, nb_rows)
    df_others = df_others_values.append(df_others_rows)

    if (len(df_others)==0):
        return df
    return df_cropped_rows.append({criteria_label:"Others", volume_label:df_others[volume_label].sum()}, ignore_index=True)


def get_top_values_for_aggregator(df, aggregator, volume_label, cropping_threshold=0, cropping_nb_rows=-1, subplot=0):
    df_grouped = group_by_label_sum(df, aggregator, volume_label, False)
    df_grouped = compute_percentage_volumes(df_grouped, volume_label)

    # Crop to restrain to the volumes higher than 1 percent of total volume
    df_crop = crop_and_group_others(df_grouped, aggregator, "Percentage " + volume_label, cropping_threshold,
                                    cropping_nb_rows)

    return [df_crop[aggregator].as_matrix(), df_crop]


def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)
