import unittest
from datetime import datetime

from modules.account.account_service import AccountService
from modules.account.internal.store.account_repository import AccountRepository
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.comment.comment_service import CommentService
from modules.comment.errors import CommentBadRequestError, CommentNotFoundError
from modules.comment.internal.store.comment_repository import CommentRepository
from modules.comment.types import (
    CommentErrorCode,
    CreateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    GetCommentsForTaskParams,
    UpdateCommentParams,
)
from modules.logger.logger_manager import LoggerManager
from modules.task.internal.store.task_repository import TaskRepository
from modules.task.task_service import TaskService
from modules.task.types import CreateTaskParams


class TestCommentService(unittest.TestCase):
    def setUp(self) -> None:
        LoggerManager.mount_logger()
        CommentRepository.collection()  # Initialize the collection
        # Create test account
        self.account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username="testuser@example.com",
                password="testpassword",
                first_name="Test",
                last_name="User",
            )
        )
        # Create test task
        self.task = TaskService.create_task(
            params=CreateTaskParams(
                account_id=self.account.id, title="Test Task for Comments", description="A task to test comments"
            )
        )

    def tearDown(self) -> None:
        CommentRepository.collection().delete_many({})
        TaskRepository.collection().delete_many({})
        AccountRepository.collection().delete_many({})

    def test_create_comment_success(self) -> None:
        """Test successful comment creation"""
        create_params = CreateCommentParams(
            account_id=self.account.id, task_id=self.task.id, content="This is a test comment", author="Test User"
        )

        comment = CommentService.create_comment(params=create_params)

        assert comment.id is not None
        assert comment.account_id == self.account.id
        assert comment.task_id == self.task.id
        assert comment.content == "This is a test comment"
        assert comment.author == "Test User"
        assert comment.active is True
        assert isinstance(comment.created_at, datetime)
        assert isinstance(comment.updated_at, datetime)

    def test_create_comment_empty_content(self) -> None:
        """Test that creating a comment with empty content raises an error"""
        create_params = CreateCommentParams(
            account_id=self.account.id, task_id=self.task.id, content="", author="Test User"
        )

        with self.assertRaises(CommentBadRequestError) as context:
            CommentService.create_comment(params=create_params)

        assert context.exception.code == CommentErrorCode.BAD_REQUEST
        assert "empty or whitespace only" in context.exception.message

    def test_create_comment_whitespace_only_content(self) -> None:
        """Test that creating a comment with whitespace-only content raises an error"""
        create_params = CreateCommentParams(
            account_id=self.account.id, task_id=self.task.id, content="   ", author="Test User"
        )

        with self.assertRaises(CommentBadRequestError) as context:
            CommentService.create_comment(params=create_params)

        assert context.exception.code == CommentErrorCode.BAD_REQUEST
        assert "empty or whitespace only" in context.exception.message

    def test_get_comment_success(self) -> None:
        """Test successfully getting a single comment"""
        # Create a test comment
        test_comment = CommentService.create_comment(
            params=CreateCommentParams(
                account_id=self.account.id,
                task_id=self.task.id,
                content="Test comment content",
                author="Test Author",
            )
        )

        get_params = GetCommentParams(account_id=self.account.id, comment_id=test_comment.id)

        comment = CommentService.get_comment(params=get_params)

        assert comment.id == test_comment.id
        assert comment.account_id == self.account.id
        assert comment.content == test_comment.content
        assert comment.author == test_comment.author

    def test_get_comment_not_found(self) -> None:
        """Test getting a non-existent comment raises an error"""
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        get_params = GetCommentParams(account_id=self.account.id, comment_id=non_existent_comment_id)

        with self.assertRaises(CommentNotFoundError) as context:
            CommentService.get_comment(params=get_params)

        assert context.exception.code == CommentErrorCode.NOT_FOUND

    def test_get_comments_for_task_multiple(self) -> None:
        """Test getting multiple comments for a task"""
        # Create multiple comments
        comment1 = CommentService.create_comment(
            params=CreateCommentParams(
                account_id=self.account.id, task_id=self.task.id, content="First comment", author="User 1"
            )
        )
        comment2 = CommentService.create_comment(
            params=CreateCommentParams(
                account_id=self.account.id, task_id=self.task.id, content="Second comment", author="User 2"
            )
        )
        comment3 = CommentService.create_comment(
            params=CreateCommentParams(
                account_id=self.account.id, task_id=self.task.id, content="Third comment", author="User 3"
            )
        )

        get_params = GetCommentsForTaskParams(account_id=self.account.id, task_id=self.task.id)
        comments = CommentService.get_comments_for_task(params=get_params)

        assert len(comments) == 3
        # Comments should be sorted by created_at descending
        assert comments[0].id == comment3.id
        assert comments[1].id == comment2.id
        assert comments[2].id == comment1.id

    def test_get_comments_for_task_empty(self) -> None:
        """Test getting comments for a task with no comments"""
        get_params = GetCommentsForTaskParams(account_id=self.account.id, task_id=self.task.id)
        comments = CommentService.get_comments_for_task(params=get_params)

        assert len(comments) == 0

    def test_update_comment_success(self) -> None:
        """Test successfully updating a comment"""
        # Create a test comment
        test_comment = CommentService.create_comment(
            params=CreateCommentParams(
                account_id=self.account.id,
                task_id=self.task.id,
                content="Original content",
                author="Test Author",
            )
        )

        update_params = UpdateCommentParams(
            account_id=self.account.id, comment_id=test_comment.id, content="Updated comment content"
        )

        updated_comment = CommentService.update_comment(params=update_params)

        assert updated_comment.id == test_comment.id
        assert updated_comment.content == "Updated comment content"
        assert updated_comment.updated_at > test_comment.updated_at

    def test_update_comment_empty_content(self) -> None:
        """Test that updating a comment with empty content raises an error"""
        # Create a test comment
        test_comment = CommentService.create_comment(
            params=CreateCommentParams(
                account_id=self.account.id,
                task_id=self.task.id,
                content="Original content",
                author="Test Author",
            )
        )

        update_params = UpdateCommentParams(account_id=self.account.id, comment_id=test_comment.id, content="")

        with self.assertRaises(CommentBadRequestError) as context:
            CommentService.update_comment(params=update_params)

        assert context.exception.code == CommentErrorCode.BAD_REQUEST
        assert "empty or whitespace only" in context.exception.message

    def test_update_comment_not_found(self) -> None:
        """Test updating a non-existent comment raises an error"""
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        update_params = UpdateCommentParams(
            account_id=self.account.id, comment_id=non_existent_comment_id, content="Updated content"
        )

        with self.assertRaises(CommentNotFoundError) as context:
            CommentService.update_comment(params=update_params)

        assert context.exception.code == CommentErrorCode.NOT_FOUND

    def test_delete_comment_success(self) -> None:
        """Test successfully deleting a comment"""
        # Create a test comment
        test_comment = CommentService.create_comment(
            params=CreateCommentParams(
                account_id=self.account.id,
                task_id=self.task.id,
                content="Test comment content",
                author="Test Author",
            )
        )

        delete_params = DeleteCommentParams(account_id=self.account.id, comment_id=test_comment.id)

        deletion_result = CommentService.delete_comment(params=delete_params)

        assert deletion_result.comment_id == test_comment.id
        assert deletion_result.success is True
        assert isinstance(deletion_result.deleted_at, datetime)

        # Verify the comment is no longer accessible
        get_params = GetCommentParams(account_id=self.account.id, comment_id=test_comment.id)
        with self.assertRaises(CommentNotFoundError):
            CommentService.get_comment(params=get_params)

    def test_delete_comment_not_found(self) -> None:
        """Test deleting a non-existent comment raises an error"""
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        delete_params = DeleteCommentParams(account_id=self.account.id, comment_id=non_existent_comment_id)

        with self.assertRaises(CommentNotFoundError) as context:
            CommentService.delete_comment(params=delete_params)

        assert context.exception.code == CommentErrorCode.NOT_FOUND

    def test_delete_comment_idempotency(self) -> None:
        """Test that deleting a comment twice raises an error on the second attempt"""
        # Create a test comment
        test_comment = CommentService.create_comment(
            params=CreateCommentParams(
                account_id=self.account.id,
                task_id=self.task.id,
                content="Test comment content",
                author="Test Author",
            )
        )

        delete_params = DeleteCommentParams(account_id=self.account.id, comment_id=test_comment.id)

        # First deletion should succeed
        deletion_result = CommentService.delete_comment(params=delete_params)
        assert deletion_result.success is True

        # Second deletion should raise CommentNotFoundError
        with self.assertRaises(CommentNotFoundError) as context:
            CommentService.delete_comment(params=delete_params)

        assert context.exception.code == CommentErrorCode.NOT_FOUND
