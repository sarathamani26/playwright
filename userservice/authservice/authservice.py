
from django.contrib.auth import authenticate
from knox.models import AuthToken
from rest_framework import status


from userservice.data.authresponse import AuthResponse
from userservice.data.errorResponse import auth_error
from userservice.models.usermodels import Entity, Employee


class AuthService:
    def get_user(self, user_name, password):
        user = authenticate(username=user_name, password=password)
        return user
    def automation_authenticate(self, user_name, password):
        user = self.get_user(user_name, password)
        if user is None:
            # error_response = auth_error()
            # error_response.set_http_status(status.HTTP_403_FORBIDDEN)
            # error_response.set_description('Invalid user account')
            # print(error_response)
            return 403
        else:
            user.auth_token_set.all().delete()
            token_obj = AuthToken.objects.create(user)
            employee = Employee.objects.filter(user_name=user_name)
            print(token_obj)
            auth_user = token_obj[0].user
            expiry = token_obj[0].expiry
            expiry_str = str(expiry)
            auth_response = AuthResponse()
            # auth_response.set_id(auth_user.id)
            # zeyaly_user = User.objects.get(id=auth_user.id)
            # auth_response.set_name(zeyaly_user.full_name)
            # auth_response.set_email(zeyaly_user.email)
            # auth_response.set_phone(zeyaly_user.phone)
            auth_response.set_token(token_obj[1])
            auth_response.set_expiry(expiry_str)
            auth_response.set_name(employee[0].full_name)
            auth_response.set_code(employee[0].user_name)
            auth_response.set_employee_id(employee[0].id)
            auth_response.user_id = employee[0].user_id
            auth_response.entity_id = employee[0].entity_id
            # auth_response.set_http_status(status.HTTP_200_OK)
            # entity details
            # entity = Entity.objects.get(id=entity_id)
            # auth_response.entity_id = entity_id
            # auth_response.entity_name = entity.name
            # user_serv = UserService()
            # user_serv.change_employee_entity_mapping(user_name, entity_id)
            return auth_response
