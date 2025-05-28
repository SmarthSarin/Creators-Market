# Django eCommerce Website
This project is a full-fledged eCommerce website built using Django, a high-level Python web framework. It includes essential features such as user authentication, product browsing, cart management, checkout process, payment integration, and more. The website is designed to be robust, scalable, and user-friendly, providing a seamless shopping experience for customers.

## Table of Contents
- [Features](#features)
- [Screenshots](#screenshots)
- [Technologies Used](#technologies-used)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

- **User Authentication:** Secure user registration, login, reset password, and profile management.
- **Product Catalog:** Browse and search products with detailed descriptions and images.
- **Shopping Cart:** Add, update, and remove items from the cart seamlessly.
- **Checkout Process:** Smooth checkout flow with order summary and address management.
- **Payment Integration:** Integrated with Razorpay for secure online payments.
- **Order Management:** View order history and status updates.
- **Responsive Design:** Mobile-friendly UI ensuring a consistent experience across devices.
- **Admin Panel:** Manage products, orders, and users efficiently through Django's admin interface.

## Screenshots

### Home Page

![Homepage Screenshot](https://github.com/user-attachments/assets/466a5f52-5edf-467b-beba-a23ac613dde8)


### Wishlist Page

![image](https://github.com/user-attachments/assets/5ec62b0b-5731-42a2-b384-73b510f534c9)

### Order History Page

![image](https://github.com/user-attachments/assets/81712ce3-d7c2-47c4-9424-bd1d05e89abd)


### Order Details Page

![Screenshot 2025-05-28 101302](https://github.com/user-attachments/assets/56dae1e2-e5a8-4fc4-bc24-c816b75703ce)


### Contact-Us Page

![image](https://github.com/user-attachments/assets/20bad533-0b26-4829-be64-e88776cd2955)


### About-Us Page

![image](https://github.com/user-attachments/assets/fe083506-8c51-4e99-9f8a-ec4e766556ba)


### Product Page

![image](https://github.com/user-attachments/assets/2f14468a-4937-420a-9743-af6a1fdf29fa)


### Shopping Cart Page

![image](https://github.com/user-attachments/assets/bddd64ee-403e-4ae7-a979-25b009eeb100)


### Payment Testing View Page

![image](https://github.com/user-attachments/assets/7040621d-d751-4aa6-b879-d3403babd93d)


### Payment Success Page

![image](https://github.com/user-attachments/assets/d7645f9d-690c-472e-9ecd-947dc7e8ab76)


### Login Page

![image](https://github.com/user-attachments/assets/e11796a9-f448-4d9a-8781-02a7433519bf)


### Register Page

![image](https://github.com/user-attachments/assets/39281b76-7117-4b3b-8585-99019353e406)


### Reset Password Page

![image](https://github.com/user-attachments/assets/1e0d2fd8-fe21-454a-8ba8-0c5bfc7b7961)


### Profile Page

![image](https://github.com/user-attachments/assets/753ef372-2612-4a6a-8d78-312f348c7af4)


### Shipping Address Page

![image](https://github.com/user-attachments/assets/e9fde370-b24f-40a7-82da-069b68cc8cf3)


### Change Password View

![image](https://github.com/user-attachments/assets/0eb0beeb-80e7-48e7-a3f2-4151c029d998)


## Technologies Used

- **Django:** Python-based web framework for backend development.
- **HTML/CSS/JavaScript:** Frontend development for a responsive and interactive UI.
- **Razorpay API:** Payment gateway integration for secure transactions.
- **Bootstrap:** Frontend framework for responsive design and UI components.

## Setup Instructions

To run this project locally, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/atulguptag/Django-eCommerce-Website.git
   cd Django-eCommerce-Website
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```
3. **Activate the virtual environment:**

   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### `Note`: Before running `python manage.py migrate`, first create `.env` file in your project root, and update it with the same as `.env.example`

- Then, add `SECRET_KEY` and `DEBUG=True` in `.env` file -

- **How to generate/get the SECRET_KEY?**

- Open your terminal (make sure your virtual environment is activated, it should be something like this - `(venv) PS C:\Users\asus\Django-eCommerce-Website`)

- then type `django-admin shell`, and hit enter.

- Paste the below code into your shell (use mouse right side button to paste the copied code, `as Ctrl+V may not work`)-

  ```bash
  from django.core.management.utils import get_random_secret_key
  get_random_secret_key()
  ```

* Copy the `SECRET_KEY`(whatever you got in the output), and paste it in your `.env` file after `SECRET_KEY=`.

* Now, you are good to go :) -

5. **Apply database migrations:**

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (admin):**

   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server:**

   ```bash
   python manage.py runserver
   ```

8. **Open your web browser and navigate to:**
   ```
   http://127.0.0.1:8000/
   ```

### `Note`: After you navigate to the above url (`http://127.0.0.1:8000/`), and when you try to navigate to the login, signup, or any page which requires login, then you'll see an error coming from the Social Account Model. If you don't want to add google auth functionality in your project, you can simply remove all social account related things in the code. In case, if you want to proceed with the default, then here's how you can fix that error -

- Follow this step: navigate to `http://127.0.0.1:8000/admin/`, enter your `username and password` which you used to create in `Step no: 6`
- then follow this screenshot for better understanding :) -

# - ![Social Application Screenshot](Screenshots/google_auth-Change-social-application-Django-site-admin.png)

- Simply, put your Google Client Id and Secret Id in those two places which I highlighted.

- Now, you are ready to rock 🎉🤘🏻

## Usage

- **Admin Panel:** Access the admin panel at `http://127.0.0.1:8000/admin/` to manage products, orders, and users.
- **Shopping:** Browse products, add items to the cart, proceed to checkout, and make payments using Razorpay.
- **Profile:** Users can register, login, reset their password, view their order history, and update their profiles.
