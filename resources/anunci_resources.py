import falcon
from sqlalchemy.orm.exc import NoResultFound

import messages
from db.models import Anunci
from hooks import requires_auth
from resources.base_resources import DAMCoreResource

@falcon.before(requires_auth)
class ResourceGetAnuncis(DAMCoreResource):
    def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetAnuncis, self).on_get(req, resp, args, *kwargs)

        current_user = req.context["auth_user"]

        response_anuncis = list()

        request_type = req.get_param("type", False)

        aux_anuncis = self.db_session.query(Anunci)\
            .filter(Anunci.owner_id != current_user.id) # Codi MySQL

        if request_type is not None:
            aux_anuncis = self.db_session.query(Anunci).filter(Anunci.type == request_type)



        if aux_anuncis is not None:
            for current_anunci in aux_anuncis.all():
                response_anuncis.append(current_anunci.min_json)

        resp.media = response_anuncis
        resp.status = falcon.HTTP_200

@falcon.before(requires_auth)
class ResourceGetAnunci(DAMCoreResource):
    def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetAnunci, self).on_get(req, resp, args, *kwargs)

        # IDEM USER
        if "id" in kwargs:
            try:
                aux_anunci = self.db_session.query(Anunci).filter(Anunci.id == kwargs["id"]).one()

                resp.media = aux_anunci.json_model
                resp.status = falcon.HTTP_200
            except NoResultFound:
                raise falcon.HTTPBadRequest(description=messages.anunci_not_found)