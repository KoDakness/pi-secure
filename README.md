Pi-Secure - Password Manager & File Upload App
v 1.0.0
Pi-Secure is a simple yet powerful password manager and file storage App designed for Raspberry Pi OS. With Pi-Secure, you can store and manage your passwords securely, generate strong passwords, and upload important files to keep them off your PC. Think of it as your own mini cloud for safe file storage and password management.

This project is designed to run on Raspberry Pi OS, but it should work on other Debian-based OSes such as Bookworm for Raspberry Pi 4, Pi 5, and other compatible devices.

Features Password Manager: Store and manage your passwords securely. Password Generator: Generate strong, random passwords with a single click. File Upload: Upload and store files safely. Self-Hosted: Run it locally on your Raspberry Pi for a personal cloud experience. Requirements Raspberry Pi OS (should work on Raspberry Pi 4, Pi 5, and OW2 3 & 4) SSH access to your Raspberry Pi Python 3 pip (for Python package installation) Git

Installation Follow these steps to install Pi-Secure on your Raspberry Pi OS:

Prepare Your Raspberry Pi Make sure your Raspberry Pi is running Raspberry Pi OS (any version compatible with Bookworm and based on Debian, Mine was 32 bit pi OS in testing). For best results, use SSH to access your Raspberry Pi, as it might be tricky to set up directly on the Pi due to its slower 32-bit OS. There are good YouTube Tuts on how to ssh into a pi.

Clone the Repository First, clone the Pi-Secure repository to your Raspberry Pi. You can use SSH to clone the repo directly to your Pi.

/home is a good dir to use then git clone https://github.com/KoDakness/pi-secure to the cd /home/pi-secure

Set Up the Environment Pi-Secure uses a virtual environment to manage dependencies. Create and activate the virtual environment.

python3 -m venv venv source venv/bin/activate

Install Dependencies Install the necessary Python dependencies by running:

pip install -r requirements.txt

Configure the Application Ensure you have the required environment variables and settings. You might need to edit certain configuration files based on your needs (such as database configurations and secret keys). there is always some conflicts somewhere u gotta work through XD

Run the App with python app.py - for local testing the debug in app.py is set to false may need to make true

Start the application with Gunicorn (for production use) u will need to install this

Access Pi-Secure After setting up the application, you can access Pi-Secure by navigating to the IP address of your Raspberry Pi in your

browser: http://192.188.x.x:5000/

The default port is 5000, but you can configure it to any other port if needed.

Features in Detail

Password Manager: You can securely store passwords for various websites and accounts. Easily add, view, and delete passwords. Password Generator: Generate strong and random passwords at the click of a button.

File Upload: Upload files that you don't want stored on your PC. Download or delete these files via the Pi-Secure web interface. Responsive UI: Designed to work well on both desktop and mobile browsers.

Notes: This project is specifically designed for Raspberry Pi OS, but it should work on other Debian-based operating systems like Bookworm. We recommend using SSH to set up Pi-Secure on your Raspberry Pi for a smoother experience. The project is optimized for devices like Raspberry Pi 4, Pi 5, and OW2 3/4, but other devices may also work with some adjustments.

Contributing: Feel free to fork this repository and contribute. If you find any bugs or have suggestions for improvements, open an issue or
create a pull request.
