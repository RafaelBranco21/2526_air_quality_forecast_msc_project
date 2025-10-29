import pandas as pd

contaminants_cols= ['code', 'desc', 'units']

def load_contaminants(path = './../data/original_data/air_quality_contaminants.csv'):
    d = pd.read_csv(path)
    d.columns = contaminants_cols
    d = d.sort_values(by=[contaminants_cols[0]])
    return d

def get_contaminant_by_code(df, code = None):
    if code == None:
        return []
    else:
        d = df[df[contaminants_cols[0]] == code]
        
        if len(d) == 0:
            return []
        else:
            return d.values[0]


if __name__ == '__main__':
    df = load_contaminants()
    print(df)