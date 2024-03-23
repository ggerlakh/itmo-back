class MissedRequiredFieldException(Exception):
    def __init__(self, field_name):
        self.field_name = field_name

    def __str__(self):
        return f"Field '{self.field_name}' is required"


class YearWrongTypeException(Exception):
    def __str__(self):
        return  "Field 'year' should be integer between 1900 and 2100"


class RatingWrongTypeException(Exception):
    def __str__(self):
        return  "Field 'rating' should be integer between 0 and 10"


class IDWrongTypeException(Exception):
    def __str__(self):
        return  "Field 'id' should be integer"
    

class FIOWrongTypeException(Exception):
    def __str__(self):
        return  "Field 'fio' should be string"

  
class TitleWrongTypeException(Exception):
    def __str__(self):
        return  "Field 'title' should be string with length <= 100"


class DirectorWrongTypeException(Exception):
    def __str__(self):
        return  "Field 'director' should be json that match that schema: {\"id\": integer, \"fio\": string}"


class MovieLengthTypeException(Exception):
    def __str__(self):
        return  "Field 'length' should be string with format [0-9][0-9]:[0-9][0-9]:[0-9][0-9]"