from datetime import datetime

from sqlalchemy import column, Integer, String, Float, Column, Enum, Boolean, ForeignKey
from app import db, app
from enum import Enum as RoleEnum
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime



class UserRole(RoleEnum):
    ADMIN = 1
    USER = 2
    STAFF = 3

class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100),
                    default='https://res.cloudinary.com/dxxwcby8l/image/upload/v1646729533/zuur9gzztcekmyfenkfr.jpg')
    user_role = Column(Enum(UserRole), default=UserRole.USER)
    comments = relationship('Comment', backref='user', lazy=True)


class Category(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)

class RoomType(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    price = Column(Float, nullable=False, default=0)
    max_guests = Column(Integer, nullable=False, default=1)
    proportion = Column(Float, nullable=False, default=1.0)
    coefficient = Column(Float, nullable=False, default=1.0)
    room = relationship('Room', backref='roomtype', lazy=True)
    image = Column(String(100), nullable=True)
    commnents = relationship('Comment', backref='room_type', lazy=True)

class Room(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    roomtype_id = Column(Integer, ForeignKey(RoomType.id), nullable=False)
    booking  = relationship('Booking', backref='room', lazy=True)



class Reservation(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String(100), nullable=False)
    contact_phone = Column(String(15), nullable=False)
    reservation_date = Column(DateTime, default=datetime.now, nullable=False)
    checkin_date = Column(DateTime, nullable=False)
    checkout_date = Column(DateTime, nullable=False)
    is_checked_in = Column(Boolean, default=False, nullable=False)
    is_checked_out = Column(Boolean, default=False, nullable=False)
    booking = relationship('Booking', backref='reservation', lazy=True)
    bill = relationship('Bill', backref='reservation', uselist=False)

class Comment(db.Model):
    content = Column(String(255), nullable=False)
    room_type_id = Column(Integer, ForeignKey(RoomType.id), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    created_date = Column(DateTime, default=datetime.now)

    def __str__(self):
        return self.content

class Bill(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    reservation_id = Column(Integer, ForeignKey('reservation.id'), unique=True, nullable=False)  # Quan hệ 1-1
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    total_amount = Column(Float, nullable=False, default=0.0)
    staff_name = Column(String(100), nullable=True)  # Tên nhân viên
    is_paid = Column(Boolean, default=False, nullable=False)  # Trạng thái thanh toán



class Booking(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    reservation_id = Column(Integer, ForeignKey(Reservation.id), nullable=False)
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False)
    customer = relationship('Customer', backref='booking', lazy=True)
    expense = Column(Float, nullable=False, default=0.0)




class Customer(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    id_card = db.Column(db.String(20), nullable=False, unique=False)
    customer_type = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    booking_id = Column(Integer, ForeignKey(Booking.id), nullable=False)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # import hashlib
        # v = User(name='staff', username='staff', password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
        #          user_role=UserRole.STAFF)
        # db.session.add(v)
        # db.session.commit()

        # c1 = Category(name='Thuê phòng')
        # c2 = Category(name='Thanh toán')
        # c3 = Category(name='Thống kê')
        #
        #
        # db.session.add_all([c1,c2,c3])
        # db.session.commit()
        # rt1 = RoomType(name = "normal", price=1000000, max_guests = 3, proportion=0.25, coefficient=1.5, image="images/room_type1.jpg")
        # rt2 = RoomType(name = "vip", price=2000000, max_guests = 5, proportion=0.25, coefficient=1.5, image="images/room_type2.jpg")
        #
        # r1 = Room(name="Phòng 101", roomtype=rt1)
        # r2 = Room(name="Phòng 102", roomtype=rt1)
        # r3 = Room(name="Phòng 103", roomtype=rt2)
        # r4 = Room(name="Phòng 104", roomtype=rt2)


        # b1 = Booking(room=r1, checkin_date=datetime(2024, 11, 26), checkout_date=datetime(2024, 11, 28))
        # b2 = Booking(room=r2, checkin_date=datetime(2024, 11, 29), checkout_date=datetime(2024, 12, 1))
        # b3 = Booking(room=r1, checkin_date=datetime(2024, 12, 4), checkout_date=datetime(2024, 12, 7))
        # b4 = Booking(room=r3, checkin_date=datetime(2024, 12, 4), checkout_date=datetime(2024, 12, 7))
        # b5 = Booking(room=r4, checkin_date=datetime(2024, 12, 4), checkout_date=datetime(2024, 12, 7))
        # b6 = Booking(room=r2, checkin_date=datetime(2024, 12, 4), checkout_date=datetime(2024, 12, 7))
        #
        #
        #
        # c1 = Customer(booking=b1, name="Nguyễn Văn A", id_card="12", address="Hà Nội", customer_type="domestic")
        # c2 = Customer(booking=b1, name="Trần Thị B", id_card="987654321", address="TP.HCM", customer_type="international")
        # c3 = Customer(booking=b2, name="Trần Minh C", id_card="3658390290", address="Bình Dương", customer_type="domestic")
        # c4 = Customer(booking=b3, name="Bùi Thị D", id_card="2836638998", address="TP.HCM", customer_type="international")
        # c5 = Customer(booking=b4, name="bùi thị năm", id_card="28366", address="TP.HCM",
        #               customer_type="international")
        # c6 = Customer(booking=b5, name="Lê Van sáu", id_card="283663899", address="TP.HCM",
        #               customer_type="international")
        # c7 = Customer(booking=b6, name="Fedor gorst", id_card="8998", address="TP.HCM",
        #               customer_type="international")


        # db.session.add_all([r1, r2, r3, r4, rt1, rt2])
        # db.session.commit()
