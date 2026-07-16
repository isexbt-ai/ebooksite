import pytest
from webserver.models import Database, User, Card, init_database


@pytest.fixture
def db():
    """测试数据库"""
    import tempfile
    import os

    # 创建临时数据库
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test.db')

    # 设置数据库路径
    from webserver.settings import CONF
    CONF['database'] = db_path

    # 初始化数据库
    init_database()

    yield Database()

    # 清理
    import shutil
    shutil.rmtree(temp_dir)


def test_user_create(db):
    """测试用户创建"""
    user = User.create('testuser', 'testpassword', 'Test User')
    assert user.username == 'testuser'
    assert user.name == 'Test User'
    assert user.active is False


def test_user_verify_password(db):
    """测试密码验证"""
    user = User.create('testuser2', 'testpassword', 'Test User')
    assert user.verify_password('testpassword') is True
    assert user.verify_password('wrongpassword') is False


def test_user_activate(db):
    """测试用户激活"""
    from datetime import datetime, timedelta
    user = User.create('testuser3', 'testpassword', 'Test User')
    expiry_date = datetime.now() + timedelta(days=30)
    user.activate(expiry_date)
    assert user.active is True
    assert user.expiry_date is not None


def test_user_extend_expiry(db):
    """测试延长有效期"""
    from datetime import datetime, timedelta
    user = User.create('testuser4', 'testpassword', 'Test User')
    expiry_date = datetime.now() + timedelta(days=30)
    user.activate(expiry_date)

    user.extend_expiry(30)
    assert user.expiry_date > expiry_date


def test_card_create(db):
    """测试卡密创建"""
    card = Card.create('TEST-CODE-1234', 'register', 30)
    assert card.code == 'TEST-CODE-1234'
    assert card.type == 'register'
    assert card.duration_days == 30
    assert card.used is False


def test_card_redeem(db):
    """测试卡密兑换"""
    card = Card.create('TEST-CODE-5678', 'register', 30)
    user = User.create('testuser5', 'testpassword', 'Test User')

    result = card.redeem(user.id)
    assert result is True
    assert card.used is True
    assert card.used_by == user.id


def test_card_redeem_used(db):
    """测试已使用卡密"""
    card = Card.create('TEST-CODE-9012', 'register', 30)
    user = User.create('testuser6', 'testpassword', 'Test User')

    card.redeem(user.id)
    result = card.redeem(user.id)
    assert result is False
