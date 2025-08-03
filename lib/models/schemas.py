from typing import List, Dict

from pydantic import BaseModel


#-------СОЗДАНИЕ ПАРАМЕТРОВ ИГРЫ-----------#
class GlobalParams(BaseModel):
    name: str
    profession: str
    talk_style: str
    traits: str
    look: str
    extra: str

class GoalParams(BaseModel):
    type: str
    object: str
    condition: str

class Params(BaseModel):
    npc: GlobalParams
    hero: GlobalParams
    world_settings: str
    NPC_to_hero_relation: str
    hero_to_NPC_relation: str
    mx_answers_cnt: int
    mn_answers_cnt: int
    mx_depth: int
    mn_depth: int
    scene: str
    genre: str
    epoch: str
    tonality: str
    extra: str
    context: str
    goals: List[GoalParams]
    game_id: str
    scene_id: str
    script_id: str

#-------ПЕРЕГЕНЕРАЦИЯ-----------#
class Graph:
    pass
#-------РЕГИСТРАЦИЯ И ВХОД-----------#
class UserRegisterRequest(BaseModel):
    mail: str
    name: str
    surname: str
    password: str

class UserLoginRequest(BaseModel):
    mail: str
    password: str

class UserResponse(BaseModel):
    id: int
    mail: str
    name: str
    surname: str


#-------РУЧКИ ДЛЯ БД-----------#
class UserUpdateName(BaseModel):
    name: str
    surname: str

class UserUpdatePassword(BaseModel):
    password_hash: str
