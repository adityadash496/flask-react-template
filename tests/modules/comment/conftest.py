import pytest

from modules.account.account_service import AccountService
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.comment.comment_service import CommentService
from modules.comment.types import CreateCommentParams
from modules.task.task_service import TaskService
from modules.task.types import CreateTaskParams


@pytest.fixture
def test_account_id():
    """Create a test account and return its ID"""
    account = AccountService.create_account_by_username_and_password(
        params=CreateAccountByUsernameAndPasswordParams(
            username="testuser@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
        )
    )
    return account.id


@pytest.fixture
def test_task(test_account_id):
    """Create a test task and clean it up after test"""
    task = TaskService.create_task(
        params=CreateTaskParams(
            account_id=test_account_id, title="Test Task for Comments", description="A task to test comments"
        )
    )
    yield task
    # Cleanup is handled by the teardown in the test class


@pytest.fixture
def test_comment(test_account_id, test_task):
    """Create a test comment and clean it up after test"""
    comment = CommentService.create_comment(
        params=CreateCommentParams(
            account_id=test_account_id,
            task_id=test_task.id,
            content="Test comment content",
            author="Test Author",
        )
    )
    yield comment
    # Cleanup is handled by the teardown in the test class
