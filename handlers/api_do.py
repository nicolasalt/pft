from common import CommonHandler
from datastore import models
from util import  parse_csv



class DoAddProfile(CommonHandler):
  def HandlePost(self):
    profile_name = self.request.get('name')

    self.profile = models.Profile.Create(self.visitor.key.id(), profile_name)
    models.User.Update(self.visitor.key.id(), active_profile_id=self.profile.key.id())

    return {
      'id': self.profile.key.id(),
      'status': 'ok'
    }


class DoSetActiveProfile(CommonHandler):
  def HandlePost(self):
    profile_id = int(self.request.get('id'))

    if models.Profile.get_by_id(profile_id):
      models.User.Update(self.visitor.key.id(), active_profile_id=profile_id)
      return {'status': 'ok'}
    else:
      return {'status': 'profile_does_not_exist'}


# Not tested


class DoAddParseSchema(CommonHandler):
  def HandlePost(self):
    name = self.request.get('name')
    schema = self.request.get('schema')

    self.profile.parse_schemas.append(
        models.ParseSchema(name=name, schema=schema))
    self.profile.put()

    self.WriteToJson({'status': 'ok'})


class DoApplyParseSchemaToImportedFile(CommonHandler):
  def HandlePost(self):
    imported_file_id = int(self.request.get('id'))
    schema = self.request.get('schema')

    imported_file = lookup.GetImportedFileById(self.profile, imported_file_id)
    imported_file.schema = schema
    imported_file.parsed = True
    imported_file.parsed_transactions = parse_csv.ParseCsv(
        imported_file.schema, imported_file.source_file)

    # For future performance
    imported_file.source_file = None
    imported_file.put()

    self.WriteToJson({'status': 'ok'})
