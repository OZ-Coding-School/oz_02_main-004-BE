from datetime import timedelta
from django.utils import timezone


def get_consecutive_success_days(user) -> int:
    today = timezone.now().date()

    # 테스트 후 바꿀 코드: 오늘날짜를 기준으로 연속 목표 달성일 카운트 하도록 할것
    posts = user.posts.filter(todo_progress__gte=80, todo_date__lte=today).order_by('-todo_date')
    # 테스트를 위한 코드: 생성된 포스트들 중 최신순으로 나열시 연속 목표 달성일 카운트

    # posts = user.posts.filter(todo_progress__gte=80).order_by('-todo_date')

    if not posts:
        return 0

    streak = 0
    previous_date = None

    for post in posts:
        print(f"날짜 : {post.todo_date} | 달성률 : {post.todo_progress}")
        if previous_date is None:
            streak = 1
            previous_date = post.todo_date

        else:
            if previous_date - post.todo_date == timedelta(days=1):
                streak += 1
                previous_date = post.todo_date
            else:
                break

    # whenever five consecutive sucess days
    pet = user.pet
    previous_streak = getattr(pet, 'streak', 0)

    if streak != previous_streak:
        if streak % 5 == 0:
            pet.random_boxes += 1
        pet.streak = streak
        pet.save()

    print(f'연속 목표 달성(days) : {streak}일')
    return streak
