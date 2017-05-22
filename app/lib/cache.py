from flask_cache import Cache


def build_cache_from_config(app):
    cfg = app.config
    cache_type = cfg.get('CACHE_TYPE')

    if cache_type is None:
        return None

    cache_config = {'CACHE_TYPE': cache_type}

    if cache_type == 'redis':
        cache_config.update({
            'CACHE_KEY_PREFIX': cfg['CACHE_KEY_PREFIX'],
            'CACHE_REDIS_HOST': cfg['CACHE_REDIS_HOST'],
            'CACHE_REDIS_PORT': cfg['CACHE_REDIS_PORT'],
            'CACHE_REDIS_URL': cfg['CACHE_REDIS_URL']
        })

    cache = Cache(config=cache_config)

    return cache
