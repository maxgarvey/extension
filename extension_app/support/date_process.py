import datetime

def one_year_process():
    today = datetime.datetime.now()

    new_expires_by_date = ''
    new_expires_by_date += str(today.year + 1)
    new_expires_by_date += str(today.month)
    new_expires_by_date += str(today.day)
    new_expires_by_date += '120000Z'
    return new_expires_by_date

def custom_date_process(date_string):
    try:
        date_split = date_string.split('/')
    except:
        return [False, 
            'no slashes present in date. Must be of format' + \
            ' "YYYY/MM/DD", ex. "2013/01/01"']

    if len(date_split) != 3:
        return [False, 
            'improper number of slashes. Must be exactly two,' + \
            ' ex. "2013/01/01"']

    else:
        try:
            year_as_int  = int(date_split[0])
            month_as_int = int(date_split[1])
            day_as_int   = int(date_split[2])
        except:
            return [False, 'non-integer values used for date.']

        if len(date_split[0]) != 2:
            return [False, 'month must be 2 digits long, ex. "01/01/2013"']
        elif len(date_split[1]) != 2:
            return [False, 'day must be 2 digits long, ex. "01/01/2013"']
        elif len(date_split[2]) != 4:
            return [False, 'year must be 4 digits long, ex. "01/01/2013"']
        else:
            custom_month = date_split[0]
            custom_day   = date_split[1]
            custom_year  = date_split[2]
            custom_etc   = '120000Z'

            new_expires_by_date = custom_year + custom_month + custom_day + custom_etc
            return [True, new_expires_by_date]
