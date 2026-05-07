import pytest
from src.movie_system import MovieSystem, Movie, User


class TestAddMovie:
    """测试添加电影功能"""
    
    def setup_method(self):
        """每个测试前初始化系统"""
        self.system = MovieSystem()
    
    def test_add_valid_movie(self):
        """测试添加有效电影"""
        movie = self.system.add_movie("Inception", "Christopher Nolan", 2010, "Sci-Fi")
        assert movie.movie_id == 1
        assert movie.name == "Inception"
        assert movie.director == "Christopher Nolan"
        assert movie.release_year == 2010
        assert movie.genre == "Sci-Fi"
        assert movie.rating == 0.0
    
    def test_add_duplicate_movie_name(self):
        """测试添加重复电影名应抛出异常"""
        self.system.add_movie("Inception", "Christopher Nolan", 2010, "Sci-Fi")
        with pytest.raises(ValueError, match="already exists"):
            self.system.add_movie("inception", "Other Director", 2011, "Drama")
    
    def test_add_movie_invalid_year(self):
        """测试添加无效年份应抛出异常"""
        with pytest.raises(ValueError, match="Release year"):
            self.system.add_movie("Test", "Director", 1700, "Drama")
    
    def test_add_movie_empty_name(self):
        """测试添加空名称应抛出异常"""
        with pytest.raises(ValueError, match="Movie name"):
            self.system.add_movie("", "Director", 2010, "Drama")
    
    def test_add_movie_empty_genre(self):
        """测试添加空类型应抛出异常"""
        with pytest.raises(ValueError, match="Genre"):
            self.system.add_movie("Test", "Director", 2010, "")


class TestRegisterUser:
    """测试用户注册功能"""
    
    def setup_method(self):
        """每个测试前初始化系统"""
        self.system = MovieSystem()
    
    def test_register_valid_user(self):
        """测试注册有效用户"""
        user = self.system.register_user("alice")
        assert user.user_id == 1
        assert user.username == "alice"
        assert user.rated_movies == {}
    
    def test_register_duplicate_username(self):
        """测试注册重复用户名应抛出异常"""
        self.system.register_user("alice")
        with pytest.raises(ValueError, match="already exists"):
            self.system.register_user("Alice")
    
    def test_register_empty_username(self):
        """测试注册空用户名应抛出异常"""
        with pytest.raises(ValueError, match="Username"):
            self.system.register_user("")


class TestRateMovie:
    """测试评分功能"""
    
    def setup_method(self):
        """每个测试前初始化系统"""
        self.system = MovieSystem()
        self.movie = self.system.add_movie("Inception", "Christopher Nolan", 2010, "Sci-Fi")
        self.user = self.system.register_user("alice")
    
    def test_rate_valid_movie(self):
        """测试对有效电影进行有效评分"""
        self.system.rate_movie(self.user.user_id, self.movie.movie_id, 8.5)
        assert self.movie.rating == 8.5
        assert self.user.rated_movies[self.movie.movie_id] == 8.5
    
    def test_rate_nonexistent_user(self):
        """测试对不存在的用户评分应抛出异常"""
        with pytest.raises(ValueError, match="does not exist"):
            self.system.rate_movie(999, self.movie.movie_id, 8.0)
    
    def test_rate_nonexistent_movie(self):
        """测试对不存在的电影评分应抛出异常"""
        with pytest.raises(ValueError, match="does not exist"):
            self.system.rate_movie(self.user.user_id, 999, 8.0)
    
    def test_rate_out_of_range_high(self):
        """测试评分超过10应抛出异常"""
        with pytest.raises(ValueError, match="Rating must be between"):
            self.system.rate_movie(self.user.user_id, self.movie.movie_id, 11.0)
    
    def test_rate_out_of_range_low(self):
        """测试评分低于0应抛出异常"""
        with pytest.raises(ValueError, match="Rating must be between"):
            self.system.rate_movie(self.user.user_id, self.movie.movie_id, -1.0)
    
    def test_update_average_rating(self):
        """测试更新平均评分"""
        # Alice 评分 8.0
        self.system.rate_movie(self.user.user_id, self.movie.movie_id, 8.0)
        
        # 注册 Bob 并评分 10.0
        bob = self.system.register_user("bob")
        self.system.rate_movie(bob.user_id, self.movie.movie_id, 10.0)
        
        # 平均分为 (8.0 + 10.0) / 2 = 9.0
        assert self.movie.rating == 9.0


class TestSearchMovies:
    """测试查询电影功能"""
    
    def setup_method(self):
        """每个测试前初始化系统"""
        self.system = MovieSystem()
        self.system.add_movie("The Matrix", "Wachowski Sisters", 1999, "Sci-Fi")
        self.system.add_movie("Inception", "Christopher Nolan", 2010, "Sci-Fi")
        self.system.add_movie("Titanic", "James Cameron", 1997, "Romance")
    
    def test_search_by_name_partial_match(self):
        """测试按名称模糊匹配"""
        results = self.system.search_movies("Matrix", by_name=True)
        assert len(results) == 1
        assert results[0].name == "The Matrix"
    
    def test_search_by_name_no_match(self):
        """测试按名称无匹配结果"""
        results = self.system.search_movies("NonExistent", by_name=True)
        assert len(results) == 0
    
    def test_search_by_genre(self):
        """测试按类型搜索"""
        results = self.system.search_movies("sci", by_name=False)
        assert len(results) == 2
        names = {m.name for m in results}
        assert "The Matrix" in names
        assert "Inception" in names
    
    def test_search_by_genre_case_insensitive(self):
        """测试按类型搜索不区分大小写"""
        results = self.system.search_movies("ROMANCE", by_name=False)
        assert len(results) == 1
        assert results[0].name == "Titanic"
    
    def test_search_empty_query_raises_error(self):
        """测试空查询应抛出异常"""
        with pytest.raises(ValueError, match="non-empty string"):
            self.system.search_movies("")


class TestRecommendMovies:
    """测试电影推荐功能"""
    
    def setup_method(self):
        """每个测试前初始化系统"""
        self.system = MovieSystem()
        # 添加一些电影
        self.m1 = self.system.add_movie("Movie A", "Dir A", 2020, "Action")
        self.m2 = self.system.add_movie("Movie B", "Dir B", 2020, "Action")
        self.m3 = self.system.add_movie("Movie C", "Dir C", 2020, "Drama")
        self.m4 = self.system.add_movie("Movie D", "Dir D", 2020, "Action")
        
        # 注册用户并评分
        self.user = self.system.register_user("test_user")
        self.system.rate_movie(self.user.user_id, self.m1.movie_id, 9.0)
    
    def test_recommend_for_new_user(self):
        """测试新用户（无评分）返回空列表"""
        new_user = self.system.register_user("new_user")
        recommendations = self.system.recommend_movies(new_user.user_id)
        assert recommendations == []
    
    def test_recommend_returns_correct_movies(self):
        """测试推荐返回正确类型的电影"""
        # 给M2也打个分，确保它也被计入偏好
        self.system.rate_movie(self.user.user_id, self.m2.movie_id, 8.0)
        
        recommendations = self.system.recommend_movies(self.user.user_id)
        # 应该只推荐Action类型的电影，排除已评分的M1和M2
        assert len(recommendations) == 1
        assert recommendations[0].movie_id == self.m4.movie_id
        assert recommendations[0].genre == "Action"
    
    def test_recommend_excludes_rated_movies(self):
        """测试推荐排除已评分电影"""
        recommendations = self.system.recommend_movies(self.user.user_id)
        rated_ids = set(self.user.rated_movies.keys())
        for rec in recommendations:
            assert rec.movie_id not in rated_ids
    
    def test_recommend_with_no_matching_genre(self):
        """测试没有匹配类型时返回空列表"""
        # 移除所有Action电影的评分，只留一个非Action评分
        self.system.rate_movie(self.user.user_id, self.m3.movie_id, 7.0)
        # 清除之前的Action评分以便测试
        del self.user.rated_movies[self.m1.movie_id]
        
        recommendations = self.system.recommend_movies(self.user.user_id)
        # 现在偏好是Drama，但Drama只有M3，已被评分，所以没有可推荐的Drama
        # Action没有被评分，所以不在偏好中
        assert recommendations == []
    
    def test_recommend_limit_n(self):
        """测试限制推荐数量N"""
        # 添加更多Action电影
        for i in range(5):
            self.system.add_movie(f"Action Movie {i}", f"Dir {i}", 2020, "Action")
        
        # 给M2也打个分，确保它也被计入偏好
        self.system.rate_movie(self.user.user_id, self.m2.movie_id, 8.0)
        
        recommendations = self.system.recommend_movies(self.user.user_id, n=2)
        assert len(recommendations) == 2
    
    def test_recommend_invalid_n(self):
        """测试无效N值应抛出异常"""
        with pytest.raises(ValueError, match="positive integer"):
            self.system.recommend_movies(self.user.user_id, n=-1)
    
    def test_recommend_nonexistent_user(self):
        """测试不存在的用户应抛出异常"""
        with pytest.raises(ValueError, match="does not exist"):
            self.system.recommend_movies(999)


class TestGetPopularMovies:
    """测试热门电影功能"""
    
    def setup_method(self):
        """每个测试前初始化系统"""
        self.system = MovieSystem()
        self.m1 = self.system.add_movie("Movie 1", "Dir 1", 2020, "Action")
        self.m2 = self.system.add_movie("Movie 2", "Dir 2", 2020, "Drama")
        self.m3 = self.system.add_movie("Movie 3", "Dir 3", 2020, "Comedy")
        
        # 设置不同评分
        user1 = self.system.register_user("user1")
        user2 = self.system.register_user("user2")
        
        self.system.rate_movie(user1.user_id, self.m1.movie_id, 9.0)
        self.system.rate_movie(user1.user_id, self.m2.movie_id, 8.0)
        self.system.rate_movie(user1.user_id, self.m3.movie_id, 9.0)
    
    def test_get_popular_sorted_by_rating_desc(self):
        """测试热门电影按评分降序排列"""
        popular = self.system.get_popular_movies()
        assert len(popular) >= 2
        # M1和M3都是9.0，M2是8.0
        # 评分相同按ID升序，所以M1应该在M3前面
        assert popular[0].movie_id == self.m1.movie_id  # Rating 9.0, ID 1
        assert popular[1].movie_id == self.m3.movie_id  # Rating 9.0, ID 3
        assert popular[2].movie_id == self.m2.movie_id  # Rating 8.0, ID 2
    
    def test_get_popular_limit_n(self):
        """测试限制返回数量N"""
        popular = self.system.get_popular_movies(n=2)
        assert len(popular) == 2
    
    def test_get_popular_invalid_n(self):
        """测试无效N值应抛出异常"""
        with pytest.raises(ValueError, match="positive integer"):
            self.system.get_popular_movies(n=0)
    
    def test_get_popular_empty_system(self):
        """测试空系统返回空列表"""
        empty_system = MovieSystem()
        popular = empty_system.get_popular_movies()
        assert popular == []