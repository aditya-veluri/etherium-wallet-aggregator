from datetime import timedelta, date
from calendar import timegm


class UtilityMethods:
    @staticmethod
    def get_date_range_in_batches(start_date: date, end_date: date) -> tuple[int,int]:
        cur_date = start_date
        while cur_date <= end_date:
            chunk_end_date = min(cur_date + timedelta(days=365), end_date)
            yield timegm(cur_date.timetuple()), timegm(chunk_end_date.timetuple())
            cur_date += timedelta(days=366)

    @staticmethod
    def delete_file(file_path):
        if file_path.exists():
            file_path.unlink()
            print(f"Deleted: {file_path}")
        else:
            print(f"File does not exist: {file_path}.")
