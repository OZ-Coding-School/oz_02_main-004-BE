from datetime import timedelta

def get_consecutive_success_days(user) -> int:
    posts = user.posts.filter(todo_progress__gte=80).order_by("-todo_date")
    if not posts:
        return 0

    streak = 0
    previous_date = None

    for post in posts:
        print(f'날짜 : {post.todo_date} | "달성률 : {post.todo_progress}')
        if previous_date is None:
            streak = 1
            previous_date = post.todo_date

        else:
            if previous_date - post.todo_date == timedelta(days=1):
                streak += 1
                previous_date = post.todo_date
            else:
                break

    print(f"연속 목표 달성(days) : {streak}일")
    return streak