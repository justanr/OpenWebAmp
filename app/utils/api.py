from flask import abort
from flask.ext.restful import Resource

class SingleResource(Resource):
    model = None
    schema = None
    json_root = ''

    def get(self, slug):
        slug = slug.lower()
        q = self.model.query
        q = q.filter(self.model.slug == slug)
        q = q.first()

        if not q:
            abort(404)
        
        return { self.json_root : self.schema(q).data }
