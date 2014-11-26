from flask import abort, request
from flask.ext.restful import Resource

class SingleResource(Resource):
    model = None
    schema = None
    schema_opts = {}

    def get(self, slug):
        slug = slug.lower()
        q = self.model.query.filter(self.model.slug == slug).first()

        if not q:
            abort(404)
        
        return self.schema(q, **self.schema_opts).data

class ListResource(Resource):
    model = None
    schema = None
    schema_opts = {}

    def get(self):
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)

        page = self.model.query.order_by(self.model.name).paginate(page, limit, False)
        serializer = self.schema(page.items, many=True, **self.schema_opts)

        return serializer.data

