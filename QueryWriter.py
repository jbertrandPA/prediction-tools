from DataAnalysis import *


def compute_query(dimensions, nb_days, table_name, with_label_number = False):
    table_hive = "cbsdata.bid_request_imp_clicks" if table_name == "clicks" else "cbsdata.bid_request_imp_click_sales"
    days_additional = "and day > date_sub( current_date, " + str(nb_days + 1) + ") " if nb_days > -1 else ""
    dimensions_string = ",".join(dimensions)
    filename = get_filename(dimensions, nb_days, table_name, with_label_number)

    if with_label_number :
        hql = compute_query_per_label_number(dimensions_string, table_name, days_additional, table_hive, filename)
    else :
        hql =compute_query_per_dimension(dimensions_string, table_name, days_additional, table_hive, filename)

    print(hql)

def compute_query_per_dimension(dimensions_string, table_name, days_additional, table_hive, filename ):
    return "hive -e \"select " + dimensions_string + ", sum(A.total) as total, sum(A.c) as c \n from (select " \
          + dimensions_string + ",1 as total, CASE WHEN label_nb" + table_name + ">0 THEN 1 ELSE 0 END as c \n from " \
          + table_hive + " \n where day < current_date " + days_additional + " ) as A \n group by " + dimensions_string \
          + ";\">" + filename


def compute_query_per_label_number(dimensions_string, table_name, days_additional, table_hive, filename ):
    label = "label_nb"+ table_name
    return  "hive -e \"select " + dimensions_string + ", sum(A.total) as total, " + label+" \n from (select "  \
          +  dimensions_string + ",1 as total, " + label + "\n from " + table_hive + " \n where day < current_date " \
          + days_additional + " ) as A \n group by "+ label +", " + dimensions_string + ";\">" + filename
