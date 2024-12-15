from flask_admin import Admin, BaseView,expose
from app import db, app
from flask_admin.contrib.sqla import ModelView
from app.models import Booking, Room, Customer, User, UserRole
from flask_login import current_user, logout_user
from flask import redirect

admin = Admin(app, name='ecourseapp',template_mode='bootstrap4' )

class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)

class MyView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class RoomView(AuthenticatedView):
    column_searchable_list = ['id','name']
    can_view_details = True

class LogoutView(MyView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect("/admin")

class StatsView(MyView):
    @expose("/")
    def index(self):
        return self.render('admin/stats.html')



admin.add_view(RoomView(Room, db.session))
admin.add_view(AuthenticatedView(Booking, db.session))
admin.add_view(AuthenticatedView(User, db.session))
admin.add_view(StatsView(name="Thống kê báo cáo"))
admin.add_view(LogoutView(name="Đăng xuất"))