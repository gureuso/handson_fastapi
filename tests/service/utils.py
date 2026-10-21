from unittest.mock import AsyncMock


def mock_repositories(service):
    # service가 __init__에서 만든 repository를 모두 AsyncMock으로 교체
    for name in list(vars(service)):
        if name.endswith('_repository'):
            setattr(service, name, AsyncMock())
    return service


def like_state(cnt: int, liked: bool) -> dict:
    return {'cnt': cnt, 'liked': liked}


def dislike_state(cnt: int, disliked: bool) -> dict:
    return {'cnt': cnt, 'disliked': disliked}
