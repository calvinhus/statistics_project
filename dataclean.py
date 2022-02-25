import pandas as pd


def clean(df):

    # strip columns (remove spaces)
    for col in df.columns:
        if type(col) == object:
            df[col] = df[col].apply(lambda x: x.strip())
        else:
            continue

    # delete Cybersecurity entries
    df = df[df['curriculum'] != 'Cybersecurity']

    # Pôr strings com o mesmo formato .title()
    #df['curriculum']=df['curriculum'].apply(lambda x: x.title())
    df['status'] = df['status'].apply(lambda x: x.title())

    # Hired 0 or 1
    df.loc[df['hired'] != 0, 'hired'] = 1

    # New columns: conversions
    df['conv_applied_interview'] = df.apply(
        lambda x: x['interview']/x['applied'] if x['applied'] != 0 else 0, axis=1)
    df['conv_interview_hired'] = df.apply(
        lambda x: x['hired']/x['interview'] if x['interview'] != 0 else 0, axis=1)
    df['conv_applied_interview_prcnt'] = df['conv_applied_interview']*100
    df['conv_interview_hired_prcnt'] = df['conv_interview_hired']*100

    # graduation date to date time e sort
    df["graduation_date"] = pd.to_datetime(
        df["graduation_date"], format="%Y-%m-%d")
    df.sort_values("graduation_date", inplace=True)

    # New column: format, PT or FT

    def format_pt_ft(row):
        if ('PT' in row['cohort']):
            return 'PT'
        else:
            return 'FT'

    df['format'] = df.apply(format_pt_ft, axis=1)

    # new columns year month month_year
    df['year'] = df['graduation_date'].dt.year
    df['month'] = df['graduation_date'].dt.month
    df['month_year'] = df['graduation_date'].apply(
        lambda x: str(x.month) + '-' + str(x.year))

    return df
