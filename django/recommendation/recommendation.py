import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from recommendation.models import UserToDoInteraction

def get_recommendations(user_id, num_recommendations=5):
    # 예시 데이터를 DataFrame으로 가져오기 (실제 데이터베이스 쿼리로 대체)
    interactions = UserToDoInteraction.objects.all().values('user_id', 'todo_id', 'interaction_type')
    df = pd.DataFrame(list(interactions))

    # 사용자-아이템 행렬 생성
    user_item_matrix = df.pivot_table(index='user_id', columns='todo_id', aggfunc='size', fill_value=0)

    # 사용자 간 유사도 계산
    user_similarity = cosine_similarity(user_item_matrix)
    user_similarity_df = pd.DataFrame(user_similarity, index=user_item_matrix.index, columns=user_item_matrix.index)

    # 대상 사용자의 유사한 사용자 목록 가져오기
    similar_users = user_similarity_df[user_id].sort_values(ascending=False).index[1:]

    # 유사한 사용자가 좋아한 아이템 목록 가져오기
    similar_users_interactions = df[df['user_id'].isin(similar_users)]
    similar_users_items = similar_users_interactions['todo_id'].value_counts()

    # 사용자가 아직 하지 않은 아이템 필터링
    user_interactions = df[df['user_id'] == user_id]['todo_id']
    recommendations = similar_users_items[~similar_users_items.index.isin(user_interactions)]
    return recommendations.head(num_recommendations).index.tolist()