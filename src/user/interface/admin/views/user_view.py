from sqladmin import ModelView
from sqlalchemy.orm import class_mapper

from src.user.infrastructure.database.models.user_model import UserModel


class UserView(ModelView, model=UserModel):  # type: ignore[call-arg]
    category = "User"
    name = "User List"
    column_list = [attr.key for attr in class_mapper(UserModel).column_attrs]

    column_labels = {
        UserModel.id: "ID",
        UserModel.username: "Username",
        UserModel.email: "Email",
        UserModel.password: "Password",
        UserModel.created_at: "Created At",
        UserModel.updated_at: "Updated At",
    }

    column_searchable_list = [UserModel.id, UserModel.username, UserModel.email]
    column_sortable_list = [UserModel.id, UserModel.username, UserModel.created_at]
