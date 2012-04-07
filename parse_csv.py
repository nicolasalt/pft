import csv
from datetime import datetime
from datastore import models


def _ParseSchema(raw_schema):
  """
    'a,b' -> ['a', 'b']
  """
  schema = raw_schema.replace(' ', '').split(',')
  schema_set = set(schema)
  if 'date' in schema_set and ('debit' in schema_set or 'credit' in schema_set):
    return schema
  else:
    return None

def ParseCsv(raw_schema, raw_csv):
  schema = _ParseSchema(raw_schema)
  if not schema: return []

  parsed_transactions = []
  for row in csv.DictReader(raw_csv.splitlines(), schema):
    try:
      date = datetime.strptime(row['date'], '%d.%m.%Y')
      if row['debit'] or row['credit']:
        if row['debit']:
          amount = float(row['debit'])
        else:
          amount = -float(row['credit'])
        parsed_transactions.append(
            models.ImportedFileTransaction(date=date, amount=amount,
                                           description=row['description']))
    except ValueError:
      pass

  return parsed_transactions


def AutoDetectSchema(schemas, raw_csv):
  for schema in schemas:


    parsed_transactions = ParseCsv(schema, raw_csv)
    if len(parsed_transactions) >= 2:
      return schema, parsed_transactions

  return None, None

