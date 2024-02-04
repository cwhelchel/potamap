import os
from json import JSONDecodeError
from dataclasses import dataclass
from marshmallow import Schema, fields, post_load

F_NAME = "config.json"


@dataclass
class Config:
    location: str
    init_x: float
    init_y: float
    display_opts: int
    show_actx_lbl: bool
    show_hunt_lbl: bool
    show_unkn_lbl: bool
    text_color: str


class ConfigSchema(Schema):
    location = fields.Str(load_default='US-GA')
    init_x = fields.Float(load_default=33.0406)
    init_y = fields.Float(load_default=-83.6431)
    display_opts = fields.Int(load_default=0)
    show_actx_lbl = fields.Bool(load_default=True)
    show_hunt_lbl = fields.Bool(load_default=False)
    show_unkn_lbl = fields.Bool(load_default=False)
    text_color = fields.Str(load_default='#6d6af7')

    @post_load
    def make_user(self, data, **kwargs):
        return Config(**data)


def get_config() -> Config:
    '''
    Read the config file into a Config object and return said object.

    Errors with or the absence of the serialized file will result in a Config
    object being returned with default values.
    '''

    if not os.path.exists(F_NAME):
        cfg_schema = ConfigSchema()
        default_cfg: Config = cfg_schema.load({})
        return default_cfg

    with open(F_NAME, 'r') as cfg_file:
        cfg_schema = ConfigSchema()
        s = cfg_file.read()
        try:
            x: Config = cfg_schema.loads(s)
        except JSONDecodeError:
            x: Config = cfg_schema.loads("{}")  # load_defaults
        return x


def save_config(cfg: Config):
    '''
    Serialize the given Config object and save to a file.

    :param cfg: the Config object to serialize to a file
    '''

    with open(F_NAME, 'w') as cfg_file:
        cfg_schema = ConfigSchema()
        s = cfg_schema.dumps(cfg, indent=4)
        cfg_file.write(s)
