from locust import HttpUser, task, TaskSet


class UserBehavior(TaskSet):
    @task
    def get_user_detail(self):
        user_id = 1
        self.client.get(f'/users/{user_id}')

    @task
    def get_users(self):
        self.client.get('/users')


class LocustUser(HttpUser):
    host = "http://localhost:8000"
    tasks = [UserBehavior]
