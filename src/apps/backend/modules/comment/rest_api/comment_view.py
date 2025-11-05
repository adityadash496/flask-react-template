from dataclasses import asdict

from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware
from modules.comment.comment_service import CommentService
from modules.comment.errors import CommentBadRequestError
from modules.comment.types import (
    CreateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    GetCommentsForTaskParams,
    UpdateCommentParams,
)


class CommentView(MethodView):
    @access_auth_middleware
    def post(self, account_id: str, task_id: str) -> ResponseReturnValue:
        """Create a new comment on a task"""
        request_data = request.get_json()

        if request_data is None:
            raise CommentBadRequestError("Request body is required")

        if not request_data.get("content"):
            raise CommentBadRequestError("Content is required")

        # Use author from request body if provided, otherwise use a default
        author = request_data.get("author", "Anonymous")

        create_comment_params = CreateCommentParams(
            account_id=account_id, task_id=task_id, content=request_data["content"], author=author
        )

        created_comment = CommentService.create_comment(params=create_comment_params)
        comment_dict = asdict(created_comment)
        # Convert datetime objects to ISO format strings
        comment_dict["created_at"] = created_comment.created_at.isoformat()
        comment_dict["updated_at"] = created_comment.updated_at.isoformat()

        return jsonify(comment_dict), 201

    @access_auth_middleware
    def get(self, account_id: str, task_id: str = None, comment_id: str = None) -> ResponseReturnValue:
        """Get a single comment or all comments for a task"""
        if comment_id:
            # Get single comment
            comment_params = GetCommentParams(account_id=account_id, comment_id=comment_id)
            comment = CommentService.get_comment(params=comment_params)
            comment_dict = asdict(comment)
            comment_dict["created_at"] = comment.created_at.isoformat()
            comment_dict["updated_at"] = comment.updated_at.isoformat()
            return jsonify(comment_dict), 200
        elif task_id:
            # Get all comments for a task
            comments_params = GetCommentsForTaskParams(account_id=account_id, task_id=task_id)
            comments = CommentService.get_comments_for_task(params=comments_params)
            comments_list = []
            for comment in comments:
                comment_dict = asdict(comment)
                comment_dict["created_at"] = comment.created_at.isoformat()
                comment_dict["updated_at"] = comment.updated_at.isoformat()
                comments_list.append(comment_dict)
            return jsonify(comments_list), 200
        else:
            raise CommentBadRequestError("Either task_id or comment_id must be provided")

    @access_auth_middleware
    def patch(self, account_id: str, comment_id: str) -> ResponseReturnValue:
        """Update a comment"""
        request_data = request.get_json()

        if request_data is None:
            raise CommentBadRequestError("Request body is required")

        if not request_data.get("content"):
            raise CommentBadRequestError("Content is required")

        update_comment_params = UpdateCommentParams(
            account_id=account_id, comment_id=comment_id, content=request_data["content"]
        )

        updated_comment = CommentService.update_comment(params=update_comment_params)
        comment_dict = asdict(updated_comment)
        comment_dict["created_at"] = updated_comment.created_at.isoformat()
        comment_dict["updated_at"] = updated_comment.updated_at.isoformat()

        return jsonify(comment_dict), 200

    @access_auth_middleware
    def delete(self, account_id: str, comment_id: str) -> ResponseReturnValue:
        """Delete a comment (soft delete)"""
        delete_params = DeleteCommentParams(account_id=account_id, comment_id=comment_id)

        CommentService.delete_comment(params=delete_params)

        return "", 204
