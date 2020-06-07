import falcon
from sqlalchemy.orm.exc import NoResultFound

import messages
from db.models import Anunci, AnunciTypeEnum, AnunciLevelEnum
from hooks import requires_auth
from resources.base_resources import DAMCoreResource
from resources.schemas import SchemaCreateAnunci

@falcon.before(requires_auth)
class ResourceGetAnuncis(DAMCoreResource):
    def on_get(self, req, resp, args, *kwargs):
        super(ResourceGetAnuncis, self).on_get(req, resp, args, *kwargs)

        current_user = req.context["auth_user"]

        response_anuncis = list()


        aux_anuncis = self.db_session.query(Anunci)\
            .filter(Anunci.owner_id != current_user.id) # Codi MySQL



        if aux_anuncis is not None:
            for current_anunci in aux_anuncis.all():
                response_anuncis.append(current_anunci.min_json)

        resp.media = response_anuncis
        resp.status = falcon.HTTP_200

@falcon.before(requires_auth)
class ResourceGetAnunci(DAMCoreResource):
    def on_get(self, req, resp, args, *kwargs):
        super(ResourceGetAnunci, self).on_get(req, resp, args, *kwargs)

        # IDEM USER
        if "id" in kwargs:
            try:
                aux_anunci = self.db_session.query(Anunci).filter(Anunci.id == kwargs["id"]).one()

                resp.media = aux_anunci.json_model
                resp.status = falcon.HTTP_200
            except NoResultFound:
                raise falcon.HTTPBadRequest(description=messages.anunci_not_found)

class ResourceCreateAnunci(DAMCoreResource):
    @jsonschema.validate(SchemaCreateAnunci)
    def on_post(self, req, resp, *args, **kwargs):
        super(ResourceCreateAnunci, self).on_post(req, resp, *args, **kwargs)

        aux_user = Anunci()

        try:
            try:
                aux_type = AnunciTypeEnum(req.media["type"].upper())
            except ValueError:
                raise falcon.HTTPBadRequest(description=messages.genere_invalid)
            try:
                aux_level = AnunciLevelEnum(req.media["level"].upper())
            except ValueError:
                raise falcon.HTTPBadRequest(description=messages.genere_invalid)

            aux_user.title = req.media["title"]
            aux_user.description = req.media["description"]
            aux_user.price = req.media["price"]
            aux_user.admits_negotiation = req.media["admits_negotiation"]
            aux_user.distance_to_serve = req.media["distance_to_serve"]
            aux_user.type = aux_type
            aux_user.level = aux_level

            self.db_session.add(aux_user)

            try:
                self.db_session.commit()
            except IntegrityError:
                raise falcon.HTTPBadRequest(description=messages.user_exists)

        except KeyError:
            raise falcon.HTTPBadRequest(description=messages.parameters_invalid)

        resp.status = falcon.HTTP_200
