
def read_and_clean_outputs(filename, label, filtered_days):
    df = pd.read_csv(filename, sep='\t', header=None)
    df.columns = ['Day', 'Hour', 'Count', label]
    df = df.fillna("Other")

    # order
    df = df.sort_values(by=['Day', 'Hour'])

    # Filter on bad day
    df = df[~df.Day.isin(filtered_days)]

    return df