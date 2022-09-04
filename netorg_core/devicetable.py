"""All the things associated with Loading, building and accessing a device table."""
import pandas as pd
from pandas import DataFrame

# pylint: disable=too-few-public-methods
class DeviceTable :
    """The device table is the heart of Network Organizer."""
    def __init__(self,data) -> None:
        # pylint: disable=invalid-name
        self.__df = pd.DataFrame(data)

    def get_df(self) -> DataFrame:
        """Return the DataFrame."""
        return self.__df
