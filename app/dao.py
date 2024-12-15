from sqlalchemy import false, or_

from app.models import Category, User, Room, Booking, Customer, Reservation, Bill, RoomType
import hashlib
from app import app, db
import cloudinary.uploader


def load_categories():
    return Category.query.order_by("id").all()


def get_user_by_id(id):
    return User.query.get(id)

def get_room_type_by_id(room_type_id):
    return RoomType.query.get(room_type_id)

def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User.query.filter(User.username.__eq__(username.strip()),
                          User.password.__eq__(password))
    if role:
        u = u.filter(User.user_role.__eq__(role))

    return u.first()
def load_rooms():
    query = RoomType.query

    return query.all()

def add_user(name, username, password, avatar=None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(name=name, username=username, password=password)

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get('secure_url')

    db.session.add(u)
    db.session.commit()


def get_room_by_id(room_id):
    return Room.query.get(room_id)


def add_booking(room, reservation):
    b = Booking(room=room, reservation=reservation)
    db.session.add(b)
    db.session.commit()
    return b


def add_reservation(customer_name,contact_phone, checkin_date, checkout_date, is_checked_in=false()):
    r = Reservation(customer_name=customer_name, contact_phone=contact_phone,checkin_date=checkin_date,checkout_date=checkout_date, is_checked_in=is_checked_in)
    db.session.add(r)
    db.session.commit()
    return r

def add_bill(reservation,total_amount):
    b = Bill(reservation=reservation,total_amount=total_amount)
    db.session.add(b)
    db.session.commit()

def load_reservation(search_query=None, page=1):
    r = Reservation.query
    if search_query:
        r = r.filter(
            Reservation.customer_name.contains(search_query),
            Reservation.is_checked_in == 0)
    else:
        r = r.filter(Reservation.is_checked_in == 0)

    page_size = app.config["PAGE_SIZE"]
    start = (page - 1) * page_size
    r = r.slice(start, start + page_size)

    return r.all()


def load_checkout(search_query=None, page=1):
    r = Reservation.query
    if search_query:
        r = r.outerjoin(Bill).filter(
            Reservation.customer_name.contains(search_query),
            Reservation.is_checked_in == 1,
            or_(
                Reservation.is_checked_out == 0,
                Bill.is_paid == 0
            )
            )
    else:
        r = r.outerjoin(Bill).filter(Reservation.is_checked_in == 1,
                     or_(
                         Reservation.is_checked_out == 0,
                         Bill.is_paid == 0
                     )
                     )

    page_size = app.config["PAGE_SIZE"]
    start = (page - 1) * page_size
    r = r.slice(start, start + page_size)

    return r.all()


def count_checkout(search_query=None):
    r = Reservation.query
    if search_query:
        r = r.outerjoin(Bill).filter(
            Reservation.customer_name.contains(search_query),
            Reservation.is_checked_in == 1,
            or_(
                Reservation.is_checked_out == 0,
                Bill.is_paid == 0
            )
        )
    else:
        r = r.outerjoin(Bill).filter(Reservation.is_checked_in == 1,
                     or_(
                         Reservation.is_checked_out == 0,
                         Bill.is_paid == 0
                     )
                     )

    return r.count()


def count_reservation(search_query=None):
    r = Reservation.query
    if search_query:
        r = r.filter(Reservation.customer_name.contains(search_query), Reservation.is_checked_in == 0)
    else:
        r = r.filter(Reservation.is_checked_in == 0)

    return r.count()


def add_customer(booking, name, id_card, customer_type, address):
    c = Customer(booking=booking, name=name, id_card=id_card, address=address, customer_type=customer_type)

    db.session.add(c)
    db.session.commit()


def calculate_expense(booking):
    price = booking.room.roomtype.price
    proportion = booking.room.roomtype.proportion
    coefficient = booking.room.roomtype.coefficient
    surcharge = 1.0
    max_guests = booking.room.roomtype.max_guests

    for customer in booking.customer:
        if customer.customer_type == 'international':
            price =price*coefficient
            break

    if len(booking.customer) == max_guests:
        price = price+(price*proportion)

    booking.expense = price
    db.session.commit()
    return price

def is_accessible(user_role, required_role):
    return user_role == required_role

def find_available_rooms(checkin_date, checkout_date):
    rooms = Room.query.all()
    available_rooms = []
    for room in rooms:
        is_available = True
        for booking in room.booking:
            reservation = booking.reservation  # Lấy Reservation liên kết với Booking
            if (checkin_date < reservation.checkout_date and checkout_date > reservation.checkin_date):
                is_available = False
                break

        if is_available:
            available_rooms.append(room)

    return available_rooms
