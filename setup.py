from setuptools import setup, find_packages

setup(
    name='retro-blog',
    version='1.0.0',
    packages=find_packages(include=['app', 'app.*']),
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'flask-login',
        'flask-admin',
        'flask-security-too',
        'flask-mail',
        'flask-wtf',
        'flask-migrate',
        'pyotp',
        'pillow',
        'python-dotenv',
        'bcrypt',
        'email-validator',
        'python-magic',
    ],
    python_requires='>=3.8',
)
