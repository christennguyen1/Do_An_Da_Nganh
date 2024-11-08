from databases.databases import *
from datetime import datetime
from fastapi import Request
from werkzeug.security import check_password_hash, generate_password_hash
import asyncio


def service_user_login(body):
    data = body

    # Kiểm tra nếu email và password được gửi đến
    if not data or not data.get('email') or not data.get('password'):
        return {
                'message': 'Email and password required', 
                'errCode': 1
            }, 400

    email = data.get('email')
    password = data.get('password')

    # Tìm người dùng theo email trong MongoDB
    user = collection_user.find_one({'email': email})

    user_status_delete = user.get('isDeleted', 'Unknown')

    if((not user) or (user_status_delete == True)):
        return {
                'message': 'User not found', 
                'data': {}
            }, 404

    # Kiểm tra mật khẩu có đúng không
    if not check_password_hash(user['password'], password):
        return {
                'message': 'Wrong username or password', 'errCode': 1
            }, 401
    
    # Trả về thông tin người dùng khi đăng nhập thành công
    return {
        'message': 'User Sign in successfully',
        'data': {
            'First name': user['fist_name'],
            'Last name': user['last_name'],
            'Username': user['username'],
            'Email': user['email'],
            'PhoneNumber': user['phoneNumber'],
            'Address': user['address']
        }
    }, 201 



def service_user_register(body):
    data = body

    if not data or not data.get('email') or not data.get('password'):
        # Trả về phản hồi lỗi nếu thiếu thông tin
        return {
                'message': 'Email and password required', 
                'data': [],
                'errCode': 1
            }, 400

    fname = data.get('first_name')
    lname = data.get('last_name')
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    phoneNumber = data.get('phoneNumber')
    address = data.get('address')
    role = data.get('role')

    user = collection_user.find_one({'email': email})

    # Mã hóa mật khẩu trước khi lưu
    hashed_password = generate_password_hash(password)

    # Thêm người dùng vào cơ sở dữ liệu
    user_data = {
        'fist_name': fname,
        'last_name': lname,
        'username': username,
        'password': hashed_password,
        'email': email,
        'phoneNumber': phoneNumber,
        'address': address,
        'role': role,
        'isDeleted': False
    }

    # Kiểm tra nếu người dùng đã tồn tại
    if user:
        user_status_delete = user.get('isDeleted', 'Unknown')
        if user_status_delete == False:
            return {
                    'message': 'User already exists', 
                    'errCode': 1,
                    'data': []
                }, 409
        else: 
            query = {"email": email}
            new_values = {
                "$set": {
                    'password': hashed_password, 
                    'fist_name': fname,
                    'last_name': lname,
                    'phoneNumber': phoneNumber, 
                    'address': address, 
                    'role': role,
                    'isDeleted': False
                    }
                }
            
            collection_user.update_one(query, new_values)
    else:     
        collection_user.insert_one(user_data)

    # Trả về thông tin người dùng vừa đăng ký
    return {
        'message': 'User registered successfully',
        'data': {
            'First name': user_data['fist_name'],
            'Last name': user_data['last_name'],
            'Username': user_data['username'],
            'Email': user_data['email'],
            'PhoneNumber': user_data['phoneNumber'],
            'Address': user_data['address']
        }
    }, 201  


def delete_data_user_service(body):
    data = body
    email = data.get('email')

    user = collection_user.find_one({'email': email})

    user_status_delete = user.get('isDeleted', 'Unknown')

    if ((not user) or (user_status_delete == True)):
        return {
                'message': 'User not in system', 
                'errCode': 1
            }, 400
    
    query = {"email": email}
    new_values = {
        "$set": {
            "isDeleted": True, "timestamp": datetime.now()
            }
        }
    
    collection_user.update_one(query, new_values)

    return {
        'message': 'User delete successful',
        'data': {
            'email': email,
            'timestamp': datetime.now()
        }
    }, 200


def service_user_updatePassword(body):
    data = body

    if not data or not data.get('email') or not data.get('password'):
        # Trả về phản hồi lỗi nếu thiếu thông tin
        return {
                'message': 'Email and password required', 
                'errCode': 1
            }, 400

    password = data.get('password')
    email = data.get('email')

    user = collection_user.find_one({'email': email})

    user_status_delete = user.get('isDeleted', 'Unknown')

    if ((not user) or (user_status_delete == True)):
         return {
                'message': 'User not found', 
                'errCode': 1
            }, 404


    # Mã hóa mật khẩu trước khi lưu
    hashed_password = generate_password_hash(password)

    query = {"email": email}
    new_values = {
        "$set": {
            'password': hashed_password
            }
        }
            
    collection_user.update_one(query, new_values)


    # Trả về thông tin người dùng vừa đăng ký
    return {
        'message': 'Update password user successfully',
        'data': {
            'email': email
        }
    }, 201  


def service_user_updateInfo(body):
    data = body

    if not data or not data.get('email'):
        return {
                'message': 'Email is required', 
                'errCode': 1
            }, 400

    fname = data.get('first_name')
    lname = data.get('last_name')
    username = data.get('username')
    email = data.get('email')
    phoneNumber = data.get('phoneNumber')
    address = data.get('address')

    user = collection_user.find_one({'email': email})

    user_status_delete = user.get('isDeleted', 'Unknown')

    if ((not user) or (user_status_delete == True)):
         return {
                'message': 'User not found', 
                'errCode': 1
            }, 404
    
    query = {"email": email}

    new_values = {"$set": {}}

    if fname:
        new_values["$set"]['fist_name'] = fname
    else:
        new_values["$set"]['fist_name'] = user.get('first_name')


    if lname:
        new_values["$set"]['last_name'] = lname
    else:
        new_values["$set"]['last_name'] = user.get('last_name')


    if phoneNumber:
        new_values["$set"]['phoneNumber'] = phoneNumber
    else:
        new_values["$set"]['phoneNumber'] = user.get('phoneNumber')


    if address:
        new_values["$set"]['address'] = address
    else:
        new_values["$set"]['address'] = user.get('address')

    if username:
        new_values["$set"]['username'] = username
    else:
        new_values["$set"]['username'] = user.get('username')
            
    collection_user.update_one(query, new_values)

    return {
        'message': 'User update successfully',
        'data': {
            'First name': fname,
            'Last name': lname,
            'Username': username,
            'PhoneNumber': phoneNumber,
            'Address': address
        }
    }, 201 