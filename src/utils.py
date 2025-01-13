from datetime import datetime, timedelta



def generate_date_list(start_date, end_date):
    """
    Generate list of dates between the start and end dates

    Args:
    -----
    start_date: The start date
    end_date: The end date

    Return:
    -------
    date_list: The list of all dates one day after the start date till the end_date
    """
    date_list = []
    current_date = start_date + timedelta(days=1)
    current_date = current_date.date()
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)
        
    return date_list