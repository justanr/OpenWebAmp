from inspect import isclass

from flask import abort, request
from flask.ext.restful import Resource

class BaseResource(Resource):
    model = None
    schema = None
    schema_opts = {}
    urls = []
    route_opts = {}

    @classmethod
    def register(cls, api):
        api.add_resource(cls, *cls.urls, **route_opts)

class SingleResource(BaseResource):
    def get(self, slug):
        slug = slug.lower()
        q = self.model.query.filter(self.model.slug == slug).first()

        if not q:
            abort(404)
        
        return self.schema(q, **self.schema_opts).data

class ListResource(BaseResource):
    def get(self):
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)

        page = self.model.query.order_by(self.model.name).paginate(page, limit, False)
        serializer = self.schema(page.items, many=True, **self.schema_opts)

        return serializer.data

def register_resources(resources_module, api):
    for resource in resources_module.__dict__.values():
        if isclass(resource) and issubclass(resource, BaseResource):
            resource.register(api)
