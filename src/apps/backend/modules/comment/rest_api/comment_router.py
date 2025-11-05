from flask import Blueprint

from modules.comment.rest_api.comment_view import CommentView


class CommentRouter:
    @staticmethod
    def create_route(*, blueprint: Blueprint) -> Blueprint:
        # POST /api/accounts/{account_id}/tasks/{task_id}/comments - Create a new comment
        # GET /api/accounts/{account_id}/tasks/{task_id}/comments - Get all comments for a task
        blueprint.add_url_rule(
            "/accounts/<account_id>/tasks/<task_id>/comments",
            view_func=CommentView.as_view("comment_view"),
            methods=["POST", "GET"],
        )

        # GET /api/accounts/{account_id}/comments/{comment_id} - Get a single comment
        # PATCH /api/accounts/{account_id}/comments/{comment_id} - Update a comment
        # DELETE /api/accounts/{account_id}/comments/{comment_id} - Delete a comment
        blueprint.add_url_rule(
            "/accounts/<account_id>/comments/<comment_id>",
            view_func=CommentView.as_view("comment_view_by_id"),
            methods=["GET", "PATCH", "DELETE"],
        )

        return blueprint
