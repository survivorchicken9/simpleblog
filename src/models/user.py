import datetime
import uuid

from flask import session

from src.common.database import Database
from src.models.blog import Blog


class User(object):
    def __init__(self, email, password, _id=None):
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def get_by_email(cls, email):
        data = Database.find_one("users", {"email": email})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_id(cls, _id):
        data = Database.find_one("users", {"_id": _id})
        if data is not None:
            return cls(**data)

    @staticmethod
    def login_valid(email, password):
        # Checking if user's email matches password they provide
        user = User.get_by_email(email)
        if user is not None:
            return user.password == password
        return False

    @classmethod
    def register(cls, email, password):
        user = cls.get_by_email(email)
        if user is None:
            new_user = cls(email, password)
            new_user.save_to_mongo()
            session['email'] = email  # flask handles cookies for session
            return True
        else:
            return False  # new user cannot be created

    @staticmethod
    def login(user_email):
        # already called login_valid
        session['email'] = user_email  # flask handles cookies for session

    @staticmethod
    def logout(user_email):
        # already called login_valid
        session['email'] = None  # flask handles cookies for session

    def get_blogs(self):
        # get all blogs from provided author_id
        return Blog.find_by_author_id(self._id)

    def new_blog(self, title, description):
        # needs following: author, author_id, title, description
        blog = Blog(author=self.email,
                    author_id=self._id,
                    title=title,
                    description=description)
        blog.save_to_mongo()

    @staticmethod
    def new_post(blog_id, title, content, created_date=datetime.datetime.utcnow()):
        # needs title, content, created_date=datetime.datetime.utcnow()
        blog = Blog.from_mongo(blog_id)
        blog.new_post(title=title,
                      content=content,
                      created_date=created_date)

    def json(self):
        # only using internally to save to mongodb
        return {
            "email": self.email,
            "_id": self._id,
            "password": self.password
        }

    def save_to_mongo(self):
        Database.insert("users", self.json())
