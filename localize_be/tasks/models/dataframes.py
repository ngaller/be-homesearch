from dagster_pandas import create_dagster_pandas_dataframe_type, PandasColumn

HomeSearchDataframe = create_dagster_pandas_dataframe_type(
    name="HomeSearchDataframe",
    columns=[
        PandasColumn.integer_column("id"),
        PandasColumn.string_column("city"),
        PandasColumn.string_column("postal_code"),
        PandasColumn.integer_column("price"),
    ]
)