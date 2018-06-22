import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
from texttable import Texttable
from datetime import datetime
import calendar
from Plotting import *


# Compute the ratio as a percentage from a serie x
def ComputeRatio(x):
    return 100 * x[1]/x[0] 

def get_file_path(dimensions, nb_days, table_name, with_label_number = False):
    return "files/" + get_filename(dimensions, nb_days, table_name, with_label_number)

def get_filename(dimensions, nb_days, table_name, with_label_number = False):
    days = str(nb_days) + "days" if nb_days > -1 else "alldays"
    description = "labelnb" + table_name  if with_label_number else table_name
    return "_".join([description, "_".join(dimensions), days]) + ".txt"

# Reads a file
def read_and_clean(filename, label, label_aggregation, filtered_days, additional_columns = True):
    df = pd.read_csv(filename, sep='\t', header=None)
    if label_aggregation == "":
        df.columns = ['Day', 'Hour', 'Count', label]
    else:
        df.columns = ['Day', 'Hour', label_aggregation, 'Count', label]
    df = df.fillna("Other")

    # order
    df = df.sort_values(by=['Day', 'Hour'])

    # Filter on bad day
    df = df[~df.Day.isin(filtered_days)]

    if additional_columns :
        return compute_additional_columns(df, label)
    else :
        return df


def read_and_clean2(filename, dimensions, sorting_dimensions=[], ascending=True):
    df = pd.read_csv(filename, sep='\t', header=None)
    names = list(dimensions)
    names.extend(['Count', "Output"])
    df.columns = names
    df = df.fillna("Other")

    # order
    if len(sorting_dimensions) > 0:
        df = df.sort_values(by=sorting_dimensions, ascending=ascending)

    # Compute ratio (sales or click)
    # df['Ratio'] = df[["Count", "Output"]].apply(lambda x: ComputeRatio(x.values), axis=1)

    return df

def compute_additional_columns(df):
    # Compute the columns relatives to date that are missing
    df['WeekDay'] = df[["Day"]].apply(lambda x: calendar.day_name[datetime.strptime(x.values[0], '%Y-%m-%d').weekday()], axis=1)
    df['WeekHour'] = df[["WeekDay", "Hour"]].apply(lambda x: str(x.values[0]) + str(x.values[1]), axis=1)
    df['DayAndHour'] = df[["Day", "Hour"]].apply(lambda x: str(x.values[0]) + str(x.values[1]), axis=1)


    return df

def split(df, label_table):
    df_by_day = group_by_label_sum(df, ["Day"])
    df_by_day = compute_ratio(df_by_day, label_table)
    df_by_hour = group_by_label_average(df, "Hour")
    df_by_hour = compute_ratio(df_by_hour, label_table)
    return [df_by_day, df_by_hour]

def split2(df, dimensions,sortingLabels = "", ascending= True):
    groups = [group_by_label_sum(df, dimension, sortingLabels, ascending) for dimension in dimensions]
    return [compute_ratio2(group) for group in groups]

def group_by_label_sum(df, labels, sortingLabels = "", ascending= True): #, orderByLabel, )
    df_by_label = df.groupby(labels, as_index = False).sum()
    if len(sortingLabels) > 0 :
        df_by_label = df_by_label.sort_values(by=sortingLabels, ascending=ascending)
    return df_by_label

def group_by_label_average(df, labels, sortingLabels = "", ascending= True): #, orderByLabel, ascending)
    df_by_label = df.groupby(labels, as_index = False).mean()
    if len(sortingLabels) > 0 :
        df_by_label = df_by_label.sort_values(by=sortingLabels, ascending=ascending)
    return df_by_label

def compute_ratio(df, ratioLabel):
    df['Ratio'] = df[["Count",ratioLabel]].apply(lambda x: ComputeRatio(x.values),axis = 1)
    return df

def compute_ratio2(df):
    df['Ratio'] = df[["Count","Output"]].apply(lambda x: ComputeRatio(x.values),axis = 1)
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

def display_rows_by_aggretor0(df,aggregator,label_table):
    i = 0
    rows = [["", "Mean", 'Std', "Std/Mean percent"]]

    for value in df[aggregator].unique():
        df_aggregator = df[df[aggregator] == value]
        df_aggregator_by_day = group_by_label_sum(df_aggregator, ["Day"])
        df_aggregator_by_day = compute_ratio(df_aggregator_by_day, label_table)
        # print(df_aggregator_by_day["Count"].mean())
        update_rows(rows, [(df_aggregator_by_day, "day")], "Count", str(value))

    #print(rows)
    display(rows)

def display_rows_by_aggretor(df,aggregator,label_table,volume_label, values=[]):
    i = 0
    rows = [["", "Mean", 'Std', "Std/Mean percent"]]

    values = df[aggregator].unique() if len(values)== 0 else values
    for value in values:
        df_aggregator = df[df[aggregator] == value]
        df_aggregator_by_day = group_by_label_sum(df_aggregator, ["Day"])
        df_aggregator_by_day = compute_ratio(df_aggregator_by_day, label_table)

        df_aggregator_by_hour = group_by_label_average(df_aggregator, ["Hour"])
        df_aggregator_by_hour = compute_ratio(df_aggregator_by_hour, label_table)
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



#def get_global_rows(df_hour, df_day, labels):
#    rows = [["", "Mean", 'Std', "Std/Mean percent"]]
#    for label in labels:
#        rows = update_rows(rows, df_hour, df_day, label)
#    return rows


#def update_rows(rows, df_hour, df_day, label, value=""):
#    title = value + ": " + label if value != "" else label
#    rows.append(get_average_std(df_day, title + " per day", label))
#    rows.append(get_average_std(df_hour, title + " per hour", label))
#    return rows

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
