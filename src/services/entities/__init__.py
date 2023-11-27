from typing import Union

from .user_entity import (
    UserDTO,
    UserEmailDTO,
    UserRequestDTO,
    UserResponseDTO,
    UserUsernameDTO,
    UserPasswordDTO,
    UserUpdatePassword,
    UserEmailPasswordDTO,
    UserUsernamePasswordDTO,
)
from .user_history_entity import (
    UserHistory,
    UserHistoryDTO
)
from .broker_entity import (
    BrokerUserReg,
    BrokerUserEmailUpdate
)
from .auth_entity import (
    JWTToken,
    JWTRefreshToken,
    JWTTypeToken,
    JWTPayload
)


# Types
LoginType = Union[UserUsernamePasswordDTO, UserEmailPasswordDTO]
UserUpdateType = Union[UserEmailPasswordDTO, UserUsernamePasswordDTO, UserUpdatePassword]


__all__ = [
    'UserDTO',
    'UserEmailDTO',
    'UserUsernameDTO',
    'UserHistory',
    'UserHistoryDTO',
    'UserRequestDTO',
    'UserResponseDTO',
    'UserPasswordDTO',
    'UserUpdatePassword',
    'UserEmailPasswordDTO',
    'UserUsernamePasswordDTO',
    'BrokerUserReg',
    'BrokerUserEmailUpdate',
    'JWTToken',
    'JWTRefreshToken',
    'JWTTypeToken',
    'JWTPayload',

    'LoginType',
    'UserUpdateType'
]
