# samplesite/routers.py

class MainRouter:
    # Приложения, которые будут храниться в базе 'utility'
    route_app_labels = {'admin', 'auth', 'contenttypes', 'sessions'}
    utility_db = 'utility'
    default_db = 'default'

def allow_migrate(self, db, app_label, model_name=None, **hints):
    if app_label in self.route_app_labels:
        return db == self.utility_db
    else:
        return db == self.default_db

def db_for_read(self, model, **hints):
    if model._meta.app_label in self.route_app_labels:
        return self.db  # 'utility'
    else:
        return 'default'  # Исправить None на 'default'

def db_for_write(self, model, **hints):
    if model._meta.app_label in self.route_app_labels:
        return self.db
    else:
        return 'default'

def allow_relation(self, obj1, obj2, **hints):
    app1 = obj1._meta.app_label
    app2 = obj2._meta.app_label
    
    if app1 in self.route_app_labels and app2 in self.route_app_labels:
        return True
    elif app1 not in self.route_app_labels and app2 not in self.route_app_labels:
        return True
    # Объекты из разных групп - запрещаем связь
    else:
        return False