function search_room(){

    event.preventDefault();
    const today = new Date().toISOString().split("T")[0];
    const checkinElement = document.getElementById('checkin_date').value;

    const checkinDate = checkinElement ? checkinElement : today;

    const checkoutDate = document.getElementById('checkout_date').value;

    fetch('/api/search', {
        method: 'POST',
        body: JSON.stringify({
            'checkin_date': checkinDate,
            'checkout_date': checkoutDate
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
     .then(response => response.json())
     .then(data => {
        if (data.error) {
            alert(data.error);  // Hiển thị lỗi từ server
        } else {
            displayAvailableRooms(data.available_rooms);  // Hiển thị các phòng có sẵn
        }
    })
}


function displayAvailableRooms(rooms) {
    const container = document.getElementById('available-rooms-container');
    const roomList = document.getElementById('room-list');
    const noRoom = document.getElementById('no-room');
    roomList.innerHTML = ''; // Xóa nội dung cũ

    if (rooms.length === 0) {
        noRoom.style.display = 'block';
        container.style.display = 'none';
    roomList.style.display = 'none';
    } else {
        rooms.forEach((room) => {
            const li = document.createElement('li');
            li.classList.add('list-group-item');
            li.innerHTML = `
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" value="${room.id}" id="room-${room.id}" name="rooms" onchange="toggleRoomSelection(${room.id})">
                    <label class="form-check-label" for="room-${room.id}">
                        ${room.name} - Giá: ${room.price} VNĐ/đêm
                    </label>
                </div>
                <div id="guests-form-${room.id}" class="guests-form mt-3" style="display:none;">
                    <label for="num_guests-${room.id}">Số lượng khách:</label>
                    <input type="number" id="num_guests-${room.id}" name="num_guests-${room.id}" min="1" max="${room.max_guests}" class="form-control" onchange="updateGuestForm(${room.id})">
                    <div id="guests-list-${room.id}"></div>
                </div>
            `;
            roomList.appendChild(li);
        });
    noRoom.style.display = 'none';
    container.style.display = 'block';
    roomList.style.display = 'block';
    }


}


function toggleRoomSelection(roomId) {
        const numGuestsField = document.getElementById('num_guests-' + roomId);
        const guestsForm = document.getElementById('guests-form-' + roomId);

        // Hiển thị form nhập số lượng khách nếu phòng được chọn
        if (document.getElementById('room-' + roomId).checked) {
            guestsForm.style.display = 'block';
        } else {
            guestsForm.style.display = 'none';
        }
    }

function updateGuestForm(roomId) {
        const numGuests = document.getElementById('num_guests-' + roomId).value;
        const guestsList = document.getElementById('guests-list-' + roomId);

        guestsList.innerHTML = '';
        for (let i = 0; i < numGuests; i++) {
            const guestForm = document.createElement('div');
            guestForm.classList.add('guest-form');
            guestForm.innerHTML = `
                <label for="guest-name-${roomId}-${i}">Tên khách ${i + 1}:</label>
                <input type="text" id="guest-name-${roomId}-${i}" name="guest-name-${roomId}-${i}" required>
                <label for="guest-idcard-${roomId}-${i}">CMND/CCCD khách ${i + 1}:</label>
                <input type="text" id="guest-idcard-${roomId}-${i}" name="guest-idcard-${roomId}-${i}" required>
                 <label for="guest-address-${roomId}-${i}">Địa chỉ:</label>
            <input type="text" id="guest-address-${roomId}-${i}" name="guest-address-${roomId}-${i}" required>

            <label for="guest-type-${roomId}-${i}">Loại khách:</label>
            <select id="guest-type-${roomId}-${i}" name="guest-type-${roomId}-${i}" required>
                <option value="domestic">Nội địa</option>
                <option value="international">Quốc tế</option>
            </select>
            `;
            guestsList.appendChild(guestForm);
        }
    }

function checkRoomSelectionBook(event) {
    // Ngừng hành động submit mặc định
    event.preventDefault();

    const rooms = document.querySelectorAll('input[name="rooms"]:checked');
    if (rooms.length === 0) {
        alert('Vui lòng chọn ít nhất một phòng!');
        return false;
    }

    // Kiểm tra thông tin khách hàng cho từng phòng
    let roomData = [];
    const customerName = document.getElementById('customer_name').value;
    const contactPhone = document.getElementById('contact_phone').value;
    if (!customerName) {
        alert('Vui lòng nhập tên khách hàng đặt phòng!');
        return false;
    }
    if (!contactPhone) {
        alert('Vui lòng nhập số điện thoại liên lạc!');
        return false;
       }

    for (let room of rooms) {
        const roomId = room.value;
        const numGuests = document.getElementById('num_guests-' + roomId).value;
        let guests = [];

        // Kiểm tra từng khách trong phòng
        for (let i = 0; i < numGuests; i++) {
            const guestName = document.getElementById('guest-name-' + roomId + '-' + i).value;
            const guestIdCard = document.getElementById('guest-idcard-' + roomId + '-' + i).value;
            const guestAddress = document.getElementById('guest-address-' + roomId + '-' + i).value;
            const guestType = document.getElementById('guest-type-' + roomId + '-' + i).value;

            if (!guestName || !guestIdCard || !guestAddress || !guestType) {
                alert('Vui lòng điền đầy đủ thông tin cho khách hàng!');
                return false;
            }

            // Thêm khách vào danh sách
            guests.push({
                name: guestName,
                idCard: guestIdCard,
                address: guestAddress,
                type: guestType
            });
        }

        // Thêm phòng vào dữ liệu gửi
        roomData.push({
            roomId: roomId,
            numGuests: numGuests,
            guests: guests
        });
    }

    // Gửi dữ liệu đã chọn đến server
    const formData = {
        customerName: customerName,
        contactPhone: contactPhone,
        checkinDate: document.getElementById('checkin_date').value,
        checkoutDate: document.getElementById('checkout_date').value,
        rooms: roomData
    };

    // Gửi yêu cầu đặt phòng
    fetch('/api/confirm', {
        method: 'POST',
        body: JSON.stringify(formData),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Đặt phòng thành công!!!!');
            window.location.href = '/booking';
        } else {
            alert('Có lỗi 1 xảy ra trong quá trình đặt phòng!');
        }
    })
    .catch(error => {
        alert('Có lỗi 2 xảy ra trong quá trình đặt phòng!');
    });

    return false;  // Ngừng hành động submit mặc định
}

function checkRoomSelectionRent(event) {
    // Ngừng hành động submit mặc định
    event.preventDefault();

    const rooms = document.querySelectorAll('input[name="rooms"]:checked');
    if (rooms.length === 0) {
        alert('Vui lòng chọn ít nhất một phòng!');
        return false;
    }

    // Kiểm tra thông tin khách hàng cho từng phòng
    let roomData = [];
    const customerName = document.getElementById('customer_name').value;
    const contactPhone = document.getElementById('contact_phone').value;
    if (!customerName) {
        alert('Vui lòng nhập tên khách hàng đặt phòng!');
        return false;
    }
    if (!contactPhone) {
        alert('Vui lòng nhập số điện thoại liên lạc!');
        return false;
    }
    for (let room of rooms) {
        const roomId = room.value;
        const numGuests = document.getElementById('num_guests-' + roomId).value;
        let guests = [];

        // Kiểm tra từng khách trong phòng
        for (let i = 0; i < numGuests; i++) {
            const guestName = document.getElementById('guest-name-' + roomId + '-' + i).value;
            const guestIdCard = document.getElementById('guest-idcard-' + roomId + '-' + i).value;
            const guestAddress = document.getElementById('guest-address-' + roomId + '-' + i).value;
            const guestType = document.getElementById('guest-type-' + roomId + '-' + i).value;

            if (!guestName || !guestIdCard || !guestAddress || !guestType) {
                alert('Vui lòng điền đầy đủ thông tin cho khách hàng!');
                return false;
            }

            // Thêm khách vào danh sách
            guests.push({
                name: guestName,
                idCard: guestIdCard,
                address: guestAddress,
                type: guestType
            });
        }

        // Thêm phòng vào dữ liệu gửi
        roomData.push({
            roomId: roomId,
            numGuests: numGuests,
            guests: guests
        });
    }

    // Gửi dữ liệu đã chọn đến server
    const formData = {
        customerName: customerName,
        contactPhone: contactPhone,
        checkinDate: document.getElementById('checkin_date').value,
        checkoutDate: document.getElementById('checkout_date').value,
        rooms: roomData
    };

    // Gửi yêu cầu đặt phòng
    fetch('/api/rent_cf', {
        method: 'POST',
        body: JSON.stringify(formData),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Đặt phòng thành công!!!!');
            window.location.href = '/rent';
        } else {
            alert('Có lỗi 1 xảy ra trong quá trình đặt phòng!');
        }
    })
    .catch(error => {
        alert('Có lỗi 2 xảy ra trong quá trình đặt phòng!');
    });

    return false;  // Ngừng hành động submit mặc định
}


function checkIn(reservationId) {
        // Gửi yêu cầu AJAX đến server
        fetch(`/checkin/${reservationId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ is_checked_in: true })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Cập nhật UI nếu check-in thành công
                alert('Check-in thành công!');
                location.reload();  // Tải lại trang để cập nhật trạng thái
            } else {
                alert('Có lỗi khi thực hiện check-in.');
            }
        })
        .catch(error => {
            console.error('Lỗi:', error);
            alert('Có lỗi khi thực hiện check-in.');
        });
    }

function checkOut(reservationId) {
        // Gửi yêu cầu AJAX đến server
        fetch(`/checkout/${reservationId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ is_checked_out: true })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Cập nhật UI nếu check-in thành công
                alert('Check-out thành công!');
                location.reload();  // Tải lại trang để cập nhật trạng thái
            } else {
                alert('Có lỗi khi thực hiện check-in.');
            }
        })
        .catch(error => {
            console.error('Lỗi:', error);
            alert('Có lỗi khi thực hiện check-in.');
        });
    }


function payBill(billId) {
    // Gửi yêu cầu AJAX đến server để thanh toán
    fetch(`/pay_bill/${billId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_paid: true })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {

            alert('Thanh toán thành công!');

            const payButton = document.getElementById(`pay-btn-${billId}`);
            payButton.classList.add('disabled');
            payButton.textContent = 'Đã thanh toán';
            location.reload();  // Tải lại trang để hiển thị thông tin mới
        } else {
            alert('Có lỗi 1 khi thực hiện thanh toán.');
        }
    })
    .catch(error => {
        console.error('Lỗi:', error);
        alert('Có lỗi 2 khi thực hiện thanh toán.');
    });
}





// Đặt ngày nhận phòng mặc định là ngày hôm nay và không cho thay đổi
    document.addEventListener('DOMContentLoaded', function () {
        const today = new Date().toISOString().split('T')[0];
        const checkinDateInput = document.getElementById('checkin_date');

    });
