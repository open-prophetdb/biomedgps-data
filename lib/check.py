import os

def check_file_exists(file_path):
    if not os.path.exists(file_path):
        raise Exception("File not found: %s" % file_path)


def check_columns(df, columns):
    for column in columns:
        if column not in df.columns:
            raise Exception("Column not found: %s" % column)