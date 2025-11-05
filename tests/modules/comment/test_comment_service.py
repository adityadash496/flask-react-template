import unittest
from datetime import datetime

import pytest

from modules.account.internal.store.account_repository import AccountRepository
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


class TestCommentService(unittest.TestCase):
    def setUp(self) -> None:
        LoggerManager.mount_logger()
        CommentRepository.collection()  # Initialize the collection

    def tearDown(self) -> None:
        CommentRepository.collection().delete_many({})
        TaskRepository.collection().delete_many({})
        AccountRepository.collection().delete_many({})

    def test_create_comment_success(self, test_account_id, test_task) -> None:
        """Test successful comment creation"""
        create_params = CreateCommentParams(
            account_id=test_account_id, task_id=test_task.id, content="This is a test comment", author="Test User"
        )

        comment = CommentService.create_comment(params=create_params)

        assert comment.id is not None
        assert comment.account_id == test_account_id
        assert comment.task_id == test_task.id
        assert comment.content == "This is a test comment"
        assert comment.author == "Test User"
        assert comment.active is True
        assert isinstance(comment.created_at, datetime)
        assert isinstance(comment.updated_at, datetime)

    def test_create_comment_empty_content(self, test_account_id, test_task) -> None:
        """Test that creating a comment with empty content raises an error"""
        create_params = CreateCommentParams(
            account_id=test_account_id, task_id=test_task.id, content="", author="Test User"
        )

        with pytest.raises(CommentBadRequestError) as exc_info:
            CommentService.create_comment(params=create_params)

        assert exc_info.value.code == CommentErrorCode.BAD_REQUEST
        assert "empty or whitespace only" in exc_info.value.message

    def test_create_comment_whitespace_only_content(self, test_account_id, test_task) -> None:
        """Test that creating a comment with whitespace-only content raises an error"""
        create_params = CreateCommentParams(
            account_id=test_account_id, task_id=test_task.id, content="   ", author="Test User"
        )

        with pytest.raises(CommentBadRequestError) as exc_info:
            CommentService.create_comment(params=create_params)

        assert exc_info.value.code == CommentErrorCode.BAD_REQUEST
        assert "empty or whitespace only" in exc_info.value.message

    def test_get_comment_success(self, test_account_id, test_comment) -> None:
        """Test successfully getting a single comment"""
        get_params = GetCommentParams(account_id=test_account_id, comment_id=test_comment.id)

        comment = CommentService.get_comment(params=get_params)

        assert comment.id == test_comment.id
        assert comment.account_id == test_account_id
        assert comment.content == test_comment.content
        assert comment.author == test_comment.author

    def test_get_comment_not_found(self, test_account_id) -> None:
        """Test getting a non-existent comment raises an error"""
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        get_params = GetCommentParams(account_id=test_account_id, comment_id=non_existent_comment_id)

        with pytest.raises(CommentNotFoundError) as exc_info:
            CommentService.get_comment(params=get_params)

        assert exc_info.value.code == CommentErrorCode.NOT_FOUND

    def test_get_comments_for_task_multiple(self, test_account_id, test_task) -> None:
        """Test getting multiple comments for a task"""
        # Create multiple comments
        comment1 = CommentService.create_comment(
            params=CreateCommentParams(
                account_id=test_account_id, task_id=test_task.id, content="First comment", author="User 1"
            )
        )
        comment2 = CommentService.create_comment(
            params=CreateCommentParams(
                account_id=test_account_id, task_id=test_task.id, content="Second comment", author="User 2"
            )
        )
        comment3 = CommentService.create_comment(
            params=CreateCommentParams(
                account_id=test_account_id, task_id=test_task.id, content="Third comment", author="User 3"
            )
        )

        get_params = GetCommentsForTaskParams(account_id=test_account_id, task_id=test_task.id)
        comments = CommentService.get_comments_for_task(params=get_params)

        assert len(comments) == 3
        # Comments should be sorted by created_at descending
        assert comments[0].id == comment3.id
        assert comments[1].id == comment2.id
        assert comments[2].id == comment1.id

    def test_get_comments_for_task_empty(self, test_account_id, test_task) -> None:
        """Test getting comments for a task with no comments"""
        get_params = GetCommentsForTaskParams(account_id=test_account_id, task_id=test_task.id)
        comments = CommentService.get_comments_for_task(params=get_params)

        assert len(comments) == 0

    def test_update_comment_success(self, test_account_id, test_comment) -> None:
        """Test successfully updating a comment"""
        update_params = UpdateCommentParams(
            account_id=test_account_id, comment_id=test_comment.id, content="Updated comment content"
        )

        updated_comment = CommentService.update_comment(params=update_params)

        assert updated_comment.id == test_comment.id
        assert updated_comment.content == "Updated comment content"
        assert updated_comment.updated_at > test_comment.updated_at

    def test_update_comment_empty_content(self, test_account_id, test_comment) -> None:
        """Test that updating a comment with empty content raises an error"""
        update_params = UpdateCommentParams(account_id=test_account_id, comment_id=test_comment.id, content="")

        with pytest.raises(CommentBadRequestError) as exc_info:
            CommentService.update_comment(params=update_params)

        assert exc_info.value.code == CommentErrorCode.BAD_REQUEST
        assert "empty or whitespace only" in exc_info.value.message

    def test_update_comment_not_found(self, test_account_id) -> None:
        """Test updating a non-existent comment raises an error"""
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        update_params = UpdateCommentParams(
            account_id=test_account_id, comment_id=non_existent_comment_id, content="Updated content"
        )

        with pytest.raises(CommentNotFoundError) as exc_info:
            CommentService.update_comment(params=update_params)

        assert exc_info.value.code == CommentErrorCode.NOT_FOUND

    def test_delete_comment_success(self, test_account_id, test_comment) -> None:
        """Test successfully deleting a comment"""
        delete_params = DeleteCommentParams(account_id=test_account_id, comment_id=test_comment.id)

        deletion_result = CommentService.delete_comment(params=delete_params)

        assert deletion_result.comment_id == test_comment.id
        assert deletion_result.success is True
        assert isinstance(deletion_result.deleted_at, datetime)

        # Verify the comment is no longer accessible
        get_params = GetCommentParams(account_id=test_account_id, comment_id=test_comment.id)
        with pytest.raises(CommentNotFoundError):
            CommentService.get_comment(params=get_params)

    def test_delete_comment_not_found(self, test_account_id) -> None:
        """Test deleting a non-existent comment raises an error"""
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        delete_params = DeleteCommentParams(account_id=test_account_id, comment_id=non_existent_comment_id)

        with pytest.raises(CommentNotFoundError) as exc_info:
            CommentService.delete_comment(params=delete_params)

        assert exc_info.value.code == CommentErrorCode.NOT_FOUND

    def test_delete_comment_idempotency(self, test_account_id, test_comment) -> None:
        """Test that deleting a comment twice raises an error on the second attempt"""
        delete_params = DeleteCommentParams(account_id=test_account_id, comment_id=test_comment.id)

        # First deletion should succeed
        deletion_result = CommentService.delete_comment(params=delete_params)
        assert deletion_result.success is True

        # Second deletion should raise CommentNotFoundError
        with pytest.raises(CommentNotFoundError) as exc_info:
            CommentService.delete_comment(params=delete_params)

        assert exc_info.value.code == CommentErrorCode.NOT_FOUND
