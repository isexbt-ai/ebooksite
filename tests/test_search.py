import pytest
from webserver.models import Database, BookSource, DownloadLog, init_database


@pytest.fixture
def db():
    """测试数据库"""
    import tempfile
    import os

    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test.db')

    from webserver.settings import CONF
    CONF['database'] = db_path

    init_database()

    yield Database()

    import shutil
    shutil.rmtree(temp_dir)


def test_book_source_create(db):
    """测试书源创建"""
    source = BookSource.create('Test Source', 'https://example.com/opds', 'opds')
    assert source.name == 'Test Source'
    assert source.url == 'https://example.com/opds'
    assert source.type == 'opds'
    assert source.enabled is True


def test_book_source_get_all(db):
    """测试获取所有书源"""
    BookSource.create('Source 1', 'https://example1.com', 'opds')
    BookSource.create('Source 2', 'https://example2.com', 'api')

    sources = BookSource.get_all()
    assert len(sources) == 2


def test_book_source_update(db):
    """测试更新书源"""
    source = BookSource.create('Test Source', 'https://example.com', 'opds')
    source.update(name='Updated Source', enabled=False)

    updated = BookSource.get_by_id(source.id)
    assert updated.name == 'Updated Source'
    assert updated.enabled is False


def test_book_source_delete(db):
    """测试删除书源"""
    source = BookSource.create('Test Source', 'https://example.com', 'opds')
    source.delete()

    deleted = BookSource.get_by_id(source.id)
    assert deleted is None


def test_download_log_create(db):
    """测试下载记录创建"""
    from webserver.models import User
    user = User.create('testuser', 'testpassword', 'Test User')

    log = DownloadLog.create(
        user_id=user.id,
        book_title='Test Book',
        book_author='Test Author',
        source_url='https://example.com/book.epub'
    )

    assert log.book_title == 'Test Book'
    assert log.book_author == 'Test Author'
    assert log.status == 'pending'


def test_download_log_update_status(db):
    """测试更新下载状态"""
    from webserver.models import User
    user = User.create('testuser2', 'testpassword', 'Test User')

    log = DownloadLog.create(
        user_id=user.id,
        book_title='Test Book',
        book_author='Test Author',
    )

    log.update_status('completed', '/path/to/file.epub', 1024)
    assert log.status == 'completed'
    assert log.file_path == '/path/to/file.epub'
    assert log.file_size == 1024


def test_download_log_get_by_user(db):
    """测试获取用户下载记录"""
    from webserver.models import User
    user = User.create('testuser3', 'testpassword', 'Test User')

    DownloadLog.create(user_id=user.id, book_title='Book 1', book_author='Author 1')
    DownloadLog.create(user_id=user.id, book_title='Book 2', book_author='Author 2')

    logs = DownloadLog.get_by_user(user.id)
    assert len(logs) == 2
