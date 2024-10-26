from typing import Tuple

class Utils:
    period_map = {
        "1970s": ("1970-01-01", "1979-12-31"),
        "1980s": ("1980-01-01", "1989-12-31"),
        "1990s": ("1990-01-01", "1999-12-31"),
        "2000s": ("2000-01-01", "2009-12-31"),
        "2010s": ("2010-01-01", "2019-12-31"),
        "2020s": ("2020-01-01", "2023-12-31"),
    }

    @classmethod
    def parse_period(cls, period: str) -> Tuple[str, str]:
        """
        Returns the start and end dates for a given period string (e.g., "1990s").
        
        Parameters:
            period (str): The period string, such as "1990s" or "2000s".
        
        Returns:
            Tuple[str, str]: A tuple containing the start and end dates as strings.
        
        Raises:
            ValueError: If the period is not in the predefined map.
        """
        if period in cls.period_map:
            return cls.period_map[period]
        else:
            raise ValueError("Invalid period format. Use formats like '1990s', '2000s', etc.")

    
    @classmethod
    def another_helper_function(cls, param):        
        pass
