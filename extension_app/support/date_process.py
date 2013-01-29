import datetime

def one_year_process():
    today = datetime.datetime.now()

    #increment the year by one
    new_expires_by_date = ''
    new_expires_by_date += str(today.year + 1)

    #deals with the case that we have a one digit month
    str_month = str(today.month)
    if len(str_month) < 2:
        str_month = '0' + str_month
    new_expires_by_date += str(str_month)

    #deals with the case that we have a one digit date
    str_day = str(today.day)
    if len(str_day) < 2:
        str_day = '0' + str_day
    new_expires_by_date += str(str_day)

    #tacks on hr, min, sec, stuff to the end
    new_expires_by_date += '120000Z'

    return new_expires_by_date

def custom_date_process(date_string):
    #first split up the date string by slash
    try:
        date_split = date_string.split('/')
    #if it fails, there are no slashes... date is incorrect!
    except:
        return [False,
            'no slashes present in date. Must be of format' + \
            ' "YYYY/MM/DD", ex. "2013/01/01"']

    #additional format validation, year, month, day are required
    if len(date_split) != 3:
        return [False,
            'improper number of slashes. Must be exactly two,' + \
            ' ex. "2013/01/01"']

    else:
        #verify that each entry is integer
        try:
            year_as_int  = int(date_split[0])
            month_as_int = int(date_split[1])
            day_as_int   = int(date_split[2])
        except:
            return [False, 'non-integer values used for date.']

        #verify that the date is a valid date...
        try:
            date_validated = datetime.date(year=year_as_int,
                month=month_as_int, day=day_as_int)
        except:
            return [False, 'date entered: {} is not a valid date.'.format(
                '{0}/{1}/{2}'.format(
                    date_split[0],date_split[1],date_split[2]))]

        #further validation of the length of each field.
        if len(date_split[0]) != 2:
            return [False, 'month must be 2 digits long, ex. "01/01/2013"']
        elif len(date_split[1]) != 2:
            return [False, 'day must be 2 digits long, ex. "01/01/2013"']
        elif len(date_split[2]) != 4:
            return [False, 'year must be 4 digits long, ex. "01/01/2013"']
        #success case
        else:
            custom_month = date_split[0]
            custom_day   = date_split[1]
            custom_year  = date_split[2]
            custom_etc   = '120000Z'

            new_expires_by_date = custom_year + custom_month + custom_day + custom_etc
            return [True, new_expires_by_date]
