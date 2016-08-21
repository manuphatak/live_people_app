# coding=utf-8
from functools import partial, wraps


def join(*classes):
    all_classes = []

    for css_class in classes:
        if not css_class:
            continue
        if hasattr(css_class, 'split'):
            css_class = css_class.split()
        all_classes += (css_class or [])

    return ' '.join(all_classes)


def include(func, classes):
    @wraps(func)
    def wrapper(extra_classes=None, extra_extra_classes=None):
        return func(join(extra_classes, extra_extra_classes))

    return partial(wrapper, extra_extra_classes=classes)
