from .. import db, ma
import json

class BaseSchema(ma.SQLAlchemyAutoSchema):
    def get_dict(self, the_query):
        """
        Gets a json version of the object and then converts it back into
        a python object.
        """
        the_dump = self.dumps(the_query)
        return json.loads(the_dump)