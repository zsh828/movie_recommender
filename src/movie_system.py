"""
电影推荐系统核心模块。
包含 Movie 和 User 数据模型，以及 MovieSystem 业务逻辑类。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Movie:
    """电影数据模型"""
    movie_id: int
    name: str
    director: str
    release_year: int
    genre: str
    rating: float = 0.0
    
    def __post_init__(self):
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Movie name must be a non-empty string")
        if not isinstance(self.director, str) or not self.director:
            raise ValueError("Director must be a non-empty string")
        if not isinstance(self.release_year, int) or self.release_year < 1888 or self.release_year > 2100:
            raise ValueError("Release year must be an integer between 1888 and 2100")
        if not isinstance(self.genre, str) or not self.genre:
            raise ValueError("Genre must be a non-empty string")
        if not (0 <= self.rating <= 10):
            raise ValueError("Rating must be between 0 and 10")


@dataclass
class User:
    """用户数据模型"""
    user_id: int
    username: str
    rated_movies: Dict[int, float] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.username or not isinstance(self.username, str):
            raise ValueError("Username must be a non-empty string")


class MovieSystem:
    """电影推荐系统主类"""
    
    def __init__(self):
        self._movies: Dict[int, Movie] = {}
        self._users: Dict[int, User] = {}
        self._next_movie_id: int = 1
        self._next_user_id: int = 1
        
    def add_movie(self, name: str, director: str, release_year: int, genre: str) -> Movie:
        """
        添加一部新电影。
        
        Args:
            name: 电影名称
            director: 导演
            release_year: 上映年份
            genre: 类型
            
        Returns:
            创建的 Movie 对象
            
        Raises:
            ValueError: 如果输入非法或电影名重复
        """
        # 检查电影名是否重复
        for movie in self._movies.values():
            if movie.name.lower() == name.lower():
                raise ValueError(f"Movie with name '{name}' already exists")
        
        # 创建新电影
        movie = Movie(
            movie_id=self._next_movie_id,
            name=name,
            director=director,
            release_year=release_year,
            genre=genre,
            rating=0.0
        )
        self._movies[movie.movie_id] = movie
        self._next_movie_id += 1
        return movie
    
    def register_user(self, username: str) -> User:
        """
        注册用户。
        
        Args:
            username: 用户名
            
        Returns:
            创建的 User 对象
            
        Raises:
            ValueError: 如果输入非法或用户名重复
        """
        # 检查用户名是否重复（不区分大小写）
        for user in self._users.values():
            if user.username.lower() == username.lower():
                raise ValueError(f"User with username '{username}' already exists")
        
        # 创建新用户
        user = User(
            user_id=self._next_user_id,
            username=username
        )
        self._users[user.user_id] = user
        self._next_user_id += 1
        return user
    
    def rate_movie(self, user_id: int, movie_id: int, rating: float) -> None:
        """
        用户对电影进行评分。
        
        Args:
            user_id: 用户ID
            movie_id: 电影ID
            rating: 评分 (0-10)
            
        Raises:
            ValueError: 如果用户不存在、电影不存在、评分超出范围
        """
        # 验证用户存在
        if user_id not in self._users:
            raise ValueError(f"User with ID {user_id} does not exist")
        
        # 验证电影存在
        if movie_id not in self._movies:
            raise ValueError(f"Movie with ID {movie_id} does not exist")
        
        # 验证评分范围
        if not (0 <= rating <= 10):
            raise ValueError("Rating must be between 0 and 10")
        
        user = self._users[user_id]
        movie = self._movies[movie_id]
        
        # 记录用户评分
        user.rated_movies[movie_id] = rating
        
        # 重新计算电影的平均评分
        total_rating = sum(user.rated_movies.values())
        count = len(user.rated_movies)
        movie.rating = round(total_rating / count, 2)
    
    def search_movies(self, query: str, by_name: bool = True) -> List[Movie]:
        """
        查询电影。
        
        Args:
            query: 搜索关键词
            by_name: 如果为True则按电影名搜索，否则按类型搜索
            
        Returns:
            匹配的电影列表
            
        Raises:
            ValueError: 如果查询条件非法
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")
        
        results = []
        query_lower = query.lower()
        
        for movie in self._movies.values():
            if by_name:
                if query_lower in movie.name.lower():
                    results.append(movie)
            else:
                if query_lower in movie.genre.lower():
                    results.append(movie)
        
        return results
    
    def recommend_movies(self, user_id: int, n: int = 10) -> List[Movie]:
        """
        根据用户已评分电影的类型偏好，推荐同类型中评分最高的前N部电影。
        
        Args:
            user_id: 用户ID
            n: 推荐数量，默认为10
            
        Returns:
            推荐的电影列表
            
        Raises:
            ValueError: 如果用户不存在或n无效
        """
        # 验证用户存在
        if user_id not in self._users:
            raise ValueError(f"User with ID {user_id} does not exist")
        
        # 验证n的有效性
        if not isinstance(n, int) or n <= 0:
            raise ValueError("n must be a positive integer")
        
        user = self._users[user_id]
        
        # 如果没有评分过任何电影，无法推荐
        if not user.rated_movies:
            return []
        
        # 统计用户偏好的类型及其权重（基于评分）
        genre_scores: Dict[str, float] = {}
        for movie_id, rating in user.rated_movies.items():
            if movie_id in self._movies:
                genre = self._movies[movie_id].genre
                if genre not in genre_scores:
                    genre_scores[genre] = 0.0
                genre_scores[genre] += rating
        
        # 如果没有有效类型偏好，返回空列表
        if not genre_scores:
            return []
        
        # 找出所有未评分的电影
        rated_movie_ids = set(user.rated_movies.keys())
        candidate_movies = [
            movie for movie in self._movies.values()
            if movie.movie_id not in rated_movie_ids
        ]
        
        # 过滤出属于用户偏好类型的电影
        preferred_genres = set(genre_scores.keys())
        relevant_movies = [
            movie for movie in candidate_movies
            if movie.genre in preferred_genres
        ]
        
        # 如果没有符合条件的电影，返回空列表
        if not relevant_movies:
            return []
        
        # 按评分降序排序，评分相同按电影ID升序
        relevant_movies.sort(key=lambda m: (-m.rating, m.movie_id))
        
        # 返回前N部
        return relevant_movies[:n]
    
    def get_popular_movies(self, n: int = 10) -> List[Movie]:
        """
        获取热门电影（按评分降序，评分相同按ID升序）。
        
        Args:
            n: 返回数量，默认为10
            
        Returns:
            热门电影列表
            
        Raises:
            ValueError: 如果n无效
        """
        if not isinstance(n, int) or n <= 0:
            raise ValueError("n must be a positive integer")
        
        # 按评分降序排序，评分相同按电影ID升序
        all_movies = list(self._movies.values())
        all_movies.sort(key=lambda m: (-m.rating, m.movie_id))
        
        return all_movies[:n]