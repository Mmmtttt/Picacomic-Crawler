from picacomic import *


pic_albums = '''
'''

pic_photos = '''
'''


def env(name, default, trim=('[]', '""', "''")):
    import os
    value = os.getenv(name, None)
    if value is None or value == '':
        return default

    for pair in trim:
        if value.startswith(pair[0]) and value.endswith(pair[1]):
            value = value[1:-1]

    return value


def get_id_set(env_name, given):
    aid_set = set()
    for text in [
        given,
        (env(env_name, '')).replace('-', '\n'),
    ]:
        aid_set.update(str_to_set(text))

    return aid_set


def main():
    album_id_set = get_id_set('PICA_ALBUM_IDS', pic_albums)
    photo_id_set = get_id_set('PICA_PHOTO_IDS', pic_photos)

    option = get_option()
    for album_id in album_id_set:
        download_album(album_id, option=option)

    option.call_all_plugin('after_download')


def get_option():
    option = create_option(os.path.abspath(os.path.join(__file__, '../../assets/option/option_example.yml')))
    cover_option_config(option)
    log_before_raise()
    return option


def cover_option_config(option: PicaOption):
    dir_rule = env('DIR_RULE', None)
    if dir_rule is not None:
        the_old = option.dir_rule
        the_new = PicaDirRule(dir_rule, base_dir=the_old.base_dir)
        option.dir_rule = the_new


if __name__ == '__main__':
    main()
