#!/usr/bin/python
# -*- coding: utf-8 -*-

import base64
import logging

import falcon
from falcon.media.validators import jsonschema

from datetime import datetime
import calendar

import messages
from db.models import User, UserToken, GenreEnum
from hooks import requires_auth
from resources.base_resources import DAMCoreResource
from resources.schemas import SchemaUserToken

mylogger = logging.getLogger(__name__)


class ResourceCreateUserToken(DAMCoreResource):
    def on_post(self, req, resp, *args, **kwargs):
        super(ResourceCreateUserToken, self).on_post(req, resp, *args, **kwargs)

        basic_auth_raw = req.get_header("Authorization")
        if basic_auth_raw is not None:
            basic_auth = basic_auth_raw.split()[1]
            auth_username, auth_password = (base64.b64decode(basic_auth).decode("utf-8").split(":"))
            if (auth_username is None) or (auth_password is None) or (auth_username == "") or (auth_password == ""):
                raise falcon.HTTPUnauthorized(description=messages.username_and_password_required)
        else:
            raise falcon.HTTPUnauthorized(description=messages.authorization_header_required)

        current_user = self.db_session.query(User).filter(User.email == auth_username).one_or_none()
        if current_user is None:
            current_user = self.db_session.query(User).filter(User.username == auth_username).one_or_none()

        if (current_user is not None) and (current_user.check_password(auth_password)):
            current_token = current_user.create_token()
            try:
                self.db_session.commit()
                resp.media = {"token": current_token.token}
                resp.status = falcon.HTTP_200
            except Exception as e:
                mylogger.critical("{}:{}".format(messages.error_saving_user_token, e))
                self.db_session.rollback()
                raise falcon.HTTPInternalServerError()
        else:
            raise falcon.HTTPUnauthorized(description=messages.user_not_found)


@falcon.before(requires_auth)
class ResourceDeleteUserToken(DAMCoreResource):
    @jsonschema.validate(SchemaUserToken)
    def on_post(self, req, resp, *args, **kwargs):
        super(ResourceDeleteUserToken, self).on_post(req, resp, *args, **kwargs)

        current_user = req.context["auth_user"]
        selected_token_string = req.media["token"]
        selected_token = self.db_session.query(UserToken).filter(UserToken.token == selected_token_string).one_or_none()

        if selected_token is not None:
            if selected_token.user.id == current_user.id:
                try:
                    self.db_session.delete(selected_token)
                    self.db_session.commit()

                    resp.status = falcon.HTTP_200
                except Exception as e:
                    mylogger.critical("{}:{}".format(messages.error_removing_user_token, e))
                    raise falcon.HTTPInternalServerError()
            else:
                raise falcon.HTTPUnauthorized(description=messages.token_doesnt_belongs_current_user)
        else:
            raise falcon.HTTPUnauthorized(description=messages.token_not_found)


@falcon.before(requires_auth)
class ResourceAccountUserProfile(DAMCoreResource):
    def on_get(self, req, resp, *args, **kwargs):
        super(ResourceAccountUserProfile, self).on_get(req, resp, *args, **kwargs)

        current_user = req.context["auth_user"]

        resp.media = current_user.json_model
        resp.status = falcon.HTTP_200

@falcon.before(requires_auth)
class ResourceAccountUpdateUserProfile(DAMCoreResource):
    def on_post(self, req, resp, *args, **kwargs):
        super(ResourceAccountUpdateUserProfile, self).on_post(req, resp, *args, **kwargs)

        current_user = req.context["auth_user"]

        if req.media["name"] is not None:
            current_user.name = req.media["name"]
        if req.media["surname"] is not None:
            current_user.surname = req.media["surname"]
        if req.media["zone"] is not None:
            current_user.expirience = req.media["zone"]
        if req.media["phone"] is not None:
            current_user.description = req.media["phone"]
        if req.media["email"] is not None:
            current_user.expirience = req.media["email"]
        if req.media["photo"] is not None:
            current_user.expirience = req.media["photo"]


        if req.media["gender"] is not None:
            aux_gender = req.media["gender"]
            if aux_gender == "MALE":
                current_user.genere = GenreEnum.male
            elif aux_gender == "FEMALE":
                current_user.genere = GenreEnum.female

        self.db_session.add(current_user)
        self.db_session.commit()

        resp.status = falcon.HTTP_200
