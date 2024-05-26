import csv
import codecs


from bb_back.core.models import Submit
from bb_back.core.utils.view_utils import response


class SubmitService():
    def save_submit(submit_file, team, submit_schema):

        csv_file = csv.DictReader(codecs.iterdecode(submit_file, 'utf-8'))

        for line in csv_file:
            line: dict
            if list(line.keys()) != ['id', 'rate']:
                raise ValueError('CSV file columns must be: "id", "rate"')
            if not all([value.isnumeric() for value in line.values()]):
                raise ValueError(
                    'All provided values must be valid integers')

        Submit.objects.create(file=submit_file,
                              id_command=team.id,
                              round_num=submit_schema.get("round_num"),
                              score=0)

        return {"response_data": submit_schema}
