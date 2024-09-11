# @event.listens_for(User, "after_insert")
# def create_page_perms(mapper, connection, target):
#     """Create page permissions"""
#     if not target.page_perms and target.role == constants.UserRole.ADMIN.value:
#         with Session(bind=connection) as db:
#             db.add(PagePermission(user_id=target.id))
#             db.commit()
