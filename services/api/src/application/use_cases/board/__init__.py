"""Board use cases."""

from src.application.use_cases.board.create_board import CreateBoardUseCase
from src.application.use_cases.board.create_board_list import CreateBoardListUseCase
from src.application.use_cases.board.create_group_board import CreateGroupBoardUseCase
from src.application.use_cases.board.delete_board import DeleteBoardUseCase
from src.application.use_cases.board.delete_board_list import DeleteBoardListUseCase
from src.application.use_cases.board.duplicate_board import DuplicateBoardUseCase
from src.application.use_cases.board.get_board import GetBoardUseCase
from src.application.use_cases.board.get_board_issues import GetBoardIssuesUseCase
from src.application.use_cases.board.list_board_lists import ListBoardListsUseCase
from src.application.use_cases.board.list_project_boards import ListProjectBoardsUseCase
from src.application.use_cases.board.move_board_issue import MoveBoardIssueUseCase
from src.application.use_cases.board.reorder_boards import ReorderBoardsUseCase
from src.application.use_cases.board.set_default_board import SetDefaultBoardUseCase
from src.application.use_cases.board.set_group_board_projects import SetGroupBoardProjectsUseCase
from src.application.use_cases.board.update_board import UpdateBoardUseCase
from src.application.use_cases.board.update_board_list import UpdateBoardListUseCase
from src.application.use_cases.board.update_board_scope import UpdateBoardScopeUseCase
from src.application.use_cases.board.update_board_swimlanes import UpdateBoardSwimlanesUseCase

__all__ = [
    "CreateBoardUseCase",
    "CreateBoardListUseCase",
    "CreateGroupBoardUseCase",
    "DeleteBoardUseCase",
    "DeleteBoardListUseCase",
    "DuplicateBoardUseCase",
    "GetBoardUseCase",
    "GetBoardIssuesUseCase",
    "ListBoardListsUseCase",
    "ListProjectBoardsUseCase",
    "MoveBoardIssueUseCase",
    "ReorderBoardsUseCase",
    "SetDefaultBoardUseCase",
    "SetGroupBoardProjectsUseCase",
    "UpdateBoardScopeUseCase",
    "UpdateBoardSwimlanesUseCase",
    "UpdateBoardUseCase",
    "UpdateBoardListUseCase",
]
