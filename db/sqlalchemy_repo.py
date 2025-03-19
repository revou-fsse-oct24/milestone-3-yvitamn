# from sqlalchemy.orm import Session
# from repos.base_repo import BaseRepository

# class SQLUserRepository(BaseRepository):
#     def __init__(self, db_session: Session):
#         self.session = db_session

#     def create(self, user):
#         self.session.add(user)
#         self.session.commit()
#         return user