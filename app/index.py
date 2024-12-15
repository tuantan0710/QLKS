from os import rename
import math
from flask import render_template, request, redirect, Request, jsonify, session
from select import select
from sqlalchemy.sql.functions import count

import dao
from app import app, login, db
from flask_login import login_user, logout_user, current_user
from datetime import datetime, timedelta
from app.models import Booking, Room, UserRole, Reservation, Bill, RoomType


@app.route("/")
def index():
    room = dao.load_rooms()

    return render_template('index.html', RoomType=room)


@app.route('/login', methods=['get', 'post'])
def login_process():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username=username, password=password)
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.user_role.value
            login_user(user)
            return redirect('/')

    return render_template('login.html')

@app.route('/login-admin', methods=['post'])
def login_admin_process():
    username = request.form.get('username')
    password = request.form.get('password')
    user = dao.auth_user(username=username, password=password, role=UserRole.ADMIN)
    if user:
        login_user(user)

    return redirect('/admin')

@app.route('/room_type/<int:room_type_id>')
def room_detail(room_type_id):
    room_type = dao.get_room_type_by_id(room_type_id)

    return render_template('details.html', room_type=room_type)

@app.route('/logout')
def logout_process():
    logout_user()
    session.clear()
    return redirect('/login')


@login.user_loader
def get_user_by_id(user_id):
    return dao.get_user_by_id(user_id)


@app.route('/register', methods=['get', 'post'])
def register_process():
    err_msg = ''
    if request.method.__eq__("POST"):
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        if password.__eq__(confirm):
            data = request.form.copy()
            del data['confirm']

            dao.add_user(avatar=request.files.get('avatar'), **data)

            return redirect('/login')
        else:
            err_msg = 'Mật khẩu không khớp!'

    return render_template('register.html', err_msg=err_msg)



@app.route('/booking', methods=['get', 'post'])
def booking():
    return render_template('booking.html')

@app.route('/api/search', methods=['post'])
def search_rooms():
    data = request.get_json()
    checkin_date = data.get('checkin_date')
    checkout_date = data.get('checkout_date')

    try:
        checkin_date = datetime.strptime(checkin_date, '%Y-%m-%d')
        checkout_date = datetime.strptime(checkout_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Ngày bạn nhập không hợp lệ!"})

    max_checkin_date = datetime.today() + timedelta(days=28)
    if checkin_date > max_checkin_date:
        return jsonify({"error": f"Ngày nhận phòng không được quá {max_checkin_date.strftime('%d-%m-%Y')}!"})

    if checkout_date <= checkin_date:
        return jsonify({"error": "Ngày trả phòng phải sau ngày nhận phòng!"})

    if checkin_date < datetime.today():
        return jsonify({"error": "Ngày nhận phòng phải tối thiểu từ ngày hôm nay!"})

    available_rooms = dao.find_available_rooms(checkin_date, checkout_date)

    return jsonify({
        "available_rooms": [{
            "id": room.id,
            "name": room.name,
            "price": room.roomtype.price,
            "max_guests": room.roomtype.max_guests
        } for room in available_rooms]
    })



@app.route('/api/confirm', methods=['POST'])
def booking_cf():
    data = request.get_json()
    checkin_date = datetime.strptime(data['checkinDate'], '%Y-%m-%d')
    checkout_date = datetime.strptime(data['checkoutDate'], '%Y-%m-%d')
    checkin_date = checkin_date.replace(hour=9, minute=0, second=0, microsecond=0)
    checkout_date = checkout_date.replace(hour=9, minute=0, second=0, microsecond=0)
    customer_name = data['customerName']
    contact_phone = data['contactPhone']
    reservation = dao.add_reservation(customer_name=customer_name,contact_phone=contact_phone, checkin_date=checkin_date, checkout_date=checkout_date, is_checked_in=False)
    rooms = data['rooms']
      # Duyệt qua các phòng đã chọn
    for room_data in rooms:
        room_id = room_data['roomId']
        num_guests = room_data['numGuests']
        room = dao.get_room_by_id(room_id)
        booking = dao.add_booking(room=room, reservation=reservation)
        for guest_data in room_data['guests']:
            guest_name = guest_data['name']
            guest_idcard = guest_data['idCard']
            guest_address = guest_data['address']
            guest_type = guest_data['type']
            dao.add_customer(booking=booking,name=guest_name,id_card=guest_idcard, customer_type=guest_type,address=guest_address)
        dao.calculate_expense(booking)
    return jsonify({'success': True})

@app.route('/api/rent_cf', methods=['POST'])
def renting_cf():
    data = request.get_json()
    is_checked_in = True
    total_amount = 0
    checkin_date = datetime.strptime(data['checkinDate'], '%Y-%m-%d')
    checkout_date = datetime.strptime(data['checkoutDate'], '%Y-%m-%d')
    checkin_date = checkin_date.replace(hour=9, minute=0, second=0, microsecond=0)
    checkout_date = checkout_date.replace(hour=9, minute=0, second=0, microsecond=0)
    customer_name = data['customerName']
    contact_phone = data['contactPhone']
    reservation = dao.add_reservation(customer_name=customer_name,contact_phone=contact_phone, checkin_date=checkin_date,
                                      checkout_date=checkout_date, is_checked_in=True)
    rooms = data['rooms']
    # Duyệt qua các phòng đã chọn
    for room_data in rooms:
        room_id = room_data['roomId']
        num_guests = room_data['numGuests']
        room = dao.get_room_by_id(room_id)
        booking = dao.add_booking(room=room, reservation=reservation)

        for guest_data in room_data['guests']:
            guest_name = guest_data['name']
            guest_idcard = guest_data['idCard']
            guest_address = guest_data['address']
            guest_type = guest_data['type']
            dao.add_customer(booking=booking,name=guest_name,id_card=guest_idcard, customer_type=guest_type,address=guest_address)
        expense = dao.calculate_expense(booking)
        total_amount = total_amount + expense

    dao.add_bill(reservation=reservation, total_amount=total_amount)

    return jsonify({'success': True})

@app.route('/rent')
def make_rental():
    if not current_user.is_authenticated:
        return "Access Denied", 403
    user_role = current_user.user_role.value
    if not (dao.is_accessible(user_role, 1) or dao.is_accessible(user_role, 3)):
        return "Access Denied", 403
    return render_template('rent.html')



@app.route('/checkin',methods=['GET'])
def checkin():
    if not current_user.is_authenticated:
        return "Access Denied", 403
    user_role = current_user.user_role.value
    if not (dao.is_accessible(user_role, 1) or dao.is_accessible(user_role, 3)):
        return "Access Denied", 403
    search_query = request.args.get('search')
    page = request.args.get('page',1)
    reservation = dao.load_reservation(search_query, page=int(page))

    total = dao.count_reservation(search_query)  # Hàm đếm số lượng booking thỏa mãn tìm kiếm
    page_size = app.config["PAGE_SIZE"]
    pages = math.ceil(total / page_size)  # Tính tổng số trang

    # Trả về giao diện với dữ liệu đã phân trang
    return render_template('checkin.html', reservation=reservation, pages=pages, search_query=search_query)

@app.route('/checkout',methods=['GET'])
def checkout():
    if not current_user.is_authenticated:
        return "Access Denied", 403
    user_role = current_user.user_role.value
    if not (dao.is_accessible(user_role, 1) or dao.is_accessible(user_role, 3)):
        return "Access Denied", 403
    search_query = request.args.get('search')
    page = request.args.get('page', 1)
    rent = dao.load_checkout(search_query, page=int(page))

    total = dao.count_checkout(search_query)  # Hàm đếm số lượng booking thỏa mãn tìm kiếm
    page_size = app.config["PAGE_SIZE"]
    pages = math.ceil(total / page_size)  # Tính tổng số trang

    # Trả về giao diện với dữ liệu đã phân trang
    return render_template('checkout.html', rent=rent, pages=pages, search_query=search_query)


@app.route('/checkin/<int:reservation_id>', methods=['POST'])
def check_in(reservation_id):
    # Lấy reservation từ cơ sở dữ liệu
    reservation = Reservation.query.get_or_404(reservation_id)

    reservation.is_checked_in = True
    total_amount = sum(booking.expense for booking in reservation.booking)
    dao.add_bill(reservation=reservation, total_amount=total_amount)

    db.session.commit()


    return jsonify({'success': True})


@app.route('/checkout/<int:reservation_id>', methods=['POST'])
def check_out(reservation_id):
    # Lấy reservation từ cơ sở dữ liệu
    reservation = Reservation.query.get_or_404(reservation_id)

    # Cập nhật trạng thái checkout
    reservation.is_checked_out = True

    # Lưu thay đổi vào cơ sở dữ liệu
    db.session.commit()

    # Trả về phản hồi dưới dạng JSON
    return jsonify({"success": True})

@app.route('/pay_bill/<int:bill_id>', methods=['POST'])
def pay_bill(bill_id):
    bill = Bill.query.get_or_404(bill_id)

    bill.is_paid = True
    bill.staff_name = current_user.username
    bill.created_at = datetime.now()

    db.session.commit()

    # Trả về phản hồi dưới dạng JSON
    return jsonify({"success": True})

if __name__ == "__main__":
    from app import admin
    app.run(debug=True)