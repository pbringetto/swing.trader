import app.strategy as s
import pandas as pd

class TestStrategy:
    def test_dataframe(x):
        df = pd.read_csv("/home/user/app/test/data/BTC-USD-daily.csv")
        assert isinstance(df,pd.DataFrame) is True
